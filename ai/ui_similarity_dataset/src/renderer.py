"""
Rendu HTML -> screenshot avec Playwright.

Le HTML peut contenir des classes du type :

    yolo-button
    yolo-image
    yolo-block-nav

Ces classes permettent de recalculer automatiquement les
bounding boxes après mutation.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

import config

from src.annotations import (
    Boite,
    convertir_en_yolo,
)


CSS_STABILISATION = """
*, *::before, *::after {
    animation: none !important;
    transition: none !important;
    caret-color: transparent !important;
    scroll-behavior: auto !important;
}

video, canvas {
    animation: none !important;
}
"""


def identifiant_classe(nom_classe: str) -> int:
    """Transforme le nom d'une classe UI en identifiant YOLO."""

    try:
        return config.NOMS_CLASSES.index(nom_classe)
    except ValueError:
        return 13


async def extraire_annotations(page):
    """
    Récupère les éléments annotés directement dans le DOM.
    """

    donnees = await page.evaluate(
        """
        () => {
            const resultat = [];

            const elements = Array.from(
                document.querySelectorAll("[class]")
            );

            for (const element of elements) {

                const classes = Array.from(
                    element.classList
                ).filter(
                    classe => classe.startsWith("yolo-")
                );

                if (!classes.length) {
                    continue;
                }

                const rect =
                    element.getBoundingClientRect();

                if (
                    rect.width <= 0 ||
                    rect.height <= 0
                ) {
                    continue;
                }

                for (const classe of classes) {
                    resultat.push({
                        nom: classe.slice(5),
                        x: rect.left + window.scrollX,
                        y: rect.top + window.scrollY,
                        largeur: rect.width,
                        hauteur: rect.height
                    });
                }
            }

            return {
                largeur: Math.max(
                    document.documentElement.scrollWidth,
                    document.body
                        ? document.body.scrollWidth
                        : 0
                ),

                hauteur: Math.max(
                    document.documentElement.scrollHeight,
                    document.body
                        ? document.body.scrollHeight
                        : 0
                ),

                elements: resultat
            };
        }
        """
    )

    largeur_page = max(
        float(donnees["largeur"]),
        1.0,
    )

    hauteur_page = max(
        float(donnees["hauteur"]),
        1.0,
    )

    boites = []

    for element in donnees["elements"]:
        nom = element["nom"]

        boites.append(
            Boite(
                identifiant_classe=identifiant_classe(
                    nom
                ),
                nom_classe=nom,
                x=element["x"] / largeur_page,
                y=element["y"] / hauteur_page,
                largeur=element["largeur"] / largeur_page,
                hauteur=element["hauteur"] / hauteur_page,
            )
        )

    return (
        boites,
        largeur_page,
        hauteur_page,
    )


async def rendre_html(
    html: str,
    chemin_capture: str | Path,
    chemin_annotations: str | Path,
):
    """Rend une page HTML et produit screenshot + annotations."""

    chemin_capture = Path(chemin_capture)
    chemin_annotations = Path(chemin_annotations)

    async with async_playwright() as playwright:

        navigateur = await playwright.chromium.launch(
            headless=True
        )

        contexte = await navigateur.new_context(
            viewport={
                "width": config.LARGEUR_VUE,
                "height": config.HAUTEUR_VUE,
            },
            device_scale_factor=1,
        )

        page = await contexte.new_page()

        page.set_default_timeout(
            config.DELAI_MAX_RENDER_MS
        )

        await page.set_content(
            html,
            wait_until="domcontentloaded",
            timeout=config.DELAI_MAX_RENDER_MS,
        )

        await page.add_style_tag(
            content=CSS_STABILISATION
        )

        try:
            await page.wait_for_load_state(
                "networkidle",
                timeout=5000,
            )
        except Exception:
            pass

        await page.evaluate(
            """
            () => {
                for (
                    const element
                    of document.querySelectorAll("*")
                ) {
                    if (element.tagName === "VIDEO") {
                        element.pause?.();
                        element.currentTime = 0;
                    }
                }

                window.scrollTo(0, 0);
            }
            """
        )

        (
            boites,
            largeur,
            hauteur,
        ) = await extraire_annotations(page)

        await page.screenshot(
            path=str(chemin_capture),
            full_page=True,
            animations="disabled",
            scale="css",
        )

        chemin_annotations.write_text(
            convertir_en_yolo(boites),
            encoding="utf-8",
        )

        chemin_meta = (
            chemin_annotations.with_suffix(".json")
        )

        chemin_meta.write_text(
            json.dumps(
                {
                    "largeur": largeur,
                    "hauteur": hauteur,
                    "nombre_boites": len(boites),
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        await contexte.close()
        await navigateur.close()


def rendre_sync(
    html: str,
    chemin_capture: str | Path,
    chemin_annotations: str | Path,
):
    """Version synchrone pratique pour les scripts Python."""

    asyncio.run(
        rendre_html(
            html,
            chemin_capture,
            chemin_annotations,
        )
    )
