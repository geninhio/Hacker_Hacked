package requests

type ModelRequeteURLs struct {
	NbreDomaines    int `query:"limite" validate:"required,min=1"`
	NbreTopDomaines int `query:"top" validate:"required,min=1"`
}
