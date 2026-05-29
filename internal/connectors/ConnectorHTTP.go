package connectors

import (
	"github.com/gofiber/fiber/v3/client"
	"github.com/samber/do/v2"
)

type ConnectorHTTP struct {
}

func NouveauConnectorHTTP(i do.Injector) (*ConnectorHTTP, error){
	return &ConnectorHTTP{}, nil
}

func (c *ConnectorHTTP) Get(url string, sortie any) error {

	requete := client.AcquireRequest()
	defer client.ReleaseRequest(requete)

	reponse, err := requete.Get(url)
	if err != nil {
		return err
	}

	return reponse.JSON(sortie)
}
