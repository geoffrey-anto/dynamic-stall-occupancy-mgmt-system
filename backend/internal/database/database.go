package database

import (
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

	_, err = db.Exec("CREATE TABLE IF NOT EXISTS occupancy (id VARCHAR(255) PRIMARY KEY, occupancy VARCHAR(255), project VARCHAR(255))")

	if err != nil {
		tx.Rollback()
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

	err := dbInstance.db.QueryRowContext(ctx, "SELECT id FROM occupancy WHERE id = $1", id).Scan(&id)

	if err != nil {
		return fmt.Errorf("id not found: %v", err)
	}

	_, err = dbInstance.db.ExecContext(ctx, "UPDATE occupancy SET occupancy = $1 WHERE id = $2", occupancy, id)

	if err != nil {
		return fmt.Errorf("error updating occupancy: %v", err)
	}

	return nil
}

func (s *service) AddDevice(id, project string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	_, err := dbInstance.db.ExecContext(ctx, "INSERT INTO occupancy (id, project) VALUES ($1, $2)", id, project)

	if err != nil {
		return fmt.Errorf("error adding device: %v", err)
	}

	return nil
}

func (s *service) GetOccupanciesOfDevicesForProject(project string) ([]string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	rows, err := dbInstance.db.QueryContext(ctx, "SELECT occupancy, id, project FROM occupancy WHERE project = $1", project)

	if err != nil {
		return nil, fmt.Errorf("error getting occupancies: %v", err)
	}

	defer rows.Close()

	var occupancies []string

	for rows.Next() {
		var occupancy, id, project string
		err := rows.Scan(&occupancy, &id, &project)

		if err != nil {
			return nil, fmt.Errorf("error scanning row: %v", err)
		}

		occupancies = append(occupancies, fmt.Sprintf("%s:%s:%s", id, occupancy, project))
	}

	return occupancies, nil

}
