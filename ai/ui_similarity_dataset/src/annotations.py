"""
Lecture et manipulation des annotations YOLO d'AtomBlock-WebUI.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import config


@dataclass
class Boite:
    """Représente une bounding box UI normalisée."""

    identifiant_classe: int
    nom_classe: str

    x: float
    y: float
    largeur: float
    hauteur: float

    @property
    def centre_x(self):
        return self.x + self.largeur / 2

    @property
    def centre_y(self):
        return self.y + self.hauteur / 2


def lire_yolo(texte: str) -> list[Boite]:
    """
    Convertit un texte YOLO en liste de Boite.

    Format :
        classe centre_x centre_y largeur hauteur
    """

    boites = []

    for ligne in texte.splitlines():
        morceaux = ligne.strip().split()

        if len(morceaux) != 5:
            continue

        try:
            classe, cx, cy, largeur, hauteur = map(
                float,
                morceaux,
            )
        except ValueError:
            continue

        classe = int(classe)

        if 0 <= classe < len(config.NOMS_CLASSES):
            nom = config.NOMS_CLASSES[classe]
        else:
            nom = str(classe)

        boites.append(
            Boite(
                identifiant_classe=classe,
                nom_classe=nom,
                x=cx - largeur / 2,
                y=cy - hauteur / 2,
                largeur=largeur,
                hauteur=hauteur,
            )
        )

    return boites


def charger_annotations(chemin: str | Path) -> list[Boite]:
    """Charge un fichier YOLO."""
    chemin = Path(chemin)

    if not chemin.exists():
        return []

    return lire_yolo(
        chemin.read_text(encoding="utf-8")
    )


def histogramme_classes(
    boites: Iterable[Boite],
) -> dict[str, int]:
    """Compte les éléments de chaque classe."""
    histogramme = {}

    for boite in boites:
        histogramme[boite.nom_classe] = (
            histogramme.get(boite.nom_classe, 0) + 1
        )

    return histogramme


def calculer_iou(a: Boite, b: Boite) -> float:
    """Calcule l'Intersection over Union de deux boîtes."""

    ax2 = a.x + a.largeur
    ay2 = a.y + a.hauteur

    bx2 = b.x + b.largeur
    by2 = b.y + b.hauteur

    x1 = max(a.x, b.x)
    y1 = max(a.y, b.y)
    x2 = min(ax2, bx2)
    y2 = min(ay2, by2)

    largeur = max(0.0, x2 - x1)
    hauteur = max(0.0, y2 - y1)

    intersection = largeur * hauteur

    union = (
        a.largeur * a.hauteur
        + b.largeur * b.hauteur
        - intersection
    )

    if union <= 0:
        return 0.0

    return intersection / union


def convertir_en_yolo(
    boites: Iterable[Boite],
) -> str:
    """Convertit les boîtes vers le format YOLO."""

    lignes = []

    for boite in boites:
        centre_x = boite.x + boite.largeur / 2
        centre_y = boite.y + boite.hauteur / 2

        lignes.append(
            f"{boite.identifiant_classe} "
            f"{centre_x:.6f} "
            f"{centre_y:.6f} "
            f"{boite.largeur:.6f} "
            f"{boite.hauteur:.6f}"
        )

    if not lignes:
        return ""

    return "\n".join(lignes) + "\n"
