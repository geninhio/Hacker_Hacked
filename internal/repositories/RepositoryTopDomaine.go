package repositories

import (
	"main/internal/connectors"
	"main/internal/models/data"
	"time"

	"github.com/WangYihang/tranco-go-package"
	"github.com/gofiber/fiber/v3/log"
	"github.com/samber/do/v2"
)

type RepositoryTopDomaine struct {
	Connexion *connectors.ConnectorHTTP
}

func NouveauRepositoryTopDomaine(i do.Injector) (*RepositoryTopDomaine, error) {

	connexion, err := connectors.NouveauConnectorHTTP(i)

	if err != nil {
		return nil, err
	}

	return &RepositoryTopDomaine{Connexion: connexion}, nil
}

func (r *RepositoryTopDomaine) RecupererInfosURLTopDomaine(url string) (data.InfoURLDomaines, error) {

	var sortie data.InfoURLDomaines
	err := r.Connexion.Get(url, sortie)

	if err != nil {
		log.Error("Erreur lors de la récupération des infos sur L'URL des top domaines")
		return data.InfoURLDomaines{}, err
	}

	return sortie, nil
}

func (r *RepositoryTopDomaine) RecupererTopDomaine() (*tranco.TrancoList, error) {

	// recuperer la date du jour
	dateDuJour := time.Now().Format("2006-01-02")

	// recuperer les domaines
	domaines, err := tranco.NewTrancoList(dateDuJour, false, "1000000")

	// si il y a une erreur lors de la recuperation des domaines retourne nil
	if err != nil {
		log.Error("Erreur lors de la récupération des domaines")
		return nil, err
	}

	// retourne la liste des domaines
	return domaines, nil
}
