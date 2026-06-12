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
	nbre1 := c.Query("limite")
	nbre2 := c.Query("top")

	nbreDomaines, err1 := strconv.Atoi(nbre1)
	nbreTopDomaines, err2 := strconv.Atoi(nbre2)

	if err1 != nil {
		return response.CreerReponseErreur(c, errorsinproject.ErrorHTTP(fiber.StatusBadRequest, "Le paramètre 'limite' doit être un entier valide."))
	}

	if err2 != nil {
		return response.CreerReponseErreur(c, errorsinproject.ErrorHTTP(fiber.StatusBadRequest, "Le paramètre 'top' doit être un entier valide."))
	}

	if nbreDomaines < 1 || nbreDomaines > 1000000 {
		return response.CreerReponseErreur(c, errorsinproject.ErrorHTTP(fiber.StatusBadRequest, "Le nombre de domaines sur lesquels effectuer la recherche passé dans le paramètre 'limite' doit être compris entre 1 et 1000000."))
	}

	if nbreTopDomaines < 1 || nbreTopDomaines > 1000000 {
		return response.CreerReponseErreur(c, errorsinproject.ErrorHTTP(fiber.StatusBadRequest, "Le nombre de domaines faisant partie du top passé dans le paramètre 'top' doit être compris entre 1 et 1000000."))
	}

	parametres := requests.ModelRequeteURLs{
		NbreDomaines: nbreDomaines,
		NbreTopDomaines: nbreTopDomaines,
	}

	c.Locals("parametres", parametres)
	return c.Next()
}
