import uuid
import requests
import numpy as np
from PIL import Image
from io import BytesIO
import json
from ultralytics import YOLO
from typing import List
from langchain_ollama.llms import OllamaLLM


def calculate_center_from_xyxy(bounding_box):
    x1, y1, x2, y2 = bounding_box
    return (x1 + x2) / 2, (y1 + y2) / 2


model = OllamaLLM(model="llama3.2:1b")


class ProcessedImage:

    def __init__(self, image_as_numpy, bounding_boxes, width_scale, height_scale, project_id, image_url):
        self.image_as_numpy = image_as_numpy
        self.original_bounding_boxes = []
        
        for box in bounding_boxes:
            self.original_bounding_boxes.append({
                "class": box["class"],
                "bounding_box": [
                    box["box"]["x1"],
                    box["box"]["y1"],
                    box["box"]["x2"],
                    box["box"]["y2"]
                ],
                "center": calculate_center_from_xyxy([
                    box["box"]["x1"],
                    box["box"]["y1"],
                    box["box"]["x2"],
                    box["box"]["y2"]
                ])
            })

        self.scaled_bounding_boxes = []
        
        for box in bounding_boxes:
            scaled_box = {
                "class": box["class"],
                "bounding_box": [
                    box["box"]["x1"] * width_scale,
                    box["box"]["y1"] * height_scale,
                    box["box"]["x2"] * width_scale,
                    box["box"]["y2"] * height_scale
                ],
                "center": calculate_center_from_xyxy([
                    box["box"]["x1"] * width_scale,
                    box["box"]["y1"] * height_scale,
                    box["box"]["x2"] * width_scale,
                    box["box"]["y2"] * height_scale
                ])
            }
            self.scaled_bounding_boxes.append(scaled_box)
        
        self.project_id = project_id
        self.image_url = image_url
    
    def __str__(self):
        return json.dumps({
            "project_id": self.project_id,
            "image_url": self.image_url,
            "original_bounding_boxes": self.original_bounding_boxes,
            "scaled_bounding_boxes": self.scaled_bounding_boxes
        })


def process(image_urls: List[str], width_scale: int=1, height_scale: int=1):
    project_id = uuid.uuid4().hex
    print(f"Processing project {project_id}")
    
    for image_url in image_urls:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img = np.array(img)
        
        yolo = YOLO("yolo11n.pt")
        
        pred = yolo.predict(image_url)
        
        boxes = json.loads(pred[0].to_json())

        processed_image = ProcessedImage(img, boxes, width_scale, height_scale, project_id, image_url)
        
        # Get List Of sensors from the backend to feed into the model
        
        # Run thru llm to get optimized plan for the project with the sensors required
        
        # Get the optimized plan from the model
        
        # Save the optimized plan to the database
        
        # Save the processed image to the database
        
        # Notify the frontend that the project is ready by updating the status of the project to ready in the database


def main():
    process(["https://www.grundriss-schmiede.de/images/buerogrundriss/buerogrundriss.png"], 2, 2)
    return


if __name__ == "__main__":
    main()
