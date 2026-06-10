package middlewares

import (
	errorsinproject "main/internal/errorsInProject"
	"main/internal/tools/response"
	"runtime/debug"

	"github.com/gofiber/fiber/v3"
	"github.com/gofiber/fiber/v3/log"
)

// Middleware qui permet de catch les panics que le code de Fiber/Golang peut produire
func MiddlewareRecoverPanic(c fiber.Ctx) error {
	defer func() {
		if r := recover(); r != nil {

			// Vérifier si le panic a envoyé une erreur à l'intérieur pour le formatage du log
			if err, ok := r.(error); !ok {
				log.Errorf("Panic: %v", r)

			} else {
				log.Error("Panic: " + err.Error())

			}
			log.Debug(string(debug.Stack()))

			// Créer et retourner le message d'erreur générique aux clients pour préserver les erreurs internes
			errHTTP := errorsinproject.ErrorHTTP(fiber.StatusInternalServerError)
			response.CreerReponseErreur(c, errHTTP)

		}
	}()

	// Retourner la prochaine étape du middleware ou du handler
	return c.Next()
}
