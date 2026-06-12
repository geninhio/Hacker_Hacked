package controllers

import (
	errorsinproject "main/internal/errorsInProject"
	"main/internal/models/data"
	"main/internal/models/responses"
	"main/internal/repositories"
	"main/internal/tools/calculation"

	"github.com/gofiber/fiber/v3"
	"github.com/samber/do/v2"
)

type ControllerTopDomaine struct {
	Repository *repositories.RepositoryTopDomaine
}

func NouveauControllerTopDomaine(i do.Injector) (*ControllerTopDomaine, error) {
	// Récupérer le repository depuis l'injecteur
	repository, err := do.InvokeAs[*repositories.RepositoryTopDomaine](i)

	if err != nil {
		// Si une erreur se produit lors de la récupération du repository, retourner l'erreur
		return nil, err
	}

	// Retourner une nouvelle instance du controller avec le repository injecté
	return &ControllerTopDomaine{Repository: repository}, nil
}

func (c *ControllerTopDomaine) GetTopDomaines(nomDomaine string, nbreDomaines int, nbreTopDomaines int) (responses.ModelResponseURLs, *errorsinproject.ErreurHTTP) {

	var reponse responses.ModelResponseURLs

	domaine, err := c.Repository.RecupererTopDomaine(nbreDomaines)

	domainesProches := calculation.RetournerLesDomainesProches(nomDomaine, domaine.Domaines, nbreTopDomaines)

	return modeliseurDonnees(reponse, domainesProches, err)
}

func modeliseurDonnees(reponse responses.ModelResponseURLs, domaines []data.DomaineClassifie, erreur error) (responses.ModelResponseURLs, *errorsinproject.ErreurHTTP) {

	if erreur != nil {
		errHTTP := errorsinproject.ErrorHTTP(fiber.StatusInternalServerError, "Erreur lors de la récupération des domaines")
		return reponse, errHTTP
	}

	reponse.URLS = domaines

	return reponse, nil
}
