"""
Calcul de similarité structurelle entre deux interfaces.
"""

from collections import defaultdict

from src.annotations import (
    Boite,
    calculer_iou,
    histogramme_classes,
)


def similarite_composants(
    boites_a: list[Boite],
    boites_b: list[Boite],
) -> float:

    hist_a = histogramme_classes(boites_a)
    hist_b = histogramme_classes(boites_b)

    classes = set(hist_a) | set(hist_b)

    if not classes:
        return 1.0

    scores = []

    for classe in classes:

        nombre_a = hist_a.get(classe, 0)
        nombre_b = hist_b.get(classe, 0)

        maximum = max(
            nombre_a,
            nombre_b,
        )

        if maximum == 0:
            scores.append(1.0)
        else:
            scores.append(
                1.0
                - abs(nombre_a - nombre_b)
                / maximum
            )

    return max(
        0.0,
        sum(scores) / len(scores),
    )


def apparier_boites(
    boites_a,
    boites_b,
):
    """
    Associe les éléments de même classe en recherchant
    la meilleure correspondance géométrique.
    """

    groupes_a = defaultdict(list)
    groupes_b = defaultdict(list)

    for boite in boites_a:
        groupes_a[boite.nom_classe].append(
            boite
        )

    for boite in boites_b:
        groupes_b[boite.nom_classe].append(
            boite
        )

    paires = []

    for classe in set(groupes_a) | set(groupes_b):

        liste_a = groupes_a[classe]
        liste_b = groupes_b[classe]

        deja_utilisees = set()

        for boite_a in liste_a:

            meilleur_index = None
            meilleur_score = -1

            for index, boite_b in enumerate(
                liste_b
            ):

                if index in deja_utilisees:
                    continue

                iou = calculer_iou(
                    boite_a,
                    boite_b,
                )

                dx = (
                    boite_a.centre_x
                    - boite_b.centre_x
                )

                dy = (
                    boite_a.centre_y
                    - boite_b.centre_y
                )

                distance = (
                    dx * dx + dy * dy
                ) ** 0.5

                proximite = max(
                    0.0,
                    1.0 - distance / 1.4143,
                )

                score = (
                    0.75 * iou
                    + 0.25 * proximite
                )

                if score > meilleur_score:
                    meilleur_score = score
                    meilleur_index = index

            if meilleur_index is not None:

                deja_utilisees.add(
                    meilleur_index
                )

                paires.append(
                    (
                        boite_a,
                        liste_b[meilleur_index],
                        meilleur_score,
                    )
                )

    return paires


def similarite_geometrique(
    boites_a,
    boites_b,
) -> float:

    paires = apparier_boites(
        boites_a,
        boites_b,
    )

    denominateur = max(
        len(boites_a),
        len(boites_b),
        1,
    )

    score_apparie = sum(
        score
        for _, _, score in paires
    )

    penalite_non_apparies = (
        abs(
            len(boites_a)
            - len(boites_b)
        )
        / denominateur
    )

    score = (
        score_apparie / denominateur
        - 0.35 * penalite_non_apparies
    )

    return max(
        0.0,
        min(1.0, score),
    )


def calculer_similarite_structurelle(
    boites_a,
    boites_b,
) -> dict:

    composants = similarite_composants(
        boites_a,
        boites_b,
    )

    geometrie = similarite_geometrique(
        boites_a,
        boites_b,
    )

    layout = (
        0.45 * composants
        + 0.55 * geometrie
    )

    return {
        "similarite_composants": composants,
        "similarite_geometrie": geometrie,
        "similarite_layout": layout,
    }
