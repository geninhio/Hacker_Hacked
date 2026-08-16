# UI Similarity Dataset

Pipeline Python complète permettant de transformer
AtomBlock-WebUI en dataset de paires d'interfaces web
avec un score de similarité.

## Structure

```text
ui-similarity-dataset/
│
├── config.py
├── requirements.txt
│
├── data/
│   ├── source/
│   ├── html/
│   ├── screenshots/
│   ├── variants/
│   ├── labels/
│   └── pairs/
│
├── src/
│   ├── download.py
│   ├── html_mutator.py
│   ├── renderer.py
│   ├── annotations.py
│   ├── visual_similarity.py
│   ├── structural_similarity.py
│   ├── pair_generator.py
│   └── build_dataset.py
│
└── output/
    ├── train.jsonl
    ├── validation.jsonl
    └── test.jsonl
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

playwright install chromium
```

## Première exécution

Il est fortement recommandé de commencer avec seulement
20 pages :

```bash
python ai/src/download.py --max-sources 20
```

Puis :

```bash
python ai/src/build_dataset.py \
    --variantes-par-niveau 2 \
    --hard-negatives 1
```

## Ce que fait la pipeline

### 1. Téléchargement

`download.py` utilise Hugging Face Datasets en streaming.

Il récupère notamment :

- HTML
- HTML avec images
- screenshot
- annotations YOLO

Les fichiers sont ensuite stockés localement.

### 2. Mutation

`html_mutator.py` crée plusieurs niveaux de variantes :

- niveau 1 : couleurs
- niveau 2 : typographie + espacement
- niveau 3 : bordures
- niveau 4 : structure + suppression d'un composant
- niveau 5 : modifications fortes

### 3. Rendu

`renderer.py` utilise Playwright pour :

1. charger le HTML ;
2. stabiliser les animations ;
3. attendre le rendu ;
4. capturer la page ;
5. récupérer les bounding boxes des éléments UI.

### 4. Similarité visuelle

`visual_similarity.py` calcule :

- SSIM
- similarité des couleurs
- similarité par embeddings optionnelle

Pour activer les embeddings :

```bash
export UI_SIM_USE_EMBEDDINGS=1
python src/build_dataset.py
```

### 5. Similarité structurelle

`structural_similarity.py` compare :

- nombre de boutons ;
- nombre d'images ;
- nombre de liens ;
- nombre d'inputs ;
- autres composants ;
- position ;
- taille ;
- chevauchement des bounding boxes.

### 6. Génération des paires

`pair_generator.py` produit deux grandes catégories :

#### Paires positives

```text
page originale
      ↕
variante de la même page
```

Par exemple :

```text
Original
   ↓
couleurs légèrement modifiées
   ↓
typographie modifiée
   ↓
espacement modifié
   ↓
structure modifiée
```

#### Hard negatives

```text
Page A
   ↕
Page B
```

avec deux pages différentes mais ayant des structures
UI relativement proches.

Ces exemples sont très importants pour éviter que le
modèle apprenne simplement :

> "plus les screenshots se ressemblent pixel par pixel,
> plus les interfaces sont similaires."

## Format d'un exemple

Chaque ligne JSONL contient notamment :

```json
{
  "pair_id": "...",
  "source_id_a": "...",
  "source_id_b": "...",
  "image_a": "...",
  "image_b": "...",
  "labels_a": "...",
  "labels_b": "...",
  "type_paire": "meme_page_variante",
  "difficulte": "moyenne",
  "niveau_mutation": 2,
  "similarite_composants": 0.91,
  "similarite_geometrie": 0.86,
  "similarite_layout": 0.88,
  "ssim": 0.81,
  "similarite_couleur": 0.94,
  "similarite_visuelle": 0.86,
  "similarite_style": 0.87,
  "similarite": 0.88
}
```

## Attention aux labels

Le champ `similarite` est un **pseudo-label**.

Il ne faut pas considérer automatiquement :

```text
0.88 = 88 % de similarité humaine
```

La bonne démarche est :

1. générer les paires ;
2. en sélectionner un échantillon ;
3. faire annoter ces paires par des humains ;
4. comparer les annotations humaines aux scores automatiques ;
5. ajuster les poids ;
6. seulement ensuite produire le dataset final ;
7. entraîner le modèle.

## Important : éviter la fuite de données

Le split est effectué au niveau de la page source.

Ainsi, si :

```text
page_001
page_001_variant_1
page_001_variant_2
page_001_variant_3
```

appartiennent à `train`, aucune de leurs variantes
ne doit se retrouver dans `test`.

C'est indispensable pour obtenir une véritable mesure
de généralisation.

## Utilisation future

Cette pipeline constitue principalement la phase de
construction du dataset.

Une fois le dataset validé, il pourra servir à entraîner
un modèle de comparaison d'images/UI, par exemple avec
une architecture Siamese ou une approche contrastive.

L'objectif final peut être :

```text
Screenshot A ──┐
               ├──> modèle ──> score [0,1]
Screenshot B ──┘
```

avec éventuellement une sortie :

```text
0.94 → très similaires
0.78 → similaires
0.51 → moyennement similaires
0.22 → différentes
0.05 → très différentes
```
