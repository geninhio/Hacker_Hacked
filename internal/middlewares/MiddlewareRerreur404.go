package middlewares

import (
	errorsinproject "main/internal/errorsInProject"
	"main/internal/tools/response"

	"github.com/gofiber/fiber/v3"
)

// Middleware qui valide les paramètres de la requête pour la route de moyenne de la qualité de l'air
func MiddlewareErreur404(c fiber.Ctx) error {
	// Création d'une erreur 404 puisqu'il n'existe pas de route pour la demande du client
	errHTTP := errorsinproject.ErrorHTTP(fiber.StatusNotFound, "Aucune route ne correspond à votre demande")
	return response.CreerReponseErreur(c, errHTTP)
}
