package middlewares

import (
	errorsinproject "main/internal/errorsInProject"
	"main/internal/models/requests"
	"main/internal/tools/response"
	"strconv"

	"github.com/gofiber/fiber/v3"
)

func MiddlewareRequeteDomaines(c fiber.Ctx) error {
	// Récupération du nombre de domaines depuis les paramètres de la requête
	nbre := c.Query("limite")

	nbreDomaines, err := strconv.Atoi(nbre)

	if err != nil {
		return response.CreerReponseErreur(c, errorsinproject.ErrorHTTP(fiber.StatusBadRequest, "Le paramètre 'limite' doit être un entier valide."))
	}

	if nbreDomaines < 1 {
		return response.CreerReponseErreur(c, errorsinproject.ErrorHTTP(fiber.StatusBadRequest, "Le nombre de domaines demandé doit être supérieur à 0."))
	}

	if nbreDomaines > 1000000 {
		return response.CreerReponseErreur(c, errorsinproject.ErrorHTTP(fiber.StatusBadRequest, "Le nombre de domaines demandé est trop élevé. La limite maximale est de 1000000."))
	}

	parametres := requests.ModelRequeteURLs{
		NbreDomaines: nbreDomaines,
	}

	c.Locals("parametres", parametres)
	return c.Next()
}
