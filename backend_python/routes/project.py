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

RES = {
    "PLACEMENT": """[
  {"room_id": "8", "sensor_id": "RFID-FP-003", "room_type": "conference_room_slot", "position": "[90.15676500000001, 111.247275]" },
  {"room_id": "4", "sensor_id": "PIR-002", "room_type": "office_room_slot", "position": "[90.47964499999999, 529.10071]" },
  {"room_id": "5", "sensor_id": "PIR-002", "room_type": "office_room_slot", "position": "[91.924995, 110.45950500000001]" },
  {"room_id": "1", "sensor_id": "PIR-002", "room_type": "office_room_slot", "position": "[221.0551, 84.16551]" },
  {"room_id": "3", "sensor_id": "PIR-002", "room_type": "office_room_slot", "position": "[221.54434000000003, 550.92975]" },
  {"room_id": "7", "sensor_id": "PIR-002", "room_type": "conference_room_slot", "position": "[270.748625, 319.995855]" },
  {"room_id": "11", "sensor_id": "PIR-002", "room_type": "office_room_slot", "position": "[274.70694000000003, 320.134645]" },
  {"room_id": "0", "sensor_id": "PIR-002", "room_type": "office_room_slot", "position": "[349.24396, 84.401275]" },
  {"room_id": "2", "sensor_id": "PIR-002", "room_type": "office_room_slot", "position": "[349.59424, 551.15419]" },
  {"room_id": "10", "sensor_id": "PIR-002", "room_type": "office_room_slot", "position": "[504.75058, 169.015275]" },
  {"room_id": "14", "sensor_id": "PIR-002", "room_type": "conference_room_slot", "position": "[507.97918500000003, 528.870345]" },
  {"room_id": "6", "sensor_id": "PIR-002", "room_type": "rest_room_slot", "position": "[557.737425, 457.0719]" },
  {"room_id": "12", "sensor_id": "PIR-002", "room_type": "rest_room_slot", "position": "[561.196715, 359.57547]" },
  {"room_id": "9", "sensor_id": "PIR-002", "room_type": "office_room_slot", "position": "[616.6718149999999, 596.570615]" },
  {"room_id": "13", "sensor_id": "PIR-002", "room_type": "office_room_slot", "position": "[618.64374, 146.25842500000002]" }
]""",
    "REASON": """### Sensor Placement Explanation

The sensor placement has been optimized based on the room types and dimensions. Here's an explanation of each sensor placement:

*   **Room 8 (Conference Room Slot)**: Two ultrasonic sensors (PIR-002) have been placed in this room to measure distance accurately. The first US-001 is placed near the center of the room, while the second one is placed at a corner to capture the entire area.
*   **Room 4 and 1 (Office Rooms Slots)**: One PIR sensor (PIR-002) has been placed in each room to detect motion. Both sensors are positioned at different locations within the rooms to cover more area, while minimizing potential false positives.
*   **Room 3 (Office Room Slot)**: The second ultrasonic sensor (US-001) is placed in this room to complement the first US-001 in room 8 and provide a complete coverage of the conference area.

### Sensor Placement Rationale

The rationale behind this placement is:

1.  **Distance Measurement**: Two ultrasonic sensors are used in rooms where accurate distance measurement is crucial, such as conference rooms.
2.  **Motion Detection**: One PIR sensor is placed in each office room to detect motion and prevent false positives.

These placements ensure that the sensor coverage is comprehensive while minimizing potential issues like false readings or missed areas.""",
    "DESCRIPTION": """**Smart Office Sensor Placement**
=====================================

The goal of this project is to implement a comprehensive sensor placement system for an office space. The system aims to provide accurate distance measurement and motion detection capabilities in various rooms.

### Sensor Placement

The sensor placement is as follows:

*   **Ultrasonic Sensors (US-001)**:
    *   Room 8: placed in the center of the conference room to measure distance accurately.
    *   Room 5: placed near the entrance to detect motion from multiple directions.
    *   Room 11: placed on a corner to capture movement from different angles.
*   **PIR Sensors (PIR-002)**:
    *   Room 4: placed at eye level to detect vertical motion and prevent false positives.
    *   Room 1: placed near the entrance to detect motion from multiple directions.

### Rationale

The rationale behind this placement is:

*   Distance Measurement: Two ultrasonic sensors are used in rooms where accurate distance measurement is crucial, such as conference rooms. This ensures that there is no blind spot or area without coverage.
*   Motion Detection: One PIR sensor is placed in each office room to detect motion and prevent false positives.

These placements ensure that the sensor coverage is comprehensive while minimizing potential issues like false readings or missed areas.

### Next Steps

The next step would be to implement a system that can read the sensor data, process it, and then send the processed data back to the central server using cellular networks.""",
    
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
            # project_json = model.invoke(PROMPT["PLACEMENT"](processed_image, sensors_list))
            # print(project_json)
            # with open("project.json", "w") as buffer:
            #     buffer.write(project_json)
            project_json = RES["PLACEMENT"]
                        
            # project_sensor_instructions = model.invoke(PROMPT["REASON"](processed_image, sensors_list, project_json))
            # print(project_sensor_instructions)
            # with open("reason.md", "w") as buffer:
            #     buffer.write(project_sensor_instructions)
            project_sensor_instructions = RES["REASON"]
                        
            # project_description = model.invoke(PROMPT["DESCRIPTION"](processed_image, sensors_list, project_json, project_sensor_instructions))
            # with open("description.md", "w") as buffer:
            #     buffer.write(project_description)
            # print(project_description)
            project_description = RES["DESCRIPTION"]
            
        except Exception as e:
            print(e)
            return None
        
        return "demo", project_description, project_sensor_instructions, project_json


available_sensors = [
    "eebc2e0f-f9c0-4332-8ccc-06be7c463a1d",
    "888fbd2d-f2bd-494e-9217-69cd69cf84ca"
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
