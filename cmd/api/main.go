package api

import (
	"main/internal/router"
	customrequestmapper "main/internal/tools/customRequestMapper"
	"main/internal/tools/di"
	"main/internal/tools/logger"

	"github.com/gofiber/fiber/v3"
)

func main() {
	
	app := fiber.New(fiber.Config{
		StructValidator: customrequestmapper.NouveauValideur(),
	})

	di.CreationDUDI()

	logger.ParametrerLogger()

	routeur := router.NouveauRouteur(app)

	routeur.Redirection()
	
	// TODO: Encapsuler le port dans une variable d'environnement
	app.Listen(":3000")
}