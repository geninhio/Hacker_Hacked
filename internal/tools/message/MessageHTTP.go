package message

// Struct représentant un message de statut de réponse HTTP (en JSON)
type MessageHTTP struct {
	Code    int    `json:"code"`
	Statut  string `json:"statut"`
	Contenu string `json:"contenu"`
}

// Fonction pour créer un message de statut de réponse HTTP
// Prend en paramètre le code HTTP et un message optionnel
// Si le message n'est pas fourni, un message par défaut sera utilisé en fonction du code HTTP
// Retourne une instance de MessageHTTP
func CreerMessageHTTP(codeHTTP int, messageHTTP ...string) *MessageHTTP {

	// Initialisation du message HTTP
	var messageReponseHTTP MessageHTTP

	// Attribution du code HTTP
	messageReponseHTTP.Code = codeHTTP

	// Attribution d'un message par défaut en fonction du code HTTP
	switch code := codeHTTP; code {
	case 200:
		messageReponseHTTP.Statut = "OK"
	case 201:
		messageReponseHTTP.Statut = "Created"

	default:
		messageReponseHTTP.Code = 500
		messageReponseHTTP.Statut = "Internal Server Error" // Code erreur 500
	}

	// Si un message est fourni, l'utiliser
	if len(messageHTTP) != 0 {

		messageReponseHTTP.Contenu = messageHTTP[0]

		// Retourner directement l'erreur HTTP personnalisée avec le message fourni
		return &messageReponseHTTP
	}

	// Si le message n'est passé en paramètre, on utilise le statut comme message
	messageReponseHTTP.Contenu = messageReponseHTTP.Statut

	// Retourner l'erreur HTTP personnalisée avec le message par défaut
	return &messageReponseHTTP
}

// Méthode pour obtenir le message de l'erreur HTTP
func (m MessageHTTP) Error() string {
	return m.Contenu
}
