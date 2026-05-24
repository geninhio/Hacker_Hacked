import re
import requests
import pandas as pd
import asyncio 
import time
import threading
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_top_domaine () : 

    try:
        reponse = requests.get(f'https://tranco-list.eu/api/lists/id/YLLKG')
        if reponse.status_code == 200 :
            lien = reponse.json()['download']
            donnees = requests.get(lien).text.split(f'\r\n')
            # print(requests.get(lien).text)
            # donnees = pd.read_csv(donnees, sep=",")
            # donnees = donnees.to_json()
            n = 0
            sites_web = []
            for ligne in donnees:
                if ligne != "":
                    # if n == 20:
                    #     break
                    ligne = ligne.split(",")
                    sites_web.append(ligne[1])
                    n += 1

            return sites_web
      
        else:
            return []
        
    except Exception as e:
        print(f"Erreur API: {e}")
        return []
    
def get_domaine_file () : 

    try:
        sites_web = []
        with open("domaines.csv", "r") as f:
            for ligne in f.readlines():
                if ligne != "":
                    # if n == 20:
                    #     break
                    ligne = ligne.split(",")
                    sites_web.append(ligne[1])
        return sites_web
        
    except Exception as e:
        print(f"Erreur API: {e}")
        return []
    
def extraire_nom_domaine(url):

    chaine = r'\.([\.\w-]+\.[\w\.]+)'                 
    txt = re.findall(chaine, url)[0]
    return txt

def assainir_liste_domaine(cible):
    
    domaines = get_top_domaine()
    domaines_filtrees = []

    for domaine in domaines:
        if (len(cible) - 2 <= len(domaine)) and (len(domaine) <= len(cible) + 2):
            domaines_filtrees.append(domaine)


    return domaines_filtrees


def distance_Levenstein(mot1, mot2):

    n, m = len(mot1), len(mot2)
    avant = list(range(m + 1))
    courant = [0] * (m + 1)

    for i in range(1, n + 1):
        courant[0] = i
        for j in range(1, m + 1):
            insertion = courant[j - 1] + 1
            suppression = avant[j] + 1
            substitution = avant[j - 1] + (0 if mot1[i - 1] == mot2[j - 1] else 1)
            courant[j] = min(insertion, suppression, substitution)
        avant, courant = courant, avant

    return avant[m]

def derniersIndiceMinimum(liste, n):

    liste2 = liste.copy()
    liste2.sort()
    liste_index_dans_liste = []

    for i in range(n):

        if i == 0:
            liste_index_dans_liste.append(liste.index(liste2[i]))
        else:
            min = liste2[i - 1]
            if liste2[i] == min:
                liste_index_dans_liste.append(liste.index(liste2[i], liste_index_dans_liste[i - 1] + 1))
            else : 
                liste_index_dans_liste.append(liste.index(liste2[i]))


    return liste_index_dans_liste

def retourner_les_domaines_proches(cible, liste, n):
    # t = time.time()

    if n <= 0 :
        return []
    
    #domaines = assainir_liste_domaine(cible)
    domaines = liste

    liste_distance = []
    patterns_proches = []


    for domaine in tqdm(domaines) :
        liste_distance.append(distance_Levenstein(cible, domaine))

    liste_indices_patterns_proches = derniersIndiceMinimum(liste_distance, n)

    liste_distance_patterns_proches = []
    for indice in liste_indices_patterns_proches:
        patterns_proches.append(domaines[indice])
        liste_distance_patterns_proches.append(liste_distance[indice])


    return patterns_proches

def ouvrir_page(url):

    nom_domaine = extraire_nom_domaine(url)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options = options)

    driver.get(url)

    fenetre = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
    driver.set_window_size(fenetre('Width'), fenetre('Height'))

    chemin_screenshot = f'.\Desktop\{nom_domaine}.png'
    load = driver.find_element(By.TAG_NAME, 'body').screenshot(chemin_screenshot)
    driver.quit()

    if load:
        return load, chemin_screenshot
    else:
        return load, 'Erreur lors de la prise de screenshot'
    
# print(get_top_domaine())
# print("-------------------------------------------------------------------------------")
string = "https://www.facebookk.com/python/python_regex.asp"
#print(len(assainir_liste_domaine(extraire_nom_domaine(string))))

#print(extraire_nom_domaine(string))
cible = extraire_nom_domaine(string)

# async def rechercher_les_domaines_proches(domaine, n):

#     tache1 = asyncio.create_task(retourner_les_domaines_proches(cible, domaine[:int(len(domaine)/5)], n))
#     tache2 = asyncio.create_task(retourner_les_domaines_proches(cible, domaine[int(len(domaine)/5):int(2 * len(domaine)/5)], n))
#     tache3 = asyncio.create_task(retourner_les_domaines_proches(cible, domaine[int(2 * len(domaine)/5):int(3 * len(domaine)/5)], n))
#     tache4 = asyncio.create_task
#     print(await retourner_les_domaines_proches(cible, domaine[:int(len(domaine)/5)], n))
#     print(await retourner_les_domaines_proches(cible, domaine[int(len(domaine)/5):int(2 * len(domaine)/5)], n))
#     print(await retourner_les_domaines_proches(cible, domaine[int(2 * len(domaine)/5):int(3 * len(domaine)/5)], n))
#     print(await retourner_les_domaines_proches(cible, domaine[int(3 * len(domaine)/5):int(4 * len(domaine)/5)], n))
#     print(await retourner_les_domaines_proches(cible, domaine[int(4 * len(domaine)/5):], n))

# def Creer_les_cinq_processus(domaine, n):

#     # références : https://www.tutorialspoint.com/check-if-a-thread-has-started-in-python, 
#     # https://www.dataquest.io/blog/multithreading-in-python/?utm_source=google&utm_medium=&matchtype=&device=c&utm_campaign=remarketing&campaignid=22944558136&adgroupid=&adid=&utm_content=&gad_source=1&gad_campaignid=22934590983&gbraid=0AAAAADgix8Pue5I36GD4qNi7mKMmR_VyA&gclid=EAIaIQobChMIv5KNu6n-jwMVGjIIBR1S3iZhEAAYASAAEgK7-vD_BwE

#     threads = []
#     threads.append(threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[:int(len(domaine)/2)], n)))
#     # threads.append(threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(len(domaine)/5):int(2 * len(domaine)/5)], n)))
#     # threads.append(threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(2 * len(domaine)/5):int(3 * len(domaine)/5)], n)))
#     # threads.append(threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(3 * len(domaine)/5):int(4 * len(domaine)/5)], n)))
#     # threads.append(threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(4 * len(domaine)/5):], n)))
#     threads.append(threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(len(domaine)/2):], n)))

#     return threads

     
# print(cible)
# print(retourner_les_domaines_proches(cible, 3))
#print(distance_Levenstein(cible, "amazonaws.com"))
#retourner_les_domaines_proches(cible, 4)
# t = time.time()

# ouvrir_page("https://portfolio-alexy.wstd.io")

domaine = get_top_domaine()
domaines_proches = retourner_les_domaines_proches(cible, domaine, 3)

print(domaines_proches)

for domaine_proche in domaines_proches:
    url = f"https://www.{domaine_proche}/"
    load, chemin_screenshot = ouvrir_page(url)
    if load:
        print(f"Screenshoot enregistré : {chemin_screenshot}")
    else:
        print(chemin_screenshot)

#retourner_les_domaines_proches(cible, domaine, 4)
# threads = Creer_les_cinq_processus(domaine, 4)

# for thread in threads:
#     thread.start()

# for thread in threads:
#     thread.join()

# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[:int(len(domaine)/2)], 4)).start()
# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(len(domaine)/2):], 4)).start()

# if threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[:int(len(domaine)/2)], 4)).is_alive():
    # threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[:int(len(domaine)/2)], 4)).join()
    # threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(len(domaine)/2):], 4)).join()

# print(time.time() - t)
# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[:int(len(domaine)/5)], 4)).start()
# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(len(domaine)/5):int(2 * len(domaine)/5)], 4)).start()
# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(2 * len(domaine)/5):int(3 * len(domaine)/5)], 4)).start()
# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(3 * len(domaine)/5):int(4 * len(domaine)/5)], 4)).start()
# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(4 * len(domaine)/5):], 4)).start()


# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[:int(len(domaine)/5)], 4)).join()
# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(len(domaine)/5):int(2 * len(domaine)/5)], 4)).join()
# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(2 * len(domaine)/5):int(3 * len(domaine)/5)], 4)).join()
# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(3 * len(domaine)/5):int(4 * len(domaine)/5)], 4)).join()
# threading.Thread(target=retourner_les_domaines_proches, args=(cible, domaine[int(4 * len(domaine)/5):], 4)).join()
#print(time.time() - t)

# liste1 = [3, 1, 8, 1, 7, 1, 9]
# liste = liste1
# liste2 = liste1.copy()
# liste2.sort()




# print(liste.index(liste2[0]))
# print(liste.index(liste2[1], liste.index(liste2[0]) + 1))

# liste_index_dans_liste = []

# for i in range(3):

#     if i == 0:
#         liste_index_dans_liste.append(liste.index(liste2[i]))
#     else:
#         min = liste2[i - 1]
#         if liste2[i] == min:
#             liste_index_dans_liste.append(liste.index(liste2[i], liste_index_dans_liste[i - 1] + 1))
#         else : 
#             liste_index_dans_liste.append(liste.index(liste2[i]))

# print(liste)
# print(liste2)
# print(liste_index_dans_liste)






# mot1 = "chaud"
# mot2 = "chatte"
# n = len(mot1)
# m = len(mot2)
# prev = list(range(m + 1))
# curr = [0] * (m + 1)

# print(prev)
# print(curr)
# print("------------------------------------------------------")
# for i in range(1, n + 1):
#     curr[0] = i
#     for j in range(1, m + 1):
#         insert = curr[j - 1] + 1
#         delete = prev[j] + 1
#         substitute = prev[j - 1] + (0 if mot1[i - 1] == mot2[j - 1] else 1)
#         curr[j] = min(insert, delete, substitute)
#     prev, curr = curr, prev
#     print(prev)
#     print(curr)

## Documentation SeleniumBase 
# https://seleniumbase.io/
# https://www.google.com/search?q=seleniumbase+docker&sca_esv=c041460d2f1f94b3&ei=6aIMaaWzC8Tk5NoPh9DpqAw&oq=seleniumbase+with+doc&gs_lp=Egxnd3Mtd2l6LXNlcnAiFXNlbGVuaXVtYmFzZSB3aXRoIGRvYyoCCAAyBhAAGBYYHjIGEAAYFhgeMgYQABgWGB4yBhAAGBYYHjIGEAAYFhgeMggQABiABBiiBDIFEAAY7wUyBRAAGO8FMgUQABjvBUi9QVCBBVj8K3ACeAGQAQCYAccDoAGDCaoBBzguMS40LTG4AQPIAQD4AQGYAgygAsMJwgIKEAAYsAMY1gQYR8ICDRAAGIAEGLADGEMYigXCAgcQABiABBgTwgIIEAAYExgWGB7CAggQABgWGAoYHsICCRAAGIAEGBMYDcICCBAAGBMYDRgemAMAiAYBkAYMkgcIMTAuMS40LTGgB4A8sgcHOC4xLjQtMbgHuwnCBwYwLjIuMTDIBy4&sclient=gws-wiz-serp#fpstate=ive&vld=cid:4ff18177,vid:xrYDlx8evR0,st:0