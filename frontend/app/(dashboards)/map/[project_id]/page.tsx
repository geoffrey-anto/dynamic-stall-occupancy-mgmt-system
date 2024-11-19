"use client";
import Image from "next/image";
import React, { useEffect, useState } from "react";

interface Project {
  id: string;
  name: string;
  description: string;
  instructions: string;
  project_name: string;
  sensor_configuration: any[];
  image: string;
}

const Page = ({
  params,
}: {
  params: {
    project_id: string;
  };
}) => {
  const { project_id } = params;
  const [project, setProject] = useState<Project | null>(null);
  const [devices, setDevices] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    async function fetchProject() {
      const response = await fetch(
        `http://localhost:3003/api/v1/project?project_name=${project_id}`
      );
      const data = await response.json();
      console.log(data);
      const s = JSON.parse(data.sensor_configuration);

      let sensors = s.map((sensor: any) => {
        return {
          room_id: sensor.room_id,
          sensor_id: sensor.sensor_id,
          room_type: sensor.room_type,
          position: eval(sensor.position),
        };
      });

      setProject({
        id: data.id,
        name: data.name,
        description: data.description,
        instructions: data.instructions,
        project_name: data.project_name,
        sensor_configuration: sensors,
        image: data.image,
      });
    }

    async function fetchDevices() {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_SERVER_URL}/v1/occupancies?project=${project_id}`
      );

      if (!response.ok) {
        console.error("Failed to fetch devices");
        return;
      }

      const data = await response.json();

      const mp = new Map();

      for (const d of data) {
        mp.set(d.tag.split("_")[0], d.occupancy);
      }

      setDevices(mp);
    }

    fetchDevices();

    fetchProject();
  }, [project_id]);
  console.log(project);
  console.log(devices);
  return (
    <div className="w-screen h-full items-center justify-center flex flex-col">
      <h1 className="text-3xl text-center">Layout</h1>
      <div className="relative h-[80vh] mt-5 overflow-hidden w-fit bg-zinc-500 rounded-lg">
        {/* <img src={ base 64 */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          alt=""
          src={`data:image/png;base64,${project?.image}`}
          width={640}
          height={640}
        />
        {project?.sensor_configuration.map((sensor: any) => {
          console.log(sensor);
          return (
            <div
              key={sensor.sensor_id}
              className="absolute"
              style={{
                top: sensor.position[1],
                left: sensor.position[0],
                backgroundColor: devices.has(sensor.room_id + "")
                  ? devices.get(sensor.room_id + "") === "false"
                    ? "green"
                    : "red"
                  : "gray",
                border: "2px solid",
                borderColor: devices.has(sensor.room_id + "")
                  ? devices.get(sensor.room_id + "") === "false"
                    ? "green"
                    : "red"
                  : "gray",
                zIndex: 10,
              }}
            >
              {sensor.room_id +
                " " +
                (devices.has(sensor.room_id + "")
                  ? devices.get(sensor.room_id + "") === "false"
                    ? "Vacant"
                    : "Occupied"
                  : "Not Available")}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Page;
