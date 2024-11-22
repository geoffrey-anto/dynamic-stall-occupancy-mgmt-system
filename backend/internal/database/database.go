package database

import (
	"backend/internal/models"
	"context"
	"database/sql"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	_ "github.com/jackc/pgx/v5/stdlib"
	_ "github.com/joho/godotenv/autoload"
)

// Service represents a service that interacts with a database.
type Service interface {
	// Health returns a map of health status information.
	// The keys and values in the map are service-specific.
	Health() map[string]string

	// Close terminates the database connection.
	// It returns an error if the connection cannot be closed.
	Close() error

	UpdateOccupancy(id, occupancy string) error

	AddDevice(id, project string) error

	GetOccupanciesOfDevicesForProject(project string) ([]string, error)

	GetAllSensorNames() ([]models.Sensor, error)

	GetProjectByName(name string) (models.Project, error)
}

type service struct {
	db *sql.DB
}

var (
	database   = os.Getenv("DB_DATABASE")
	password   = os.Getenv("DB_PASSWORD")
	username   = os.Getenv("DB_USERNAME")
	port       = os.Getenv("DB_PORT")
	host       = os.Getenv("DB_HOST")
	schema     = os.Getenv("DB_SCHEMA")
	dbInstance *service
)

func New() Service {
	// Reuse Connection
	if dbInstance != nil {
		return dbInstance
	}
	connStr := fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable&search_path=%s", username, password, host, port, database, schema)
	db, err := sql.Open("pgx", connStr)
	if err != nil {
		log.Fatal(err)
	}

	Init(db)

	dbInstance = &service{
		db: db,
	}
	return dbInstance
}

func Init(db *sql.DB) {
	tx, err := db.BeginTx(context.Background(), &sql.TxOptions{})

	if err != nil {
		tx.Rollback()
		log.Fatal(err)
	}

	_, err = db.Exec("CREATE TABLE IF NOT EXISTS occupancy (id VARCHAR(255) PRIMARY KEY, occupancy VARCHAR(255), project VARCHAR(255), tag VARCHAR(255), name VARCHAR(255), position VARCHAR(255), UNIQUE(id))")

	if err != nil {
		tx.Rollback()
		log.Fatal(err)
	}

	_, err = db.Exec("CREATE TABLE IF NOT EXISTS projects (id SERIAL PRIMARY KEY, name VARCHAR(255), description TEXT, instructions TEXT, project_name VARCHAR(255), sensor_configuration TEXT, image TEXT, UNIQUE(name))")

	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec("CREATE TABLE IF NOT EXISTS sensors (id SERIAL PRIMARY KEY, sensor_id VARCHAR(255), sensor_type INT, sensor_name VARCHAR(255), sensor_use VARCHAR(255), sensor_range VARCHAR(255), sensor_cost FLOAT, sensor_power FLOAT, sensor_weight FLOAT, sensor_size FLOAT, sensor_accuracy FLOAT, sensor_description VARCHAR(255), UNIQUE(sensor_id))")

	if err != nil {
		log.Fatal(err)
	}

	tx.Commit()
}

// Health checks the health of the database connection by pinging the database.
// It returns a map with keys indicating various health statistics.
func (s *service) Health() map[string]string {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	stats := make(map[string]string)

	// Ping the database
	err := s.db.PingContext(ctx)
	if err != nil {
		stats["status"] = "down"
		stats["error"] = fmt.Sprintf("db down: %v", err)
		log.Fatalf(fmt.Sprintf("db down: %v", err)) // Log the error and terminate the program
		return stats
	}

	// Database is up, add more statistics
	stats["status"] = "up"
	stats["message"] = "It's healthy"

	// Get database stats (like open connections, in use, idle, etc.)
	dbStats := s.db.Stats()
	stats["open_connections"] = strconv.Itoa(dbStats.OpenConnections)
	stats["in_use"] = strconv.Itoa(dbStats.InUse)
	stats["idle"] = strconv.Itoa(dbStats.Idle)
	stats["wait_count"] = strconv.FormatInt(dbStats.WaitCount, 10)
	stats["wait_duration"] = dbStats.WaitDuration.String()
	stats["max_idle_closed"] = strconv.FormatInt(dbStats.MaxIdleClosed, 10)
	stats["max_lifetime_closed"] = strconv.FormatInt(dbStats.MaxLifetimeClosed, 10)

	// Evaluate stats to provide a health message
	if dbStats.OpenConnections > 40 { // Assuming 50 is the max for this example
		stats["message"] = "The database is experiencing heavy load."
	}

	if dbStats.WaitCount > 1000 {
		stats["message"] = "The database has a high number of wait events, indicating potential bottlenecks."
	}

	if dbStats.MaxIdleClosed > int64(dbStats.OpenConnections)/2 {
		stats["message"] = "Many idle connections are being closed, consider revising the connection pool settings."
	}

	if dbStats.MaxLifetimeClosed > int64(dbStats.OpenConnections)/2 {
		stats["message"] = "Many connections are being closed due to max lifetime, consider increasing max lifetime or revising the connection usage pattern."
	}

	return stats
}

// Close closes the database connection.
// It logs a message indicating the disconnection from the specific database.
// If the connection is successfully closed, it returns nil.
// If an error occurs while closing the connection, it returns the error.
func (s *service) Close() error {
	log.Printf("Disconnected from database: %s", database)
	return s.db.Close()
}

func (s *service) UpdateOccupancy(id, occupancy string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	o := ""

	err := dbInstance.db.QueryRowContext(ctx, "SELECT id, occupancy FROM occupancy WHERE id = $1", id).Scan(&id, &o)

	if err != nil {
		return fmt.Errorf("id not found: %v", err)
	}

	if o == "true" {
		o = "false"
	} else {
		o = "true"
	}

	_, err = dbInstance.db.ExecContext(ctx, "UPDATE occupancy SET occupancy = $1 WHERE id = $2", o, id)

	if err != nil {
		return fmt.Errorf("error updating occupancy: %v", err)
	}

	return nil
}

func (s *service) AddDevice(id, project string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	occupancy := "false"

	_, err := dbInstance.db.ExecContext(ctx, "INSERT INTO occupancy (id, project, occupancy) VALUES ($1, $2, $3)", id, project, occupancy)

	if err != nil {
		return fmt.Errorf("error adding device: %v", err)
	}

	return nil
}

func (s *service) GetOccupanciesOfDevicesForProject(project string) ([]string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	rows, err := dbInstance.db.QueryContext(ctx, "SELECT occupancy, id, project, tag, name, position FROM occupancy WHERE project = $1", project)

	if err != nil {
		return nil, fmt.Errorf("error getting occupancies: %v", err)
	}

	defer rows.Close()

	var occupancies []string

	for rows.Next() {
		var occupancy, id, project, tag, name, position string
		err := rows.Scan(&occupancy, &id, &project, &tag, &name, &position)

		if err != nil {
			return nil, fmt.Errorf("error scanning row: %v", err)
		}

		occupancies = append(occupancies, fmt.Sprintf("%s:%s:%s:%s:%s:%s", id, occupancy, project, tag, name, position))
	}

	return occupancies, nil

}

func (s *service) GetAllSensorNames() ([]models.Sensor, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	rows, err := dbInstance.db.QueryContext(ctx, "SELECT id, sensor_id, sensor_type, sensor_name, sensor_use, sensor_range, sensor_cost, sensor_power, sensor_weight, sensor_size, sensor_accuracy, sensor_description FROM sensors")

	if err != nil {
		return nil, fmt.Errorf("error getting sensors: %v", err)
	}

	defer rows.Close()

	var sensors []models.Sensor

	for rows.Next() {
		var sensor models.Sensor
		err := rows.Scan(&sensor.ID, &sensor.SensorID, &sensor.SensorType, &sensor.SensorName, &sensor.SensorUse, &sensor.SensorRange, &sensor.SensorCost, &sensor.SensorPower, &sensor.SensorWeight, &sensor.SensorSize, &sensor.SensorAccuracy, &sensor.SensorDescription)

		if err != nil {
			return nil, fmt.Errorf("error scanning row: %v", err)
		}

		sensors = append(sensors, sensor)
	}

	return sensors, nil
}

func (s *service) GetProjectByName(name string) (models.Project, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	var project models.Project
	err := dbInstance.db.QueryRowContext(ctx, "SELECT id, name, description, instructions, project_name, sensor_configuration, image FROM projects WHERE name = $1", name).Scan(&project.ID, &project.Name, &project.Description, &project.Instructions, &project.ProjectName, &project.SensorConfiguration, &project.Image)

	if err != nil {
		return models.Project{}, fmt.Errorf("error getting project: %v", err)
	}

	return project, nil
}
