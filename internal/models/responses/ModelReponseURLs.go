package responses

import (
	errorsinproject "main/internal/errorsInProject"

	"github.com/WangYihang/tranco-go-package"
)

// Struct représentant les URLs de l'API (qui pourra être convertie en JSON)
type ModelResponseURLs struct {
	Message errorsinproject.ErreurHTTP `json:"message"`
	URLS    *tranco.TrancoList         `json:"urls"`
}
