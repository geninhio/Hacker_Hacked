"""
Générateur de variantes HTML.

L'objectif est de créer artificiellement des paires :

    page originale <-> page légèrement modifiée

afin d'obtenir plusieurs niveaux de similarité.
"""

from __future__ import annotations

import random

from bs4 import BeautifulSoup


def ajouter_css(html: str, css: str) -> str:
    """Ajoute une balise <style> au document."""

    soup = BeautifulSoup(html, "lxml")

    if soup.head is None:
        head = soup.new_tag("head")

        if soup.html:
            soup.html.insert(0, head)
        else:
            soup.insert(0, head)

    style = soup.new_tag("style")
    style.string = css

    soup.head.append(style)

    return str(soup)


def modifier_couleurs(
    html: str,
    intensite: float,
    hasard: random.Random,
) -> str:

    rotation_teinte = (
        hasard.uniform(-45, 45) * intensite
    )

    saturation = hasard.uniform(
        0.92,
        1.10,
    )

    css = f"""
    body {{
        filter:
            hue-rotate({rotation_teinte:.2f}deg)
            saturate({saturation:.3f});
    }}
    """

    return ajouter_css(html, css)


def modifier_espacement(
    html: str,
    intensite: float,
    hasard: random.Random,
) -> str:

    echelle = (
        1.0
        + hasard.uniform(-0.10, 0.14)
        * intensite
    )

    espacement = (
        hasard.uniform(-0.02, 0.03)
        * intensite
    )

    css = f"""
    body {{
        letter-spacing:
            {espacement:.4f}em !important;
    }}

    .yolo-block,
    .yolo-block-nav,
    .yolo-block-sidebar,
    .yolo-block-form,
    .yolo-block-table {{
        transform:
            scale({echelle:.4f});
        transform-origin:
            top left;
    }}
    """

    return ajouter_css(html, css)


def modifier_typographie(
    html: str,
    intensite: float,
    hasard: random.Random,
) -> str:

    taille = (
        1.0
        + hasard.uniform(-0.06, 0.08)
        * intensite
    )

    poids = hasard.choice(
        [400, 500, 600, 700]
    )

    css = f"""
    body {{
        font-size:
            {taille:.4f}em !important;
    }}

    button,
    input,
    select,
    textarea {{
        font-weight:
            {poids} !important;
    }}
    """

    return ajouter_css(html, css)


def modifier_bordures(
    html: str,
    intensite: float,
    hasard: random.Random,
) -> str:

    rayon = hasard.uniform(
        4,
        24,
    ) * intensite

    css = f"""
    button,
    input,
    select,
    textarea,
    .yolo-block {{
        border-radius:
            {rayon:.1f}px !important;
    }}
    """

    return ajouter_css(html, css)


def modifier_structure(html: str, hasard: random.Random) -> str:
    """Applique une modification structurelle prudente."""

    choix = hasard.choice(
        [
            "grille",
            "flex",
            "largeur",
        ]
    )

    if choix == "grille":
        css = """
        .yolo-block {
            grid-template-columns:
                repeat(2, minmax(0, 1fr))
                !important;
        }
        """

    elif choix == "flex":
        css = """
        .yolo-block {
            flex-direction:
                column !important;
        }
        """

    else:
        css = """
        .yolo-block {
            max-width:
                85% !important;
        }
        """

    return ajouter_css(html, css)


def masquer_composant(
    html: str,
    nom_classe: str,
) -> str:

    selecteur = f".yolo-{nom_classe}"

    css = f"""
    {selecteur} {{
        visibility:
            hidden !important;
    }}
    """

    return ajouter_css(html, css)


def muter(
    html: str,
    niveau: int,
    hasard: random.Random,
    classes_source=None,
) -> tuple[str, dict]:

    classes_source = classes_source or []

    informations = {
        "niveau": niveau,
        "operations": [],
    }

    resultat = html

    if niveau == 0:
        return resultat, informations

    # Niveau 1 : modification visuelle faible.
    if niveau >= 1:

        resultat = modifier_couleurs(
            resultat,
            0.35 if niveau == 1 else 0.70,
            hasard,
        )

        informations["operations"].append(
            "couleurs"
        )

    # Niveau 2 : typographie + espacements.
    if niveau >= 2:

        resultat = modifier_espacement(
            resultat,
            0.50 if niveau == 2 else 1.0,
            hasard,
        )

        resultat = modifier_typographie(
            resultat,
            0.50 if niveau == 2 else 1.0,
            hasard,
        )

        informations["operations"] += [
            "espacement",
            "typographie",
        ]

    # Niveau 3 : bordures.
    if niveau >= 3:

        resultat = modifier_bordures(
            resultat,
            0.70,
            hasard,
        )

        informations["operations"].append(
            "bordures"
        )

    # Niveau 4 : modification structurelle.
    if niveau >= 4:

        resultat = modifier_structure(
            resultat,
            hasard,
        )

        informations["operations"].append(
            "structure"
        )

        candidats = [
            classe
            for classe in classes_source
            if classe in {
                "button",
                "image",
                "link",
                "input",
                "select",
                "icon",
            }
        ]

        if candidats:
            cible = hasard.choice(candidats)

            resultat = masquer_composant(
                resultat,
                cible,
            )

            informations["operations"].append(
                f"masquer:{cible}"
            )

    # Niveau 5 : mutation importante.
    if niveau >= 5:

        resultat = modifier_couleurs(
            resultat,
            1.0,
            hasard,
        )

        resultat = modifier_espacement(
            resultat,
            1.0,
            hasard,
        )

        resultat = modifier_structure(
            resultat,
            hasard,
        )

        informations["operations"] += [
            "couleurs_fortes",
            "espacement_fort",
            "structure_forte",
        ]

    return resultat, informations
