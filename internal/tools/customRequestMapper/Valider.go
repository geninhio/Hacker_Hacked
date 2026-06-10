package customrequestmapper

import "github.com/go-playground/validator/v10"

type StructValidator struct {
	valide *validator.Validate
}

func (v *StructValidator) Validate(i interface{}) error {
	return v.valide.Struct(i)
}

func NouveauValideur() *StructValidator {
	return &StructValidator{valide: validator.New()}
}


