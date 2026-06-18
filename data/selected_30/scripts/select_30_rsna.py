
import os
import shutil
import pandas as pd
import pydicom
from PIL import Image
import numpy as np

# =========================
# Chemins
# =========================
BASE_DIR = os.getcwd()

CSV_PATH = os.path.join(BASE_DIR, "data", "rsna_raw", "stage_2_detailed_class_info.csv")
DICOM_DIR = os.path.join(BASE_DIR, "data", "rsna_raw", "stage_2_train_images")

OUT_IMG_DIR = os.path.join(BASE_DIR, "data", "selected_30", "images")
OUT_CSV_PATH = os.path.join(BASE_DIR, "data", "selected_30", "labels_30.csv")

os.makedirs(OUT_IMG_DIR, exist_ok=True)

# =========================
# Lecture du fichier de classes
# =========================
df = pd.read_csv(CSV_PATH)

# On garde un seul exemple par patientId pour éviter les doublons
df = df.drop_duplicates(subset=["patientId"])

# =========================
# Mapping des classes RSNA vers les classes du projet
# =========================
mapping = {
    "Normal": "normal",
    "Lung Opacity": "suspected_opacity",
    "No Lung Opacity / Not Normal": "uncertain"
}

df["project_label"] = df["class"].map(mapping)

# =========================
# Sélection équilibrée : 10 par classe
# =========================
selected_parts = []

for label in ["normal", "suspected_opacity", "uncertain"]:
    part = df[df["project_label"] == label].head(10)
    selected_parts.append(part)

selected = pd.concat(selected_parts).reset_index(drop=True)

# Vérification
if len(selected) != 30:
    raise ValueError("Erreur : impossible de sélectionner exactement 30 images.")

# =========================
# Conversion DICOM vers PNG + création du CSV
# =========================
rows = []

for i, row in selected.iterrows():
    index = i + 1
    patient_id = row["patientId"]
    label = row["project_label"]
    original_class = row["class"]

    dicom_path = os.path.join(DICOM_DIR, patient_id + ".dcm")

    if not os.path.exists(dicom_path):
        print(f"Image manquante : {dicom_path}")
        continue

    # Lire DICOM
    ds = pydicom.dcmread(dicom_path)
    img = ds.pixel_array.astype(float)

    # Normalisation 0-255
    img = img - np.min(img)
    img = img / np.max(img)
    img = (img * 255).astype(np.uint8)

    # Convertir en image PIL
    pil_img = Image.fromarray(img)

    # Nom propre
    filename = f"CXR_{index:03d}_{label}.png"
    output_path = os.path.join(OUT_IMG_DIR, filename)

    # Sauvegarde PNG
    pil_img.save(output_path)

    # Qualité simple
    if label == "uncertain":
        image_quality = "moyenne"
        comment = "Cas anormal ou hors cible choisi pour tester la prudence du modèle."
    elif label == "suspected_opacity":
        image_quality = "bonne"
        comment = "Cas avec suspicion d'opacité selon le label source RSNA."
    else:
        image_quality = "bonne"
        comment = "Cas normal selon le label source RSNA."

    rows.append({
        "image_id": f"CXR_{index:03d}",
        "filename": filename,
        "true_label": label,
        "image_quality": image_quality,
        "source": "RSNA Pneumonia Detection Challenge",
        "original_label": original_class,
        "patient_id_source": patient_id,
        "comment": comment
    })

# Création du CSV final
labels_df = pd.DataFrame(rows)
labels_df.to_csv(OUT_CSV_PATH, index=False, encoding="utf-8")

print("Sélection terminée.")
print(f"Images sauvegardées dans : {OUT_IMG_DIR}")
print(f"CSV sauvegardé dans : {OUT_CSV_PATH}")
print(labels_df["true_label"].value_counts())
