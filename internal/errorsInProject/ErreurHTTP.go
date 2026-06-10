package errorsinproject

// Struct représentant une erreur HTTP personnalisée (qui pourra être convertie en JSON)
type ErreurHTTP struct {
	Message struct {
		Code    int    `json:"code"`
		Statut  string `json:"statut"`
		Contenu string `json:"contenu"`
	} `json:"message"`
}

// Fonction pour créer une erreur HTTP personnalisée
// Prend en paramètre le code HTTP et un message optionnel
// Si le message n'est pas fourni, un message par défaut sera utilisé en fonction du code HTTP
// Retourne une instance de ErreurHTTP
func ErrorHTTP(codeHTTP int, messageHTTP ...string) *ErreurHTTP {

	// Initialisation de l'erreur HTTP
	var erreur ErreurHTTP

	// Attribution du code HTTP
	erreur.Message.Code = codeHTTP

	// Attribution d'un message par défaut en fonction du code HTTP
	switch code := codeHTTP; code {
	case 400:
		erreur.Message.Statut = "Bad Request"
	case 401:
		erreur.Message.Statut = "Unauthorized"
	case 403:
		erreur.Message.Statut = "Forbidden"
	case 404:
		erreur.Message.Statut = "Not Found"
	case 405:
		erreur.Message.Statut = "Method Not Allowed"
	case 500:
		erreur.Message.Statut = "Internal Server Error"
	case 501:
		erreur.Message.Statut = "Not Implemented"
	default:
		erreur.Message.Code = 500
		erreur.Message.Statut = "Internal Server Error" // Code erreur 500
	}

	// Si un message est fourni, l'utiliser
	if len(messageHTTP) != 0 {

		erreur.Message.Contenu = messageHTTP[0]

		// Retourner directement l'erreur HTTP personnalisée avec le message fourni
		return &erreur
	}

	// Si le message n'est passé en paramètre, on utilise le statut comme message
	erreur.Message.Contenu = erreur.Message.Statut

	// Retourner l'erreur HTTP personnalisée avec le message par défaut
	return &erreur
}

// Méthode pour obtenir le message de l'erreur HTTP
func (e ErreurHTTP) Error() string {
	return e.Message.Contenu
}