from pathlib import Path
import pandas as pd
import pydicom
from PIL import Image
import numpy as np

# =========================
# Chemins du projet
# =========================

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "data" / "rsna_raw" / "stage_2_detailed_class_info.csv"
DICOM_DIR = BASE_DIR / "data" / "rsna_raw" / "stage_2_train_images"

OUT_IMG_DIR = BASE_DIR / "data" / "selected_30" / "images"
OUT_CSV_PATH = BASE_DIR / "data" / "selected_30" / "labels_30.csv"

print("CSV cherché ici :")
print(CSV_PATH)

print("\nDossier images cherché ici :")
print(DICOM_DIR)

# =========================
# Vérifications
# =========================

if not CSV_PATH.exists():
    raise FileNotFoundError(
        f"\nFichier CSV introuvable :\n{CSV_PATH}\n\n"
        "Vérifie que stage_2_detailed_class_info.csv est bien dans data/rsna_raw/"
    )

if not DICOM_DIR.exists():
    raise FileNotFoundError(
        f"\nDossier DICOM introuvable :\n{DICOM_DIR}\n\n"
        "Vérifie que stage_2_train_images est bien extrait dans data/rsna_raw/"
    )

OUT_IMG_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# Lecture du CSV RSNA
# =========================

df = pd.read_csv(CSV_PATH)

required_columns = ["patientId", "class"]

for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Colonne manquante dans le CSV : {col}")

# Éviter les doublons
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

print("\nClasses disponibles dans le CSV RSNA :")
print(df["class"].value_counts())

# =========================
# Sélection 10 images par classe
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

    pil_img = Image.fromarray(img)

    filename = f"CXR_{index:03d}_{label}.png"
    output_path = OUT_IMG_DIR / filename

    pil_img.save(output_path)

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
# Création du CSV final
# =========================

labels_df = pd.DataFrame(rows)

if len(labels_df) != 30:
    raise ValueError(f"Seulement {len(labels_df)} images générées au lieu de 30.")

labels_df.to_csv(OUT_CSV_PATH, index=False, encoding="utf-8")

print("\nSélection terminée avec succès.")
print(f"Images sauvegardées dans : {OUT_IMG_DIR}")
print(f"CSV sauvegardé dans : {OUT_CSV_PATH}")

print("\nRépartition finale :")
print(labels_df["true_label"].value_counts())
