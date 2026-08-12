"""
Construction complète du dataset de paires.

Étapes :

1. Charger le manifeste AtomBlock.
2. Générer des variantes HTML.
3. Rendre les variantes avec Playwright.
4. Recalculer les annotations.
5. Calculer les similarités.
6. Générer les paires positives.
7. Générer les hard negatives.
8. Produire train/validation/test.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import config

from src.annotations import (
    charger_annotations,
)

from src.html_mutator import (
    muter,
)

from src.renderer import (
    rendre_sync,
)

from src.pair_generator import (
    generer_paires_meme_page,
    generer_hard_negatives,
)


def charger_manifeste():

    chemin = (
        config.DOSSIER_SOURCE
        / "manifest.json"
    )

    if not chemin.exists():
        raise FileNotFoundError(
            "Le manifeste est absent. "
            "Il faut d'abord lancer : "
            "python src/download.py"
        )

    return json.loads(
        chemin.read_text(
            encoding="utf-8"
        )
    )


def nettoyer_sorties():

    for nom in (
        "train.jsonl",
        "validation.jsonl",
        "test.jsonl",
    ):

        chemin = (
            config.DOSSIER_SORTIE / nom
        )

        if chemin.exists():
            chemin.unlink()


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Construit le dataset de "
            "similarité d'interfaces."
        )
    )

    parser.add_argument(
        "--variantes-par-niveau",
        type=int,
        default=config.VARIANTES_PAR_NIVEAU,
    )

    parser.add_argument(
        "--hard-negatives",
        type=int,
        default=1,
    )

    parser.add_argument(
        "--sans-hard-negatives",
        action="store_true",
    )

    args = parser.parse_args()

    nettoyer_sorties()

    manifeste = charger_manifeste()

    hasard = random.Random(
        config.GRAINE_ALEATOIRE
    )

    sources = [
        element["source_id"]
        for element in manifeste
    ]

    for index, element in enumerate(
        manifeste,
        start=1,
    ):

        source = element["source_id"]

        chemin_html = Path(
            element["html"]
        )

        if not chemin_html.exists():
            continue

        html = chemin_html.read_text(
            encoding="utf-8"
        )

        annotations_source = (
            charger_annotations(
                element["annotations"]
            )
        )

        classes_source = [
            boite.nom_classe
            for boite in annotations_source
        ]

        variantes = []

        # Cinq niveaux de mutation.
        for niveau in range(1, 6):

            for numero in range(
                args.variantes_par_niveau
            ):

                identifiant_variante = (
                    f"{source}"
                    f"__L{niveau}"
                    f"__V{numero}"
                )

                chemin_capture = (
                    config.DOSSIER_VARIANTES
                    / f"{identifiant_variante}.png"
                )

                chemin_annotations = (
                    config.DOSSIER_VARIANTES
                    / f"{identifiant_variante}.txt"
                )

                chemin_html_variante = (
                    config.DOSSIER_VARIANTES
                    / f"{identifiant_variante}.html"
                )

                chemin_meta = (
                    config.DOSSIER_VARIANTES
                    / f"{identifiant_variante}.json"
                )

                # Permet de reprendre une exécution interrompue.
                if (
                    chemin_capture.exists()
                    and chemin_annotations.exists()
                ):

                    if chemin_meta.exists():
                        meta = json.loads(
                            chemin_meta.read_text()
                        )
                    else:
                        meta = {
                            "niveau": niveau,
                            "operations": [],
                        }

                    variantes.append({
                        "variant_id":
                            identifiant_variante,

                        "capture":
                            str(chemin_capture),

                        "annotations":
                            str(chemin_annotations),

                        "niveau":
                            niveau,

                        **meta,
                    })

                    continue

                html_muté, meta = muter(
                    html,
                    niveau,
                    hasard,
                    classes_source,
                )

                chemin_html_variante.write_text(
                    html_muté,
                    encoding="utf-8",
                )

                try:

                    rendre_sync(
                        html_muté,
                        chemin_capture,
                        chemin_annotations,
                    )

                except Exception as erreur:

                    print(
                        f"[AVERTISSEMENT] "
                        f"Échec rendu "
                        f"{identifiant_variante}: "
                        f"{erreur}"
                    )

                    continue

                chemin_meta.write_text(
                    json.dumps(
                        meta,
                        indent=2,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

                variantes.append({
                    "variant_id":
                        identifiant_variante,

                    "capture":
                        str(chemin_capture),

                    "annotations":
                        str(chemin_annotations),

                    "niveau":
                        niveau,

                    **meta,
                })

        nombre = (
            generer_paires_meme_page(
                source,
                variantes,
            )
        )

        print(
            f"[{index}/{len(manifeste)}] "
            f"{source}: "
            f"{nombre} paires générées"
        )

    if (
        not args.sans_hard_negatives
        and len(sources) > 1
    ):

        print(
            "\nGénération des hard negatives..."
        )

        generer_hard_negatives(
            sources,
            par_source=args.hard_negatives,
        )

    print(
        "\nConstruction du dataset terminée."
    )

    print("\nNombre d'exemples :")

    for nom in (
        "train.jsonl",
        "validation.jsonl",
        "test.jsonl",
    ):

        chemin = (
            config.DOSSIER_SORTIE / nom
        )

        if chemin.exists():
            nombre = sum(
                1
                for _ in chemin.open(
                    encoding="utf-8"
                )
            )
        else:
            nombre = 0

        print(
            f"  {nom}: {nombre}"
        )


if __name__ == "__main__":
    main()
