package repositories

import (
	"bufio"
	"main/internal/connectors"
	"main/internal/models/data"
	"net/http"
	"strconv"
	"strings"
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

func (r *RepositoryTopDomaine) recupererInfosURLTopDomaine(url string) (data.InfoURLDomaines, error) {

	var sortie data.InfoURLDomaines
	err := r.Connexion.Get(url, &sortie)

	if err != nil {
		log.Error("Erreur lors de la récupération des infos sur L'URL des top domaines: ", err)
		return data.InfoURLDomaines{}, err
	}

	return sortie, nil
}

func (r *RepositoryTopDomaine) RecupererTopDomaine(nbreDomaines int) (data.Domaines, error) {

	var domaines data.Domaines
	//TODO: encapsuler l'URL dans une variable d'environnement
	infosurl, err := r.recupererInfosURLTopDomaine("https://tranco-list.eu/api/lists/date/latest")

	if err != nil {
		return data.Domaines{}, err
	}

	url := infosurl.Lien

	urlACurl := strings.ReplaceAll(url, "1000000", strconv.Itoa(nbreDomaines))

	resp, errCurl := http.Get(urlACurl)

	if errCurl != nil {
		log.Error("Erreur lors de la récupération des domaines avec curl: ", errCurl)
		return data.Domaines{}, errCurl
	}

	defer resp.Body.Close()

	scanner := bufio.NewScanner(resp.Body)
	for scanner.Scan() {
		domaines.Domaines = append(domaines.Domaines, scanner.Text())
	}

	if err := scanner.Err(); err != nil {
		log.Error("Erreur lors de la lecture de la réponse: ", err)
		return data.Domaines{}, err
	}

	return domaines, nil
}

func (r *RepositoryTopDomaine) RecupererTopDomaineSansCurl() (*tranco.TrancoList, error) {

	// recuperer la date du jour
	dateDuJour := time.Now().Format("2006-01-02")

	// recuperer les domaines
	domaines, err := tranco.NewTrancoList(dateDuJour, false, "1000000")

	// si il y a une erreur lors de la recuperation des domaines retourne nil
	if err != nil {
		log.Error("Erreur lors de la récupération des domaines", err)
		return nil, err
	}

	// retourne la liste des domaines
	return domaines, nil
}
