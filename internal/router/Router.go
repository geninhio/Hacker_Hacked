package router

import (
	"github.com/gofiber/fiber/v3"
	"github.com/gofiber/fiber/v3/middleware/cors"
)

type Router struct {
	Router *fiber.App
}

func NouveauRouteur(app *fiber.App) *Router {
	return &Router{Router: app}
}

func (r *Router) Redirection() {

	// TODO: Faire un recover de panic pour go pour ne pas arreter le serveur

	r.Router.Use(cors.Config{
		AllowOrigins: []string{"*"},
		AllowHeaders: []string{"Origin, Content-Type, Accept"},
	})


	// TODO: Finir la redirection
	
}
