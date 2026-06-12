package handlers

import (
	"main/internal/controllers"
	errorsinproject "main/internal/errorsInProject"
	"main/internal/models/requests"
	"main/internal/tools/di"
	"main/internal/tools/message"
	"main/internal/tools/response"

	"github.com/gofiber/fiber/v3"
	"github.com/gofiber/fiber/v3/log"
	"github.com/samber/do/v2"
)

func HandlerGetDomainesProches(c fiber.Ctx) error {

	nomDomaine := c.Params("URL")

	parametres, ok := c.Value("parametres").(requests.ModelRequeteURLs)

	if !ok {
		return response.CreerReponseErreur(c, errorsinproject.ErrorHTTP(fiber.StatusBadRequest, "Paramètres invalides"))
	}

	controller, errInvoke := do.InvokeAs[*controllers.ControllerTopDomaine](di.Injecteur)

	if errInvoke != nil {
		log.Error("Erreur lors de l'invocation du controller : ", errInvoke)
		return response.CreerReponseErreur(c, errorsinproject.ErrorHTTP(fiber.StatusInternalServerError, "Erreur lors de l'invocation du controller"))
	}

	contenu, errController := controller.GetTopDomaines(nomDomaine, parametres.NbreDomaines, parametres.NbreTopDomaines)

	if errController != nil {
		return response.CreerReponseErreur(c, errController)
	}

	contenu.Message = message.CreerMessageHTTP(fiber.StatusOK, "Domaines proches récupérés avec succès")

	return response.CreerReponseContenu(c, contenu, fiber.StatusOK)
}
