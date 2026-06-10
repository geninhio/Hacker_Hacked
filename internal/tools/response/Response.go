package response

import (
	errorsinproject "main/internal/errorsInProject"

	"github.com/gofiber/fiber/v3"
)

func CreerReponseContenu(c fiber.Ctx, donnees any, codeHTTP int, messageHTTP ...string) error {
	return c.Status(codeHTTP).JSON(donnees)
}

func CreerReponseErreur(c fiber.Ctx, erreur *errorsinproject.ErreurHTTP) error {
	return c.Status(erreur.Message.Code).JSON(erreur)
}
