package requests

type ModelRequeteURLs struct {
	NbreDomaines int `query:"limite" validate:"required,min=1"`
}