package models

type Sensor struct {
	ID                int     `json:"id" db:"id"`                                 // Primary key
	SensorID          string  `json:"sensor_id" db:"sensor_id"`                   // Unique identifier for the sensor
	SensorType        int     `json:"sensor_type" db:"sensor_type"`               // Type of sensor (e.g., 1 for Ultrasonic, 2 for PIR)
	SensorName        string  `json:"sensor_name" db:"sensor_name"`               // Name of the sensor
	SensorUse         string  `json:"sensor_use" db:"sensor_use"`                 // Primary use or application of the sensor
	SensorRange       string  `json:"sensor_range" db:"sensor_range"`             // Operational range (e.g., "2-400 cm")
	SensorCost        float64 `json:"sensor_cost" db:"sensor_cost"`               // Cost of the sensor
	SensorPower       float64 `json:"sensor_power" db:"sensor_power"`             // Power consumption
	SensorWeight      float64 `json:"sensor_weight" db:"sensor_weight"`           // Weight of the sensor
	SensorSize        float64 `json:"sensor_size" db:"sensor_size"`               // Physical size
	SensorAccuracy    float64 `json:"sensor_accuracy" db:"sensor_accuracy"`       // Accuracy
	SensorDescription string  `json:"sensor_description" db:"sensor_description"` // Description of the sensor
}
