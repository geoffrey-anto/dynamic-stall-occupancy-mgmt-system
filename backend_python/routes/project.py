from fastapi import APIRouter, File, UploadFile
from db import SessionDep
from sqlmodel import select
from typing import Annotated
import os
from uuid import uuid4
import uuid
import requests
import numpy as np
from PIL import Image
from io import BytesIO
import json
from ultralytics import YOLO
from typing import List
from langchain_ollama.llms import OllamaLLM
from db import Occupancy, Projects
import base64

names = {}


def get_sensors(sensors):
    sensors_str = ""
    for sensor in sensors:
        sensors_str += f"""
            Sensor ID: {sensor.sensor_id}
            Sensor Name: {sensor.sensor_name}
            Sensor Type: {sensor.sensor_type}
            Sensor Use: {sensor.sensor_use}
            Sensor Range: {sensor.sensor_range}
            Sensor Cost: {sensor.sensor_cost}
            Sensor Power: {sensor.sensor_power}
            Sensor Weight: {sensor.sensor_weight}
            Sensor Size: {sensor.sensor_size}
            Sensor Accuracy: {sensor.sensor_accuracy}
        """
    return sensors_str


PROMPT = {
    "PLACEMENT": lambda p, s: f"""
You are professional in the field of IOT and Sensor Optimal Placement!
You have been given a project to optimize the placement of sensors when given the rooms layout and the sensors available.
The sensors are as follows:
{get_sensors(s)}

The project is to optimize the placement of sensors in the rooms layout given below:
{str(p)}

    Give The Optimal Placement of Sensors in the rooms layout. it should be in the format of json:
[
    JSON("room_id": "",
    "sensor_id": "","room_type": "","position": "")
]

Give a sensor for each room in the layout. Make sure to give the sensor that is most optimal for the room.

ONLY OUTPUT JUST THE VALID JSON, NO OTHER TEXT SHOULD BE PRESENT IN THE OUTPUT, NO MARKDOWN TOO JUST RAW JSON OUTPUT
""",

"REASON": lambda p, s, sp: f"""
You are professional in the field of IOT and Sensor Optimal Placement!
You are given the sensor placement with the rooms layout and the sensors available.
The sensors are as follows:
{get_sensors(s)}

The project is to optimize the placement of sensors in the rooms layout given below:
{str(p)}

The sensor placement is as follows:
{sp}

Give a reason for the placement of the sensors in the rooms layout. Make sure to give a reason for each sensor placement in the layout.

OUTPUT ONLY VALID MARKDOWN TEXT, NO JSON OR ANY OTHER TEXT SHOULD BE PRESENT IN THE OUTPUT
""",

"DESCRIPTION": lambda p, s, sp, r: f"""
You are professional in the field of IOT and Sensor Optimal Placement!
You are given the sensor placement with the rooms layout and the sensors available.
The sensors are as follows:
{get_sensors(s)}

The project is to optimize the placement of sensors in the rooms layout given below:
{str(p)}

The sensor placement is as follows:
{sp}

The reason for the placement of the sensors is as follows:
{r}

Give a description of the project with the sensor placement and the reason for the placement of the sensors in the rooms layout.

OUTPUT ONLY VALID MARKDOWN TEXT, NO JSON OR ANY OTHER TEXT SHOULD BE PRESENT IN THE OUTPUT
""",
}

project_router = APIRouter()


def calculate_center_from_xyxy(bounding_box):
    x1, y1, x2, y2 = bounding_box
    return (x1 + x2) / 2, (y1 + y2) / 2


model = OllamaLLM(model="llama3.2:latest")


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


def get_scaled_center_with_class(scaled_boundingg_boxes):
    res = """"""
    for box in scaled_boundingg_boxes:
        res += f"""
            id: {box["id"]}
            Class: {names[box["class"]]}
            Dimensions: {box["bounding_box"]}
            Center: {box["center"]}
        """
    return res   


class ProcessedImage:

    def __init__(self, image_as_numpy, bounding_boxes, width_scale, height_scale, project_id, image_url):
        self.image_as_numpy = image_as_numpy
        self.original_bounding_boxes = []
        
        for i, box in enumerate(bounding_boxes):
            self.original_bounding_boxes.append({
                "id": i,
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
        
        for i, box in enumerate(bounding_boxes):
            scaled_box = {
                "id": i,
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
            
        # sort both with respect to the center
        self.original_bounding_boxes = sorted(self.original_bounding_boxes, key=lambda x: x["center"])
        self.scaled_bounding_boxes = sorted(self.scaled_bounding_boxes, key=lambda x: x["center"])
        
        self.project_id = project_id
        self.image_url = image_url
    
    def __str__(self):
        return f"""
        Project ID: {self.project_id}
        Image URL: {self.image_url}
        Bounding Boxes For Rooms: {get_scaled_center_with_class(self.original_bounding_boxes)}
    """


def process(image_urls: List[str], width_scale: int=1, height_scale: int=1):
    project_id = uuid.uuid4().hex
    print(f"Processing project {project_id}")
    
    for image_url in image_urls:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img = np.array(img)
        
        yolo = YOLO("./routes/best.pt")
        
        # yolo.train(data="yolo11n.pt", epochs=10, batch=16)
        
        pred = yolo.predict(image_url)
        
        global names
        
        names = pred[0].names
        
        boxes = json.loads(pred[0].to_json())
        
        print(boxes)
        print(names)

        processed_image = ProcessedImage(img, boxes, width_scale, height_scale, project_id, image_url)
        
        # Get List Of sensors from the backend tself.scaled_bounding_boxeso feed into the model
        sensors_list: List[Sensor] = []
        
        response = requests.get("http://localhost:3003/api/v1/sensors")
        
        sensors_data = response.json()
        
        for sensor_data in sensors_data:
            sensor = Sensor(
                sensor_data["sensor_id"],
                sensor_data["sensor_type"],
                sensor_data["sensor_name"],
                sensor_data["sensor_use"],
                sensor_data["sensor_range"],
                sensor_data["sensor_cost"],
                sensor_data["sensor_power"],
                sensor_data["sensor_weight"],
                sensor_data["sensor_size"],
                sensor_data["sensor_accuracy"]
            )
            sensors_list.append(sensor)
            
        # # Run thru llm to get optimized plan for the project with the sensors required
        try:
            project_json = model.invoke(PROMPT["PLACEMENT"](processed_image, sensors_list))
            
            print(project_json)
            
            project_sensor_instructions = model.invoke(PROMPT["REASON"](processed_image, sensors_list, project_json))
            
            print(project_sensor_instructions)
            
            project_description = model.invoke(PROMPT["DESCRIPTION"](processed_image, sensors_list, project_json, project_sensor_instructions))
            
            print(project_description)
        except Exception as e:
            print(e)
            return None
        
        return "demo", project_description, project_sensor_instructions, project_json


available_sensors = [
    "f5958714-3a52-4688-a24d-cc7efde8d3e0",
    "eebc2e0f-f9c0-4332-8ccc-06be7c463a1d"
]


@project_router.post("/create")
def create_new_project(file: Annotated[bytes, File()], db: SessionDep):
    project_id = uuid4()
    # Get the image    
    os.makedirs("static", exist_ok=True)
    
    with open(f"static/{project_id}.png", "wb") as buffer:
        buffer.write(file)
    
    # Run ml pipeline to create a new project
    response = process([f"http://localhost:8000/static/{project_id}.png"], 1, 1)
    
    if response is None:
        return {"status": "error", "message": "Error in processing the image"}
    
    image_base64 = ""
    
    with open(f"static/{project_id}.png", "rb") as buffer:
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    
    # Save the project to the database
    project = Projects(name=project_id, description=response[1], instructions=response[2], project_name=response[0], sensor_configuration=response[3], image=image_base64)
    
    db.add(project)
    
    value = json.loads(response[3])
    
    for i in range(min(len(available_sensors), len(value))):
        db.add(Occupancy(id=available_sensors[i], occupancy="false", project=project_id, tag=str(value[i]["room_id"]) + "_" + value[i]["room_type"], name=value[i]["sensor_id"], position=value[i]["position"]))
    
    db.commit()
    
    os.remove(f"static/{project_id}.png")
    return {"status": "ok", "project_id": project_id}
