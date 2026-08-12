from pathlib import Path
import os

# ============================================================
# Configuration générale de la pipeline de similarité d'UI
# ============================================================

RACINE = Path(__file__).resolve().parent
DOSSIER_DONNEES = RACINE / "data"

DOSSIER_SOURCE = DOSSIER_DONNEES / "source"
DOSSIER_HTML = DOSSIER_DONNEES / "html"
DOSSIER_CAPTURES = DOSSIER_DONNEES / "screenshots"
DOSSIER_VARIANTES = DOSSIER_DONNEES / "variants"
DOSSIER_ANNOTATIONS = DOSSIER_DONNEES / "labels"
DOSSIER_PAIRS = DOSSIER_DONNEES / "pairs"
DOSSIER_SORTIE = RACINE / "output"

# Dataset Hugging Face utilisé comme source.
DATASET_HF = os.getenv(
    "UI_SIM_DATASET_HF",
    "Gallardot/AtomBlock-WebUI",
)
SOUS_ENSEMBLE_HF = os.getenv("UI_SIM_SPLIT", "train")

# Nombre de pages utilisées pour un premier prototype.
MAX_SOURCES = int(os.getenv("UI_SIM_MAX_SOURCES", "100"))

# Nombre de variantes générées pour chaque niveau de mutation.
VARIANTES_PAR_NIVEAU = int(
    os.getenv("UI_SIM_VARIANTS_PER_LEVEL", "2")
)

GRAINE_ALEATOIRE = int(
    os.getenv("UI_SIM_RANDOM_SEED", "42")
)

# Configuration Playwright.
LARGEUR_VUE = int(os.getenv("UI_SIM_VIEWPORT_WIDTH", "1280"))
HAUTEUR_VUE = int(os.getenv("UI_SIM_VIEWPORT_HEIGHT", "900"))
DELAI_MAX_RENDER_MS = int(
    os.getenv("UI_SIM_RENDER_TIMEOUT_MS", "30000")
)

# Modèle d'embeddings optionnel.
UTILISER_EMBEDDINGS = (
    os.getenv("UI_SIM_USE_EMBEDDINGS", "0") == "1"
)

MODELE_EMBEDDINGS = os.getenv(
    "UI_SIM_EMBEDDING_MODEL",
    "openai/clip-vit-base-patch32",
)

# Poids utilisés pour calculer le pseudo-label final.
# Ils devront être calibrés avec des annotations humaines.
POIDS_LAYOUT = 0.40
POIDS_COMPOSANTS = 0.20
POIDS_VISUEL = 0.30
POIDS_STYLE = 0.10

# Classes UI présentes dans les annotations AtomBlock.
NOMS_CLASSES = [
    "button",
    "link",
    "input",
    "image",
    "icon",
    "checkbox",
    "radio",
    "select",
    "block-nav",
    "block-sidebar",
    "block-footer",
    "block-form",
    "block-table",
    "block",
]

# Répartition des pages entre les ensembles.
RATIOS_SPLIT = {
    "train": 0.70,
    "validation": 0.15,
    "test": 0.15,
}

for dossier in (
    DOSSIER_SOURCE,
    DOSSIER_HTML,
    DOSSIER_CAPTURES,
    DOSSIER_VARIANTES,
    DOSSIER_ANNOTATIONS,
    DOSSIER_PAIRS,
    DOSSIER_SORTIE,
):
    dossier.mkdir(parents=True, exist_ok=True)
