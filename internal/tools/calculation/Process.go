package calculation

import (
	"main/internal/models/data"
	"runtime"
	"slices"
	"strconv"
	"strings"
	"sync"

	"github.com/gofiber/fiber/v3/log"
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

	type domaineParsé struct {
		rang int
		nom  string
	}
	domainesParsés := make([]domaineParsé, len(domaines))
	for i, d := range domaines {
		parts := strings.SplitN(d, ",", 2)
		rang, _ := strconv.Atoi(parts[0])
		domainesParsés[i] = domaineParsé{rang: rang, nom: parts[1]}
	}

	distanceDomaines := make([]int, len(domaines))

	nWorkers := runtime.NumCPU()
	taillBloc := len(domaines) / nWorkers

	var wg sync.WaitGroup

	for w := 0; w < nWorkers; w++ {
		debut := w * taillBloc
		fin := debut + taillBloc
		if w == nWorkers-1 {
			fin = len(domaines) // Le dernier worker prend le reste
		}

		wg.Add(1)
		go func(debut, fin int) {
			defer wg.Done()
			// Chaque worker traite son bloc séquentiellement
			for i := debut; i < fin; i++ {
				distanceDomaines[i] = distanceDeLevenshtein(nomDomaine, domainesParsés[i].nom)
			}
		}(debut, fin)
	}

	wg.Wait()
	indicesProches := retournerIndicesDesDomainesProches(distanceDomaines, nbreDomaines)

	domainesProches := make([]data.DomaineClassifie, len(indicesProches))

	for i, index := range indicesProches {
		domainesProches[i] = data.DomaineClassifie{
			Rang:       domainesParsés[index].rang,
			NomDomaine: domainesParsés[index].nom,
			Distance:   distanceDomaines[index],
		}
	}

	return domainesProches
}

func AssainirListeDomaines(domaines []data.DomaineClassifie, filtre func(a string) (string, bool, error)) []data.DomaineClassifie {

	domainesAssainis := make([]data.DomaineClassifie, 0, len(domaines))
	var mu sync.Mutex
	var wg sync.WaitGroup

	limite := make(chan struct{}, 50)

	for _, domaine := range domaines {
		wg.Add(1)

		go func(d data.DomaineClassifie) {
			defer wg.Done()

			limite <- struct{}{}
			defer func() { <-limite }()

			url := "http://www." + d.NomDomaine
			destination, redirige, err := filtre(url)

			if err != nil {
				log.Error("Erreur lors de la vérification de la redirection pour l'URL : ", url, " Erreur : ", err)
				return
			}

			if !redirige {
				d.Redirection = false
			} else {
				if strings.Contains(destination, "https://www."+d.NomDomaine) {
					d.Redirection = false
					_, redirige2, _ := filtre(destination)

					if redirige2 {
						d.Redirection = true
					}
				} else {
					d.Redirection = true
				}
			}

			mu.Lock()
			domainesAssainis = append(domainesAssainis, d)
			mu.Unlock()

		}(domaine)
	}

	wg.Wait()

	slices.SortStableFunc(domainesAssainis, func(a, b data.DomaineClassifie) int {
		if a.Distance < b.Distance {
			return -1
		}
		if a.Distance > b.Distance {
			return 1
		}
		if a.Distance == b.Distance {
			if a.Rang < b.Rang {
				return -1
			}
			if a.Rang > b.Rang {
				return 1
			}
		}
		return 0
	})

	return domainesAssainis
}
