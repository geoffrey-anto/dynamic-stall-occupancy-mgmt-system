package server

import (
	"fmt"
	"strings"

	"github.com/gofiber/fiber/v2"
)

func (s *FiberServer) RegisterFiberRoutes() {
	s.App.Get("/", s.HelloWorldHandler)

	s.App.Get("/health", s.healthHandler)

	s.App.Post("/api/v1/occupancy", s.UpdateOccupancy)

	s.App.Post("/api/v1/device", s.AddDevice)

	s.App.Get("/api/v1/occupancies", s.GetOccupanciesOfDevicesForProject)

	s.App.Get("/api/v1/sensors", s.GetSensors)

	s.App.Get("/api/v1/project", s.GetProjectById)
}

func (s *FiberServer) HelloWorldHandler(c *fiber.Ctx) error {
	resp := fiber.Map{
		"message": "API WORKING!",
	}

	return c.JSON(resp)
}

func (s *FiberServer) healthHandler(c *fiber.Ctx) error {
	return c.JSON(s.db.Health())
}

func (s *FiberServer) UpdateOccupancy(c *fiber.Ctx) error {
	occupancy := c.FormValue("occupancy")
	id := c.FormValue("id")
	fmt.Printf("Occupancy: %s, ID: %s\n", occupancy, id)

	if occupancy == "0" {
		occupancy = "false"
	} else if occupancy == "1" {
		occupancy = "true"
	}

	if occupancy == "" || id == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"message": "Invalid request",
		})
	}

	err := s.db.UpdateOccupancy(id, occupancy)

	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"message": "Error updating occupancy",
		})
	}

	return c.JSON(fiber.Map{
		"message": "Occupancy updated",
	})
}

func (s *FiberServer) AddDevice(c *fiber.Ctx) error {
	id := c.FormValue("id")
	project := c.FormValue("project")

	if id == "" || project == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"message": "Invalid request",
		})
	}

	err := s.db.AddDevice(id, project)

	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"message": "Error adding device",
		})
	}

	return c.JSON(fiber.Map{
		"message": "Device added",
	})
}

func (s *FiberServer) GetOccupanciesOfDevicesForProject(c *fiber.Ctx) error {
	project := c.Query("project")

	if project == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"message": "Invalid request",
		})
	}

	occupancies, err := s.db.GetOccupanciesOfDevicesForProject(project)

	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"message": "Error getting occupancies",
			"error":   err.Error(),
		})
	}

	res := []map[string]string{}

	for _, occupancy := range occupancies {
		res = append(res, map[string]string{
			"id":        strings.Split(occupancy, ":")[0],
			"occupancy": strings.Split(occupancy, ":")[1],
			"project":   strings.Split(occupancy, ":")[2],
			"tag":       strings.Split(occupancy, ":")[3],
			"name":      strings.Split(occupancy, ":")[4],
		})
	}

	return c.JSON(res)
}

func (s *FiberServer) GetSensors(c *fiber.Ctx) error {
	sensors, err := s.db.GetAllSensorNames()

	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"message": "Error getting sensors",
			"error":   err.Error(),
		})
	}

	return c.JSON(sensors)
}

func (s *FiberServer) GetProjectById(c *fiber.Ctx) error {
	project_name := c.Query("project_name")

	projects, err := s.db.GetProjectByName(project_name)

	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"message": "Error getting projects",
			"error":   err.Error(),
		})
	}

	return c.JSON(projects)
}
