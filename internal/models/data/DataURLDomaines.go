package data

type InfoURLDomaines struct {
	IdListe    string `json:"list_id"`
	Disponible bool   `json:"available"`
	Echec      bool   `json:"failed"`
	Lien       string `json:"download"`
}
