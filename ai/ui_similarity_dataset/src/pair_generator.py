"""
Génération des paires et calcul des pseudo-labels.
"""

from pathlib import Path
import hashlib
import json

import config

from src.annotations import (
    charger_annotations,
    histogramme_classes,
)

from src.structural_similarity import (
    calculer_similarite_structurelle,
)

from src.visual_similarity import (
    calculer_similarite_visuelle,
)


def obtenir_split(identifiant_source: str) -> str:
    """
    Affecte une page à train/validation/test.

    Important :
    toutes les variantes d'une même page restent dans
    le même ensemble afin d'éviter les fuites de données.
    """

    valeur = int(
        hashlib.sha256(
            identifiant_source.encode()
        ).hexdigest()[:8],
        16,
    ) / 0xFFFFFFFF

    if valeur < config.RATIOS_SPLIT["train"]:
        return "train"

    if (
        valeur
        < config.RATIOS_SPLIT["train"]
        + config.RATIOS_SPLIT["validation"]
    ):
        return "validation"

    return "test"


def calculer_score_paire(
    image_a,
    annotations_a,
    image_b,
    annotations_b,
):

    boites_a = charger_annotations(
        annotations_a
    )

    boites_b = charger_annotations(
        annotations_b
    )

    structure = (
        calculer_similarite_structurelle(
            boites_a,
            boites_b,
        )
    )

    visuel = (
        calculer_similarite_visuelle(
            image_a,
            image_b,
        )
    )

    style = (
        0.50
        * visuel["similarite_couleur"]
        + 0.50
        * visuel["ssim"]
    )

    score_final = (
        config.POIDS_LAYOUT
        * structure["similarite_layout"]
        + config.POIDS_COMPOSANTS
        * structure["similarite_composants"]
        + config.POIDS_VISUEL
        * visuel["similarite_visuelle"]
        + config.POIDS_STYLE
        * style
    )

    return {
        **structure,
        **visuel,
        "similarite_style": style,
        "similarite": max(
            0.0,
            min(1.0, score_final),
        ),
    }


def ajouter_jsonl(
    chemin: Path,
    donnees: dict,
):
    """Ajoute un exemple dans un fichier JSONL."""

    with chemin.open(
        "a",
        encoding="utf-8",
    ) as fichier:

        fichier.write(
            json.dumps(
                donnees,
                ensure_ascii=False,
            )
            + "\n"
        )


def generer_paires_meme_page(
    identifiant_source: str,
    variantes: list[dict],
):

    image_originale = (
        config.DOSSIER_CAPTURES
        / f"{identifiant_source}.png"
    )

    annotations_originales = (
        config.DOSSIER_ANNOTATIONS
        / f"{identifiant_source}.txt"
    )

    if not image_originale.exists():
        return 0

    split = obtenir_split(
        identifiant_source
    )

    nombre = 0

    for variante in variantes:

        image_variante = Path(
            variante["capture"]
        )

        annotations_variante = Path(
            variante["annotations"]
        )

        if (
            not image_variante.exists()
            or not annotations_variante.exists()
        ):
            continue

        metriques = calculer_score_paire(
            image_originale,
            annotations_originales,
            image_variante,
            annotations_variante,
        )

        score = metriques["similarite"]

        if score >= 0.90:
            difficulte = "facile"
        elif score >= 0.65:
            difficulte = "moyenne"
        else:
            difficulte = "difficile"

        donnees = {
            "pair_id": (
                f"{identifiant_source}"
                f"__{variante['variant_id']}"
            ),

            "source_id_a": identifiant_source,
            "source_id_b": identifiant_source,

            "image_a": str(
                image_originale.relative_to(
                    config.RACINE
                )
            ),

            "image_b": str(
                image_variante.relative_to(
                    config.RACINE
                )
            ),

            "labels_a": str(
                annotations_originales.relative_to(
                    config.RACINE
                )
            ),

            "labels_b": str(
                annotations_variante.relative_to(
                    config.RACINE
                )
            ),

            "type_paire": "meme_page_variante",
            "difficulte": difficulte,
            "niveau_mutation": variante["niveau"],
            "operations": variante["operations"],

            **metriques,
        }

        chemin_sortie = (
            config.DOSSIER_SORTIE
            / f"{split}.jsonl"
        )

        ajouter_jsonl(
            chemin_sortie,
            donnees,
        )

        nombre += 1

    return nombre


def generer_hard_negatives(
    toutes_les_sources: list[str],
    par_source: int = 1,
):
    """
    Génère des paires provenant de pages différentes mais
    ayant une structure UI relativement proche.

    Ces paires sont essentielles pour apprendre au modèle
    à distinguer deux interfaces différentes mais visuellement
    proches.
    """

    statistiques = {}

    for source in toutes_les_sources:

        chemin = (
            config.DOSSIER_ANNOTATIONS
            / f"{source}.txt"
        )

        statistiques[source] = (
            histogramme_classes(
                charger_annotations(chemin)
            )
        )

    def distance_histogrammes(a, b):

        classes = set(a) | set(b)

        if not classes:
            return 0.0

        return sum(
            abs(
                a.get(classe, 0)
                - b.get(classe, 0)
            )
            / max(
                a.get(classe, 0),
                b.get(classe, 0),
                1,
            )
            for classe in classes
        ) / len(classes)

    for source in toutes_les_sources:

        candidats = [
            autre
            for autre in toutes_les_sources
            if autre != source
        ]

        candidats.sort(
            key=lambda autre:
            distance_histogrammes(
                statistiques[source],
                statistiques[autre],
            )
        )

        for autre in candidats[:par_source]:

            image_a = (
                config.DOSSIER_CAPTURES
                / f"{source}.png"
            )

            image_b = (
                config.DOSSIER_CAPTURES
                / f"{autre}.png"
            )

            labels_a = (
                config.DOSSIER_ANNOTATIONS
                / f"{source}.txt"
            )

            labels_b = (
                config.DOSSIER_ANNOTATIONS
                / f"{autre}.txt"
            )

            if (
                not image_a.exists()
                or not image_b.exists()
            ):
                continue

            metriques = calculer_score_paire(
                image_a,
                labels_a,
                image_b,
                labels_b,
            )

            split = obtenir_split(source)

            donnees = {
                "pair_id": (
                    f"{source}"
                    f"__HARDNEG__"
                    f"{autre}"
                ),

                "source_id_a": source,
                "source_id_b": autre,

                "image_a": str(
                    image_a.relative_to(
                        config.RACINE
                    )
                ),

                "image_b": str(
                    image_b.relative_to(
                        config.RACINE
                    )
                ),

                "labels_a": str(
                    labels_a.relative_to(
                        config.RACINE
                    )
                ),

                "labels_b": str(
                    labels_b.relative_to(
                        config.RACINE
                    )
                ),

                "type_paire": "hard_negative",
                "difficulte": "difficile",
                "niveau_mutation": None,
                "operations": [],

                **metriques,
            }

            ajouter_jsonl(
                config.DOSSIER_SORTIE
                / f"{split}.jsonl",
                donnees,
            )
