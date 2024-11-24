import React from "react";
import { MDXRemote } from "next-mdx-remote/rsc";

interface Project {
  id: string;
  name: string;
  description: string;
  instructions: string;
  project_name: string;
  sensor_configuration: any[];
  image: string;
}

const Page = async ({
  params,
}: {
  params: {
    project_id: string;
  };
}) => {
  const response = await fetch(
    `http://backend:3003/api/v1/project?project_name=${params.project_id}`
  );
  const data = await response.json();
  console.log(data);
  const s = JSON.parse(data.sensor_configuration);

  const sensors = s.map((sensor: any) => {
    return {
      room_id: sensor.room_id,
      sensor_id: sensor.sensor_id,
      room_type: sensor.room_type,
      position: eval(sensor.position),
    };
  });

  const project: Project = {
    id: data.id,
    name: data.name,
    description: data.description,
    instructions: data.instructions,
    project_name: data.project_name,
    sensor_configuration: sensors,
    image: data.image,
  };

  console.log(project);

  return (
    <div className="w-screen h-full items-center justify-center flex flex-col">
      <h1 className="text-3xl font-bold">Instructions</h1>

      {/* <div className="w-full h-full flex flex-row justify-center">
        <div className="w-1/2 h-full flex flex-col items-center">
          <div className="w-full h-1/2 mt-4">
            <img
              alt=""
              src={`data:image/png;base64,${project?.image}`}
              width={640}
              height={640}
            />
          </div>
        </div>
      </div> */}

      <h3 className="text-xl font-bold mt-4">{project?.name}</h3>

      <div className="mt-4 max-w-4xl">
        <MDXRemote source={project?.description} />
      </div>

      <div className="mt-4 max-w-4xl">
        <MDXRemote source={project?.instructions} />
      </div>
    </div>
  );
};

export default Page;
