package responses

import (
	"main/internal/tools/message"

	"github.com/WangYihang/tranco-go-package"
)

// Struct représentant les URLs de l'API (qui pourra être convertie en JSON)
type ModelResponseURLs struct {
	Message *message.MessageHTTP `json:"message"`
	URLS    *tranco.TrancoList  `json:"urls"`
}
