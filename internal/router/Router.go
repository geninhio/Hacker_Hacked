package router

import (
	"main/internal/handlers"
	"main/internal/middlewares"

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
	r.Router.Use(middlewares.MiddlewareRecoverPanic)

	r.Router.Use(cors.New(cors.Config{
		AllowOrigins: []string{"*"},
		AllowHeaders: []string{"Origin, Content-Type, Accept"},
	}))

	// TODO: Finir la redirection
	api := r.Router.Group("api")
	api.Group("domainesProches").Get("/:URL", middlewares.MiddlewareRequeteDomaines, handlers.HandlerGetDomainesProches)

	r.Router.Use(middlewares.MiddlewareErreur404)
}
