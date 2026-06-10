package logger

import (
	"io"

	"os"

	"github.com/gofiber/fiber/v3/log"
)

func ParametrerLogger() {
	fichier, err := os.OpenFile("logDeLApplication.txt", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0200)

	if err != nil {
		log.Fatal("Erreur lors de l'ouverture du fichier de log", err)
	}

	iw := io.MultiWriter(os.Stdout, fichier)

	log.SetOutput(iw)
}
