import Image from "next/image";
import React from "react";

interface Sensor {
  id: number; // Primary key
  sensor_id: string; // Unique identifier for the sensor
  sensor_type: number; // Type of sensor (e.g., 1 for Ultrasonic, 2 for PIR)
  sensor_name: string; // Name of the sensor
  sensor_use: string; // Primary use or application of the sensor
  sensor_range: string; // Operational range (e.g., "2-400 cm")
  sensor_cost: number; // Cost of the sensor
  sensor_power: number; // Power consumption
  sensor_weight: number; // Weight of the sensor
  sensor_size: number; // Physical size
  sensor_accuracy: number; // Accuracy
  sensor_description: string; // Description of the sensor
}

type SensorCardProps = {
  sensor: Sensor;
};

const SensorCard: React.FC<SensorCardProps> = ({ sensor }) => {
  return (
    <div className="max-w-sm rounded overflow-hidden shadow-lg p-6 m-4 border border-gray-200">
      <Image src="/sensor_pir.png" alt="Sensor" width={250} height={100} />
      <div className="flex justify-between items-center">
        <span className="text-xl font-bold">${sensor.sensor_cost}</span>
        <button className="bg-blue-500 m-4 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Add to project
        </button>
      </div>
      <h2 className="text-2xl font-bold mb-2">{sensor.sensor_name}</h2>
      <h4 className="text-lg font-bold mb-2">{sensor.sensor_description}</h4>
      <p className="mb-1">
        <strong>ID:</strong> {sensor.sensor_id}
      </p>
      <p className="mb-1">
        <strong>Type:</strong> {sensor.sensor_type}
      </p>
      <p className="mb-1">
        <strong>Use:</strong> {sensor.sensor_use}
      </p>
      <p className="mb-1">
        <strong>Range:</strong> {sensor.sensor_range}
      </p>
      <p className="mb-1">
        <strong>Power:</strong> {sensor.sensor_power} W
      </p>
      <p className="mb-1">
        <strong>Weight:</strong> {sensor.sensor_weight} kg
      </p>
      <p className="mb-1">
        <strong>Size:</strong> {sensor.sensor_size} cm
      </p>
      <p className="mb-1">
        <strong>Accuracy:</strong> {sensor.sensor_accuracy}%
      </p>
    </div>
  );
};

async function page() {
  try {
    const response = await fetch(`${process.env.API_SERVER_URL}/v1/sensors`);
    const data: Sensor[] = await response.json();

    return (
      <div className="flex flex-col justify-center items-center min-h-screen">
        <h1 className="text-4xl font-bold mb-8">Sensors Catalog</h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.map((sensor) => (
            <SensorCard key={sensor.id} sensor={sensor} />
          ))}
        </div>
      </div>
    );
  } catch (error) {
    console.error(`Failed to fetch sensors ${error}`);
    return <h1>Error</h1>;
  }
}

export default page;
