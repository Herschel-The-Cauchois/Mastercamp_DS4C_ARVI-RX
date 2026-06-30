from pathlib import Path
import pandas as pd
import pydicom
from PIL import Image
import numpy as np

# =========================
# Chemin du dataset téléchargé
# =========================

RAW_DIR = Path(r"rsna-pneumonia-detection-challenge")

CSV_PATH = RAW_DIR / "stage_2_detailed_class_info.csv"
DICOM_DIR = RAW_DIR / "stage_2_train_images"

# =========================
# Chemin de sortie dans ton projet PyCharm
# =========================

PROJECT_DIR = Path(r"C:\Users\rania\PyCharmMiscProject")

OUT_IMG_DIR = PROJECT_DIR / "data" / "selected_30" / "images"
OUT_CSV_PATH = PROJECT_DIR / "data" / "selected_30" / "labels_30.csv"

print("CSV cherché ici :")
print(CSV_PATH)

print("\nDossier images cherché ici :")
print(DICOM_DIR)

print("\nLes 30 images seront créées ici :")
print(OUT_IMG_DIR)

# =========================
# Vérifications
# =========================

if not CSV_PATH.exists():
    raise FileNotFoundError(f"CSV introuvable : {CSV_PATH}")

if not DICOM_DIR.exists():
    raise FileNotFoundError(f"Dossier images introuvable : {DICOM_DIR}")

OUT_IMG_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# Lecture du fichier CSV
# =========================

df = pd.read_csv(CSV_PATH)

required_columns = ["patientId", "class"]

for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Colonne manquante dans le CSV : {col}")

# Supprimer les doublons
df = df.drop_duplicates(subset=["patientId"])

# =========================
# Mapping RSNA vers les classes du projet
# =========================

mapping = {
    "Normal": "normal",
    "Lung Opacity": "suspected_opacity",
    "No Lung Opacity / Not Normal": "uncertain"
}

df["project_label"] = df["class"].map(mapping)

print("\nClasses disponibles dans RSNA :")
print(df["class"].value_counts())

# =========================
# Sélectionner 10 images par classe
# =========================

selected_parts = []

for label in ["normal", "suspected_opacity", "uncertain"]:
    part = df[df["project_label"] == label].head(10)

    if len(part) < 10:
        raise ValueError(f"Pas assez d'images pour la classe : {label}")

    selected_parts.append(part)

selected = pd.concat(selected_parts).reset_index(drop=True)

print("\nSélection finale :")
print(selected["project_label"].value_counts())

# =========================
# Conversion DICOM vers PNG
# =========================

rows = []

for i, row in selected.iterrows():
    index = i + 1

    patient_id = row["patientId"]
    label = row["project_label"]
    original_label = row["class"]

    dicom_path = DICOM_DIR / f"{patient_id}.dcm"

    if not dicom_path.exists():
        print(f"Image manquante : {dicom_path}")
        continue

    ds = pydicom.dcmread(dicom_path)
    img = ds.pixel_array.astype(np.float32)

    img_min = np.min(img)
    img_max = np.max(img)

    if img_max == img_min:
        print(f"Image ignorée car vide : {patient_id}")
        continue

    img = (img - img_min) / (img_max - img_min)
    img = (img * 255).astype(np.uint8)

    image = Image.fromarray(img)

    filename = f"CXR_{index:03d}_{label}.png"
    output_path = OUT_IMG_DIR / filename
    image.save(output_path)

    if label == "normal":
        image_quality = "bonne"
        comment = "Cas normal selon le label source RSNA."
    elif label == "suspected_opacity":
        image_quality = "bonne"
        comment = "Cas avec suspicion d'opacité selon le label source RSNA."
    else:
        image_quality = "moyenne"
        comment = "Cas anormal ou hors cible choisi pour tester la prudence du modèle."

    rows.append({
        "image_id": f"CXR_{index:03d}",
        "filename": filename,
        "true_label": label,
        "image_quality": image_quality,
        "source": "RSNA Pneumonia Detection Challenge",
        "original_label": original_label,
        "comment": comment
    })

# =========================
# Création du fichier labels_30.csv
# =========================

labels_df = pd.DataFrame(rows)

if len(labels_df) != 30:
    raise ValueError(f"Seulement {len(labels_df)} images générées au lieu de 30.")

labels_df.to_csv(OUT_CSV_PATH, index=False, encoding="utf-8")

print("\n✅ Sélection terminée avec succès.")
print(f"Images créées dans : {OUT_IMG_DIR}")
print(f"CSV créé ici : {OUT_CSV_PATH}")

print("\nRépartition finale :")
print(labels_df["true_label"].value_counts())
