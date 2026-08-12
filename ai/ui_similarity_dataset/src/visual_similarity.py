"""
Calcul de similarité visuelle entre deux screenshots.
"""

from functools import lru_cache

import numpy as np
from PIL import Image, ImageOps
from skimage.metrics import structural_similarity

import config


def charger_image(
    chemin,
    taille=(512, 512),
):
    """Charge et normalise une image."""

    image = Image.open(chemin).convert("RGB")

    image = ImageOps.fit(
        image,
        taille,
        method=Image.Resampling.LANCZOS,
    )

    return (
        np.asarray(image)
        .astype(np.float32)
        / 255.0
    )


def similarite_ssim(
    chemin_a,
    chemin_b,
) -> float:

    image_a = charger_image(chemin_a)
    image_b = charger_image(chemin_b)

    score = structural_similarity(
        image_a,
        image_b,
        channel_axis=2,
        data_range=1.0,
    )

    return float(
        np.clip(score, 0.0, 1.0)
    )


def similarite_couleur(
    chemin_a,
    chemin_b,
) -> float:

    image_a = charger_image(chemin_a)
    image_b = charger_image(chemin_b)

    distance = np.mean(
        np.abs(image_a - image_b)
    )

    return float(
        np.clip(
            1.0 - distance,
            0.0,
            1.0,
        )
    )


@lru_cache(maxsize=1)
def charger_modele_embeddings():

    if not config.UTILISER_EMBEDDINGS:
        return None

    import torch
    from transformers import (
        CLIPModel,
        CLIPProcessor,
    )

    processeur = CLIPProcessor.from_pretrained(
        config.MODELE_EMBEDDINGS
    )

    modele = CLIPModel.from_pretrained(
        config.MODELE_EMBEDDINGS
    )

    modele.eval()

    return processeur, modele


def similarite_embeddings(
    chemin_a,
    chemin_b,
) -> float:

    if not config.UTILISER_EMBEDDINGS:
        return similarite_ssim(
            chemin_a,
            chemin_b,
        )

    import torch

    processeur, modele = (
        charger_modele_embeddings()
    )

    images = [
        Image.open(chemin_a).convert("RGB"),
        Image.open(chemin_b).convert("RGB"),
    ]

    entrees = processeur(
        images=images,
        return_tensors="pt",
    )

    with torch.no_grad():

        caracteristiques = (
            modele.get_image_features(
                **entrees
            )
        )

        caracteristiques = (
            caracteristiques
            / caracteristiques.norm(
                dim=-1,
                keepdim=True,
            )
        )

        similarite = torch.sum(
            caracteristiques[0]
            * caracteristiques[1]
        ).item()

    # Transformation de [-1,1] vers [0,1].
    return float(
        np.clip(
            (similarite + 1.0) / 2.0,
            0.0,
            1.0,
        )
    )


def calculer_similarite_visuelle(
    chemin_a,
    chemin_b,
) -> dict:

    ssim = similarite_ssim(
        chemin_a,
        chemin_b,
    )

    couleur = similarite_couleur(
        chemin_a,
        chemin_b,
    )

    embeddings = similarite_embeddings(
        chemin_a,
        chemin_b,
    )

    score_visuel = (
        0.70 * embeddings
        + 0.30 * couleur
    )

    return {
        "ssim": ssim,
        "similarite_couleur": couleur,
        "similarite_embeddings": embeddings,
        "similarite_visuelle": score_visuel,
    }
