package connectors

import (
	"time"

	"github.com/gofiber/fiber/v3"
	"github.com/gofiber/fiber/v3/client"
	"github.com/samber/do/v2"
)

type ConnectorHTTP struct {
}

func NouveauConnectorHTTP(i do.Injector) (*ConnectorHTTP, error) {
	client.C().SetTimeout(10 * time.Second)
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

func (c *ConnectorHTTP) CheckerRedirection(url string) (string, bool, error) {

	reponse, err := client.Get(url, client.Config{
		MaxRedirects: 0,
		Timeout:      625 * time.Millisecond,
		UserAgent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
	})

	if err != nil {
		return "", false, err
	}
	defer reponse.Close()

	statusCode := reponse.StatusCode()

	if statusCode == fiber.StatusMovedPermanently ||
		statusCode == fiber.StatusFound ||
		statusCode == fiber.StatusTemporaryRedirect ||
		statusCode == fiber.StatusPermanentRedirect {

		destination := reponse.Header("Location")
		return destination, true, nil
	}

	return "", false, nil
}
