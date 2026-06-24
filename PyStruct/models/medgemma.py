from openai import OpenAI
import os
from dotenv import load_dotenv
from PIL import Image
import base64
from io import BytesIO
import re
import json

load_dotenv()

# constants
MODEL_URI = os.environ["MODEL_URI"]
HF_ACCESS_TOKEN = os.environ["HF_ACCESS_TOKEN"]
HF_API_URL = os.environ["HF_API_URL"]

class MedGemma:
    def __init__(self):
        self.client = OpenAI(
            base_url=HF_API_URL,
            api_key=HF_ACCESS_TOKEN
        )
    
    def build_message(self, image_path: str, prompt: str):

        def pil_to_base64(image: Image.Image):
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        image = Image.open(image_path).convert("RGB")
        image_b64 = pil_to_base64(image)
        
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]

    def generate(self, image_path: str, prompt: str, max_tokens: int = 512):
        def parse_json_response(response: str) -> dict:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in response")
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON: {e}")
            
        chat_completion = self.client.chat.completions.create(
            model=MODEL_URI,
            messages=self.build_message(image_path, prompt),
            stream=False,
            max_tokens=max_tokens
        )
        content = chat_completion.choices[0].message.content
        return parse_json_response(content)

if __name__ == "__main__":
    medgemma = MedGemma()
    image_path = "data/images/CXR_024_uncertain.png"
    prompt = """
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

    Examples of warnings:
        - "This assessment is not a medical diagnosis."
        - "Image quality limits interpretation."
        - "Potential opacity detected; radiologist review is recommended."
        - "Findings should be correlated with clinical evaluation."
        - "No definitive conclusion can be made from this image alone."

    """

    response = medgemma.generate(image_path, prompt)
    print(response)
