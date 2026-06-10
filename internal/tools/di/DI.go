package di

import (
	"main/internal/connectors"
	"main/internal/controllers"
	"main/internal/repositories"

	"github.com/samber/do/v2"
)

var Injecteur do.Injector

func creerPackage() func(do.Injector) {

	return func(i do.Injector) {

		do.ProvideTransient(i, connectors.NouveauConnectorHTTP)
		do.ProvideTransient(i, repositories.NouveauRepositoryTopDomaine)
		do.ProvideTransient(i, controllers.NouveauControllerTopDomaine)
	}
}

func CreationDUDI(p ...func(do.Injector)) {

	if len(p) > 1 {
		panic("CeateurDeDI ne peut accepter qu'un seul package de dépandances")
	}

	if len(p) == 0 {
		p = append(p, creerPackage())
	}

	injecteur := do.New(p[0])

	Injecteur = injecteur
}
