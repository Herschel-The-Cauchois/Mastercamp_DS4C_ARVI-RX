from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

CLASSES = ["normal", "suspected_opacity", "uncertain"]
VALID_LABELS = set(CLASSES)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
LABELS_PATH = PROJECT_ROOT / "data" / "labels.csv"
OUTPUT_DIR = PROJECT_ROOT / "models" / "outputs"
PREDICTIONS_PATH = OUTPUT_DIR / "predictions.csv"
METRICS_PATH = OUTPUT_DIR / "metrics.json"
CONFUSION_MATRIX_PATH = OUTPUT_DIR / "confusion_matrix.png"

PROMPT = """
You are an AI radiology screening assistant.

Your task is to analyze a chest radiology image and provide a preliminary screening assessment. This assessment is NOT a medical diagnosis and must only be based on visual evidence present in the image.

You must classify the image into exactly one of the following classes:

    - "normal": No visible pulmonary opacity or suspicious radiological finding is detected.
    - "suspected_opacity": One or more abnormal opacity regions are visually detected and may indicate a pathological finding.
    - "uncertain": The image quality, anatomical coverage, or visual evidence is insufficient to make a reliable assessment.

Instructions:

1. Base your analysis only on visible findings in the image.
2. Do not infer patient history, symptoms, laboratory results, or clinical context.
3. If the image is blurry, incomplete, overexposed, underexposed, rotated, or difficult to interpret, prefer the class "uncertain".
4. Describe only findings that are visually observable.
5. The confidence score must be a floating-point value between 0.0 and 1.0.
6. The warnings field is critical and must contain all important safety alerts related to the assessment.
7. Return ONLY valid JSON.
8. Do not include markdown, explanations, comments, or additional text outside the JSON object.

Output schema:

{
"predicted_class": "normal | suspected_opacity | uncertain",
"justification": "Brief explanation based on visible radiological findings.",
"visual_evidence": [
"List of observable visual findings supporting the decision."
],
"confidence": 0.0,
"warnings": [
"Important diagnostic limitations, uncertainty factors, or safety alerts."
]
}
"""


def check_evaluation_dependencies() -> None:
    try:
        import matplotlib.pyplot  # noqa: F401
        import sklearn.metrics  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "Install evaluation dependencies first: "
            "pip install -r models/requirements-evaluation.txt"
        ) from exc


def read_images(labels_path: Path = LABELS_PATH):
    with labels_path.open(newline="", encoding="utf-8") as labels_file:
        reader = csv.DictReader(labels_file)
        for row_number, row in enumerate(reader, start=2):
            image_path = row["image_path"].strip()
            label = row["label"].strip()

            if label not in VALID_LABELS:
                raise ValueError(
                    f"Invalid label '{label}' in {labels_path} at line {row_number}"
                )

            resolved_image_path = Path(image_path)
            if not resolved_image_path.is_absolute():
                resolved_image_path = PROJECT_ROOT / resolved_image_path

            if not resolved_image_path.exists():
                raise FileNotFoundError(
                    f"Image listed in {labels_path} does not exist: {image_path}"
                )

            yield str(resolved_image_path), label


def normalize_prediction(predicted_class: Any) -> str:
    prediction = str(predicted_class).strip()
    if prediction not in VALID_LABELS:
        return "invalid"
    return prediction


def create_medgemma():
    try:
        from .medgemma import MedGemma
    except ImportError:
        from medgemma import MedGemma

    return MedGemma()


def run_predictions(batch_size: int = 5) -> list[dict[str, Any]]:
    medgemma = create_medgemma()
    dataset = list(read_images())
    results = []

    for i in range(0, len(dataset), batch_size):
        batch = dataset[i : i + batch_size]
        image_paths = [image_path for image_path, _ in batch]
        response = medgemma.batch_mode(image_paths, PROMPT)

        if len(response) != len(batch):
            raise ValueError(
                f"Expected {len(batch)} predictions, got {len(response)}"
            )

        for (image_path, true_label), prediction_data in zip(batch, response):
            predicted_label = normalize_prediction(
                prediction_data.get("predicted_class")
            )
            results.append(
                {
                    "image_path": image_path,
                    "true_label": true_label,
                    "predicted_label": predicted_label,
                    "confidence": prediction_data.get("confidence", ""),
                    "correct": true_label == predicted_label,
                    "raw_response": json.dumps(
                        prediction_data, ensure_ascii=False
                    ),
                }
            )

    return results


def save_predictions(results: list[dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with PREDICTIONS_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "image_path",
                "true_label",
                "predicted_label",
                "confidence",
                "correct",
                "raw_response",
            ],
        )
        writer.writeheader()
        writer.writerows(results)


def build_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    from sklearn.metrics import (
        accuracy_score,
        balanced_accuracy_score,
        classification_report,
        confusion_matrix,
    )

    y_true = [row["true_label"] for row in results]
    y_pred = [row["predicted_label"] for row in results]
    labels = CLASSES + (["invalid"] if "invalid" in y_pred else [])

    report_dict = classification_report(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
        output_dict=True,
    )
    report_text = classification_report(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
    )

    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "labels": labels,
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "classification_report": report_dict,
        "classification_report_text": report_text,
        "confusion_matrix": matrix.tolist(),
    }


def save_metrics(metrics: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with METRICS_PATH.open("w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=2, ensure_ascii=False)


def save_confusion_matrix(metrics: dict[str, Any]) -> None:
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay

    labels = metrics["labels"]
    matrix = metrics["confusion_matrix"]

    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=labels,
    )
    fig, ax = plt.subplots(figsize=(8, 6))
    display.plot(ax=ax, cmap="Blues", colorbar=False, values_format="d")
    ax.set_title("Confusion matrix - MedGemma evaluation")
    fig.tight_layout()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(CONFUSION_MATRIX_PATH, dpi=160)
    plt.close(fig)


def test():
    check_evaluation_dependencies()
    results = run_predictions()
    save_predictions(results)

    metrics = build_metrics(results)
    save_metrics(metrics)
    save_confusion_matrix(metrics)

    print(f"Accuracy: {metrics['accuracy']:.2f}")
    print(f"Balanced accuracy: {metrics['balanced_accuracy']:.2f}")
    print(metrics["classification_report_text"])
    print(f"Predictions saved to: {PREDICTIONS_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")
    print(f"Confusion matrix saved to: {CONFUSION_MATRIX_PATH}")


if __name__ == "__main__":
    test()
