import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.metrics import log_loss, accuracy_score
import tqdm as tq

#
X, y = make_blobs(n_samples=100, n_features=2, centers=2, random_state=0)
X = X.reshape(X.shape[1], X.shape[0])
y = y.reshape(1, y.shape[0])


def initialisation(dimensions):

    parametres = {}

    for c in range(1, len(dimensions)):
        # Le paramètre W à la couche numéro c est une matrice aléatoire de taille (nbres de neurones à la couche c) X (nbres de neurones à la couche c - 1)
        parametres['W' + str(c)] = np.random.randn(dimensions[c], dimensions[c - 1]) 
        # Le paramètre b à la couche numéro c est une matrice aléatoire de taille (nbres de neurones à la couche c) X 1, c'est donc un vecteur
        parametres['b' + str(c)] = np.random.randn(dimensions[c], 1)

    return parametres

# liste1 = [2, 20, 12, 62, 5, 2, 1]
# parametres = initialisation(liste1)
# for cle, val in parametres.items():
#     print(cle, val.shape)
# print("----------------------------------------------")

def propagation_vers_l_avant(X, parametres):

    activations = {'A0' : X}

    C = len(parametres) // 2 # division entière de la longueur du dictionnaire "parametres" pour obtenir le nombre de couches du réseau de neurones

    for c in tq.tqdm(range(1, C + 1)):
        # calcul de la sortie linéaire Z à la couche numéro c
        Z = parametres['W' + str(c)].dot(activations['A' + str(c - 1)]) + parametres['b' + str(c)] 
        # on actualise le dictionnaire "activations" en lui ajoutant l'activation à la couche numéro c du réseau de neurones 
        activations['A' + str(c)] = 1 / (1 + np.exp(-Z))

    return activations

# activations = propagation_vers_l_avant(X, parametres)
# for cle, val in activations.items():
#     print(cle, val.shape)
# print("----------------------------------------------")

def propagation_vers_l_arriere(y, activations, parametres):

    # dictionnaire qui va contenir les variations à appliquer sur les paramètres W et b de chaque couche numéro c du réseau de neurones dans le but de corriger ces paramètres et donc de faire apprendre notre réseau de neurones.
    gradients = {} 
    m = y.shape[1] # nombre d'éléments de référence
    C = len(parametres) // 2 # division entière de la longueur du dictionnaire "parametres" pour obtenir le nombre de couches du réseau de neurones

    dZ = activations['A' + str(C)] - y # écart entre la sortie finale du réseau de neurones et la valeur attendue

    for c in reversed(range(1, C + 1)):

        gradients['dW' + str(c)] = (1 / m) * dZ.dot(activations['A' + str(c - 1)].T)
        # on fait la moyenne des écarts entre la 
        gradients['db' + str(c)] = (1 / m) * np.sum(dZ, axis=1, keepdims=True)
    
        if c > 1 :
            # on passe de la couche numéro c à la couche précédente c - 1
            dZ = (parametres['W' + str(c)].T).dot(dZ) * activations['A' + str(c - 1)] * (1 - activations['A' + str(c - 1)])

    return gradients

# gradients = propagation_vers_l_arriere(y, activations, parametres)
# for cle, val in gradients.items():
#     print(cle, val.shape)
# print("----------------------------------------------")

def mise_a_jour(gradients, parametres, pas_d_apprentissage):

    C = len(parametres) // 2 # division entière de la longueur du dictionnaire "parametres" pour obtenir le nombre de couches du réseau de neurones

    # mise à jour des deux paramètres afin de les affiner
    for c in range(1, C + 1):
        parametres['W' + str(c)] = parametres['W' + str(c)] - pas_d_apprentissage * gradients['dW' + str(c)]
        parametres['b' + str(c)] = parametres['b' + str(c)] - pas_d_apprentissage * gradients['db' + str(c)]

    return parametres

# parametres_affuttes = mise_a_jour(gradients, parametres, 0.1)
# for cle, val in parametres_affuttes.items():
#     print(cle, val.shape)
# print("----------------------------------------------")

def prediction(X, parametres):
    activations = propagation_vers_l_avant(X, parametres)
    C = len(parametres) // 2
    A = activations['A' + str(C)]
    return A >= 0.5

def reseau_neurones(X, y, couches=(20, 20, 20), pas_d_apprentissage=0.01, n_iter = 100000):
    
    np.random.seed(0)

    #initialisation des paramètres
    dimensions = list(couches)
    dimensions.insert(0, X.shape[0])
    dimensions.append(y.shape[0])
    parametres = initialisation(dimensions)

    cout_entrainement = []
    precision_pendant_entarinement = []

    for i in tq.tqdm(range(n_iter)):

        activations = propagation_vers_l_avant(X, parametres)
        gradients = propagation_vers_l_arriere(y, activations, parametres)
        parametres = mise_a_jour(gradients, parametres, pas_d_apprentissage)

        if i % 10 == 0:
            C = len(parametres) // 2
            cout_entrainement.append(log_loss(y, activations['A' + str(C)]))
            y_predit = prediction(X, parametres)
            precision_actuelle = accuracy_score(y.flatten(), y_predit.flatten())
            precision_pendant_entarinement.append(precision_actuelle)

    # visualisation des résultats
    plt.subplot(1, 2, 1)
    plt.plot(cout_entrainement, label='Évolution des pertes')
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(precision_pendant_entarinement, label='Évolution de la précision du modèle')
    plt.legend()

    plt.show()

    return parametres

parametres_finaux = reseau_neurones(X, y)