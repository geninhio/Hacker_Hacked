"""
Téléchargement / extraction d'un sous-ensemble d'AtomBlock-WebUI.

Le dataset est lu en mode streaming afin d'éviter de télécharger
l'intégralité du dataset sur la machine.
"""

from pathlib import Path
import argparse
import json

from datasets import load_dataset

import config


def sauvegarder_image(image, chemin: Path):
    """Sauvegarde une image PIL au format PNG."""
    if image is None:
        return

    image.save(chemin, format="PNG")


def main():
    parser = argparse.ArgumentParser(
        description="Extrait des pages depuis AtomBlock-WebUI."
    )

    parser.add_argument(
        "--max-sources",
        type=int,
        default=config.MAX_SOURCES,
        help="Nombre maximal de pages à récupérer.",
    )

    args = parser.parse_args()

    print(
        f"Chargement de {config.DATASET_HF} "
        f"en mode streaming..."
    )

    dataset = load_dataset(
        config.DATASET_HF,
        split=config.SOUS_ENSEMBLE_HF,
        streaming=True,
    )

    manifeste = []

    for index, ligne in enumerate(dataset):
        if index >= args.max_sources:
            break

        identifiant = ligne["file_name"]

        html = ligne.get("html") or ""
        html_avec_images = ligne.get("html_with_images") or ""

        if not html:
            print(
                f"[IGNORÉ] {identifiant}: HTML absent."
            )
            continue

        chemin_html = (
            config.DOSSIER_HTML / f"{identifiant}.html"
        )

        chemin_html.write_text(
            html,
            encoding="utf-8",
        )

        chemin_html_images = None

        if html_avec_images:
            chemin_html_images = (
                config.DOSSIER_HTML
                / f"{identifiant}.with_images.html"
            )

            chemin_html_images.write_text(
                html_avec_images,
                encoding="utf-8",
            )

        chemin_capture = (
            config.DOSSIER_CAPTURES
            / f"{identifiant}.png"
        )

        sauvegarder_image(
            ligne.get("screenshot"),
            chemin_capture,
        )

        annotations = ligne.get("labels") or ""

        chemin_annotations = (
            config.DOSSIER_ANNOTATIONS
            / f"{identifiant}.txt"
        )

        chemin_annotations.write_text(
            annotations,
            encoding="utf-8",
        )

        manifeste.append({
            "source_id": identifiant,
            "html": str(chemin_html),
            "html_avec_images": (
                str(chemin_html_images)
                if chemin_html_images
                else None
            ),
            "capture": str(chemin_capture),
            "annotations": str(chemin_annotations),
        })

        print(
            f"[{index + 1}] Page récupérée : {identifiant}"
        )

    chemin_manifeste = (
        config.DOSSIER_SOURCE / "manifest.json"
    )

    chemin_manifeste.write_text(
        json.dumps(
            manifeste,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"\n{len(manifeste)} pages sauvegardées."
    )


if __name__ == "__main__":
    main()
