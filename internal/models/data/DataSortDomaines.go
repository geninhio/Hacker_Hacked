package data

type DomaineClassifie struct {
	Rang        int    `json:"rang"`
	NomDomaine  string `json:"nom_domaine"`
	Redirection bool   `json:"redirection_detectee"`
	Distance    int    `json:"distance"`
}
