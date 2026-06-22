from pathlib import Path
import pandas as pd
from PIL import Image

# Chemin réel du fichier CSV
CSV_PATH = Path(r".\labels_30.csv")

# Chemin réel du dossier images
IMG_DIR = Path(r"..\images")

EXPECTED_COLUMNS = {
    "image_id",
    "filename",
    "true_label",
    "image_quality",
    "source",
    "original_label",
    "comment"
}

EXPECTED_LABELS = {
    "normal",
    "suspected_opacity",
    "uncertain"
}

EXPECTED_COUNT_TOTAL = 30

EXPECTED_COUNT_PER_CLASS = {
    "normal": 10,
    "suspected_opacity": 10,
    "uncertain": 10
}

print("Test du parser du dataset selected_30")
print("------------------------------------")

print("\nChemin du CSV utilisé :")
print(CSV_PATH)

print("\nChemin du dossier images utilisé :")
print(IMG_DIR)

# 1. Vérifier que le CSV existe

if not CSV_PATH.exists():
    raise FileNotFoundError(f"Fichier CSV introuvable : {CSV_PATH}")

print("\nCSV trouvé : OK")
# 2. Vérifier que le dossier images existe


if not IMG_DIR.exists():
    raise FileNotFoundError(f"Dossier images introuvable : {IMG_DIR}")

print("Dossier images trouvé : OK")

# 3. Lire le CSV

df = pd.read_csv(CSV_PATH)

print("Lecture du CSV : OK")
print(f"Nombre de lignes dans le CSV : {len(df)}")

# 4. Vérifier les colonnes obligatoires

missing_columns = EXPECTED_COLUMNS - set(df.columns)

if missing_columns:
    raise ValueError(
        f"\nColonnes manquantes dans le CSV : {missing_columns}\n"
        f"Colonnes trouvées : {list(df.columns)}"
    )

print("Colonnes obligatoires : OK")

# 5. Vérifier le nombre de lignes

if len(df) != EXPECTED_COUNT_TOTAL:
    raise ValueError(
        f"\nNombre de lignes incorrect.\n"
        f"Attendu : {EXPECTED_COUNT_TOTAL}\n"
        f"Trouvé : {len(df)}"
    )

print("Nombre de lignes : OK")

# 6. Vérifier les valeurs obligatoires

important_columns = ["image_id", "filename", "true_label"]

for col in important_columns:
    if df[col].isna().any():
        raise ValueError(f"La colonne {col} contient des valeurs manquantes.")

print("Valeurs obligatoires non vides : OK")


# 7. Vérifier les classes

labels_found = set(df["true_label"].unique())

if labels_found != EXPECTED_LABELS:
    raise ValueError(
        f"\nClasses incorrectes.\n"
        f"Classes attendues : {EXPECTED_LABELS}\n"
        f"Classes trouvées : {labels_found}"
    )

print("Noms des classes : OK")

# 8. Vérifier la répartition des classes

counts = df["true_label"].value_counts().to_dict()

for label, expected_count in EXPECTED_COUNT_PER_CLASS.items():
    found_count = counts.get(label, 0)

    if found_count != expected_count:
        raise ValueError(
            f"\nRépartition incorrecte pour la classe {label}.\n"
            f"Attendu : {expected_count}\n"
            f"Trouvé : {found_count}"
        )

print("Répartition des classes : OK")
print(counts)


# 9. Vérifier les doublons

if df["image_id"].duplicated().any():
    raise ValueError("Il y a des doublons dans image_id.")

if df["filename"].duplicated().any():
    raise ValueError("Il y a des doublons dans filename.")

print("Doublons : OK")
# 10. Vérifier les extensions

allowed_extensions = {".png", ".jpg", ".jpeg"}

for filename in df["filename"]:
    suffix = Path(filename).suffix.lower()

    if suffix not in allowed_extensions:
        raise ValueError(
            f"\nExtension non acceptée : {filename}\n"
            f"Extensions acceptées : {allowed_extensions}"
        )

print("Extensions des images : OK")

# 11. Vérifier que chaque image existe et peut être ouverte

errors = []

for _, row in df.iterrows():
    filename = row["filename"]
    img_path = IMG_DIR / filename

    if not img_path.exists():
        errors.append(f"Image manquante : {filename}")
        continue

    try:
        with Image.open(img_path) as img:
            img.verify()
    except Exception as e:
        errors.append(f"Image illisible : {filename} | erreur : {e}")

if errors:
    print("\nErreurs trouvées :")
    for error in errors:
        print("-", error)

    raise ValueError("\nLe test du parser a échoué.")

print("Toutes les images existent et sont lisibles : OK")

# RÉSULTAT FINAL

print("\n------------------------------------")
print("TEST TERMINÉ AVEC SUCCÈS")
print("------------------------------------")
print("Le parser fonctionne correctement.")
print("Le fichier labels_30.csv est valide.")
print("Les 30 images sont présentes et lisibles.")
print("Répartition finale :")
print("10 normal")
print("10 suspected_opacity")
print("10 uncertain")
