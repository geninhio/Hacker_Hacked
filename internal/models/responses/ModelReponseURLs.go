package responses

import (
	"main/internal/tools/message"
)

// Struct représentant les URLs de l'API (qui pourra être convertie en JSON)
type ModelResponseURLs struct {
	Message *message.MessageHTTP `json:"message"`
	URLS    []string             `json:"domaines"`
}
