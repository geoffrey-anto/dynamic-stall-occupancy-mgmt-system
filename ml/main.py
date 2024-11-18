import uuid
import requests
import numpy as np
from PIL import Image
from io import BytesIO
import json
from ultralytics import YOLO
from typing import List
from langchain_ollama.llms import OllamaLLM

PROMPT = {
    "MAIN": lambda p, s: f"Given the image of a {','.join([str(i) for i in p])} with the following bounding boxes {','.join([str(i) for i in s])}, what sensors would you recommend to be used for the project?"
}


def calculate_center_from_xyxy(bounding_box):
    x1, y1, x2, y2 = bounding_box
    return (x1 + x2) / 2, (y1 + y2) / 2


model = OllamaLLM(model="llama3.2:1b")


class Sensor:

    def __init__(self, sensor_id, sensor_type, sensor_name, sensor_use, sensor_range, sensor_cost, sensor_power, sensor_weight, sensor_size, sensor_accuracy):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.sensor_name = sensor_name
        self.sensor_use = sensor_use
        self.sensor_range = sensor_range
        self.sensor_cost = sensor_cost
        self.sensor_power = sensor_power
        self.sensor_weight = sensor_weight
        self.sensor_size = sensor_size
        self.sensor_accuracy = sensor_accuracy
    
    def __str__(self):
        return f"Sensor Name: {self.sensor_name}, Sensor Type: {self.sensor_type}, Sensor Use: {self.sensor_use}, Sensor Range: {self.sensor_range}, Sensor Cost: {self.sensor_cost}, Sensor Power: {self.sensor_power}, Sensor Weight: {self.sensor_weight}, Sensor Size: {self.sensor_size}, Sensor Accuracy: {self.sensor_accuracy}"


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
        
        yolo.train(data="./yolo/data/data.yaml", epochs=10, batch=16)
        
        # pred = yolo.predict(image_url)
        
        # print(pred)
        
        # boxes = json.loads(pred[0].to_json())

        # processed_image = ProcessedImage(img, boxes, width_scale, height_scale, project_id, image_url)
        
        # # Get List Of sensors from the backend to feed into the model
        # sensors_list: List[Sensor] = []
        
        # response = requests.get("http://localhost:5000/sensors")  # Todo: Change to a db call
        
        # sensors_data = response.json()
        
        # for sensor_data in sensors_data:
        #     sensor = Sensor(
        #         sensor_data["sensor_id"],
        #         sensor_data["sensor_type"],
        #         sensor_data["sensor_name"],
        #         sensor_data["sensor_use"],
        #         sensor_data["sensor_range"],
        #         sensor_data["sensor_cost"],
        #         sensor_data["sensor_power"],
        #         sensor_data["sensor_weight"],
        #         sensor_data["sensor_size"],
        #         sensor_data["sensor_accuracy"]
        #     )
        #     sensors_list.append(sensor)
        
        # # Run thru llm to get optimized plan for the project with the sensors required
        # model_response = model.predict(PROMPT["MAIN"](sensors_list, processed_image))
        
        # # Get the optimized plan from the model
        # sensors_information = model_response.split("<<>>")[0]
        # optimized_plan = model_response.split("<<>>")[1]
        
        # # Save the optimized plan to the database
        # save_to_database("optimized_plan", optimized_plan)
        
        # # Save the processed image to the database
        # save_to_database("processed_image", processed_image)
        
        # # Notify the frontend that the project is ready by updating the status of the project to ready in the database
        # update_project_status(project_id, "ready")


def main():
    # call process function from the api with the image urls and the scale
    process(["https://www.grundriss-schmiede.de/images/buerogrundriss/buerogrundriss.png"], 2, 2)
    return


if __name__ == "__main__":
    main()
