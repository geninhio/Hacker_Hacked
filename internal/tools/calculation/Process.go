package calculation

import (
	"main/internal/models/data"
	"slices"
	"strconv"
	"strings"
)

func distanceDeLevenshtein(s1, s2 string) int {

	m := len(s1)
	n := len(s2)
	avant := make([]int, n+1)
	courant := make([]int, n+1)

	for j := 0; j <= n; j++ {
		avant[j] = j
	}

	for i := 1; i <= m; i++ {
		courant[0] = i
		for j := 1; j <= n; j++ {
			insertion := courant[j-1] + 1
			suppression := avant[j] + 1
			substitution := avant[j-1]
			if s1[i-1] != s2[j-1] {
				substitution++
			}
			courant[j] = min(insertion, suppression, substitution)
		}
		avant, courant = courant, avant
	}

	return avant[n]

}

func retournerIndicesDesDomainesProches(distanceDomaines []int, nbreDomaines int) []int {

	type DomaineDistance struct {
		Index    int
		Distance int
	}

	domainesDistances := make([]DomaineDistance, len(distanceDomaines))

	for i, distance := range distanceDomaines {
		domainesDistances[i] = DomaineDistance{Index: i, Distance: distance}
	}

	// Tri des domaines par distance
	slices.SortStableFunc(domainesDistances, func(a, b DomaineDistance) int {
		if a.Distance < b.Distance {
			return -1
		}
		if a.Distance > b.Distance {
			return 1
		}
		return 0
	})

	indicesProches := make([]int, 0, nbreDomaines)
	for i := 0; i < nbreDomaines && i < len(domainesDistances); i++ {
		indicesProches = append(indicesProches, domainesDistances[i].Index)
	}

	return indicesProches

}

func RetournerLesDomainesProches(nomDomaine string, domaines []string, nbreDomaines int) []data.DomaineClassifie {
	
	distanceDomaines := make([]int, len(domaines))

	for i, domaine := range domaines {
		domaine = strings.Split(domaine, ",")[1]
		distanceDomaines[i] = distanceDeLevenshtein(nomDomaine, domaine)
	}

	indicesProches := retournerIndicesDesDomainesProches(distanceDomaines, nbreDomaines)
	
	domainesProches := make([]data.DomaineClassifie, len(indicesProches))
	
	for i, index := range indicesProches {
		rang, _ := strconv.Atoi(strings.Split(domaines[index], ",")[0])
		domainesProches[i] = data.DomaineClassifie{
			Rang:       rang,
			NomDomaine: strings.Split(domaines[index], ",")[1],
			Distance:   distanceDomaines[index],
		}
	}
	return domainesProches
}
