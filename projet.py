import pandas as pd
import os

ot_odr_filename = os.path.join(".", "OT_ODR.csv.bz2")
ot_odr_df = pd.read_csv(ot_odr_filename, compression="bz2", sep=";")
longueur_ot_odr_df = len(ot_odr_df)


equipements_filename = os.path.join(".", 'EQUIPEMENTS.csv')
equipements_df = pd.read_csv(equipements_filename, sep=";")

# Liste déroulante pour SIG_CONTEXTE
import pandas as pd

df = pd.DataFrame(ot_odr_df['SIG_CONTEXTE'])

# Création du dictionnaire
dictionnaire = {}

for _, row in df.iterrows():
    sig_contexte = row['SIG_CONTEXTE']
    contexte_parts = sig_contexte.split('/')
    
    # Parcourir les parties du contexte
    current_dict = dictionnaire
    for part in contexte_parts:
        # Vérifier si la partie existe dans le dictionnaire
        if part not in current_dict:
            current_dict[part] = {}
        
        # Passer au dictionnaire interne
        current_dict = current_dict[part]



## Stocker la liste dictionnaire

import pickle

path = 'liste_deroulante_SIG_CONTEXTE.pkl'

# Sérialisation du dictionnaire
with open(path,'wb') as fichier:
    pickle.dump(dictionnaire, fichier)

# Désérialisation du dictionnaire
with open(path, 'rb') as fichier:
    dictionnaire = pickle.load(fichier)


# Normaliser le texte
# ### Supprimer les caractères spéciaux

# import unicodedata

# def Replace_accents(word):
#     try:
#         word = unicodedata.normalize('NFD', word).encode('ascii', 'ignore').decode('utf-8')
#     except:
#         pass
#     return word


# def Delete_special_caractere(word):
#     word = Replace_accents(word)
#     try:
#         word = word.replace('\\', '_').replace('/', '_').replace('-', '_').replace("'", ' ').replace('"', ' ').replace('`', ' ').replace('!', ' ').replace('@', ' ').replace('#', ' ').replace('$', ' ').replace('%', ' ').replace('^', ' ').replace('&', ' ').replace('*', ' ').replace('(', ' ').replace(')', ' ').replace('[', ' ').replace(']', ' ').replace('{', ' ').replace('}', ' ').replace('<', ' ').replace('>', ' ').replace('~', ' ').replace(':', ' ').replace(';', ' ').replace('.', ' ').replace(',', ' ').replace('?', ' ').replace('+', ' ').replace('=', ' ').replace('|', ' ').replace('\\', ' ').replace('\n', ' ').replace('\r', ' ')
#     except:
#         pass
#     return word


var_cat = ['ODR_LIBELLE', 'TYPE_TRAVAIL',
           'SYSTEM_N1', 'SYSTEM_N2', 'SYSTEM_N3', 
           'SIG_ORGANE', 'SIG_CONTEXTE', 'SIG_OBS', 'LIGNE',
           'SIG_CONTEXTE']
for var in var_cat:
    ot_odr_df[var] = ot_odr_df[var].astype('category')


### PyAgrum
import pyAgrum as gum

rb_projet =  gum.BayesNet("Projet")

# Creation du réseau

def Create_noeud(nom_du_noeud, ot_odr_df):
    Nombre_element = ot_odr_df[nom_du_noeud].value_counts()
    va = gum.LabelizedVariable(nom_du_noeud, nom_du_noeud, len(Nombre_element))
    i = 0
    for liste in ot_odr_df[nom_du_noeud].unique():
        # liste = Delete_special_caractere(liste)
        try:
            va.changeLabel(i, str(liste))
        except gum.DuplicateElement as e:
            i -= 1
            print(f"Erreur de duplication dans le noeud '{nom_du_noeud}' pour la valeur : {liste}")
        i += 1
    return va

## Création des noeud
### Création du noeud de SIG_ORGANE

va_SIG_ORGANE = Create_noeud('SIG_ORGANE',ot_odr_df)

### Création du noeud de SIG_OBS
va_SIG_OBS = Create_noeud('SIG_OBS',ot_odr_df)

### Création du noeud de SYSTEM_N1
va_SYSTEM_N1 = Create_noeud('SYSTEM_N1',ot_odr_df)

### Création du noeud de SYSTEM_N2
va_SYSTEM_N2 = Create_noeud('SYSTEM_N2',ot_odr_df)

### Création du noeud de SYSTEM_N3
va_SYSTEM_N3 = Create_noeud('SYSTEM_N3',ot_odr_df)

### Création du noeud de TYPE_TRAVAIL
va_TYPE_TRAVAIL = Create_noeud('TYPE_TRAVAIL',ot_odr_df)

### Création du noeud de ODR_LIBELLE
va_ODR_LIBELLE = Create_noeud('ODR_LIBELLE',ot_odr_df)

### Ajout des noeuds
for va in [va_SIG_ORGANE,va_SYSTEM_N1,va_SYSTEM_N2,va_SYSTEM_N3,va_TYPE_TRAVAIL,va_ODR_LIBELLE,va_SIG_OBS]:
    rb_projet.add(va)


## Création des fixations

rb_projet.addArc("SIG_ORGANE","SYSTEM_N1")
rb_projet.addArc("SIG_OBS","SYSTEM_N1")

rb_projet.addArc("SYSTEM_N1","SYSTEM_N2")
rb_projet.addArc("SYSTEM_N2","SYSTEM_N3")

rb_projet.addArc("SYSTEM_N3","ODR_LIBELLE")

rb_projet.addArc("ODR_LIBELLE","TYPE_TRAVAIL")


### Apprentissage des LPC

import pyagrum_extra
rb_projet.fit_bis(ot_odr_df, verbose_mode=True)

rb_projet.cpt("SIG_OBS")
rb_projet.cpt("SYSTEM_N1")

pred_prob = rb_projet.predict_proba(ot_odr_df[["SIG_OBS"]].iloc[-1000:], var_target="SYSTEM_N1", show_progress=True)
print("Probabilité des prédictions : ")
print(pred_prob)

pred = rb_projet.predict(ot_odr_df[["SIG_OBS"]].iloc[-1000:], var_target="SYSTEM_N1", show_progress=True)
print("Prédictions : ")
print(pred)

import numpy as np

def afficher_probabilites_tableau(sig_organe, sig_obs, rb_projet):
    dictionnaire = {}
    colonnes = ot_odr_df['SYSTEM_N1'].unique()
    colonnes2 = ot_odr_df['SYSTEM_N2'].unique()
    colonnes3 = ot_odr_df['SYSTEM_N3'].unique()
    colonnes4 = ot_odr_df['ODR_LIBELLE'].unique()
    colonnes5 = ot_odr_df['TYPE_TRAVAIL'].unique()

    # Calculer la probabilité conditionnelle pour SYSTEM_N1
    proba_system_n1 = rb_projet.cpt("SYSTEM_N1")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs}]

    # Définir la valeur choisie pour SIG_ORGANE
    rb_projet.cpt("SIG_ORGANE")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs}] = 1.0

    # Calculer les probabilités pour SYSTEM_N2
    proba_system_n2 = np.dot(proba_system_n1, rb_projet.cpt("SYSTEM_N2")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs}])

    # Calculer les probabilités pour SYSTEM_N3
    proba_system_n3 = np.dot(proba_system_n2, rb_projet.cpt("SYSTEM_N3")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs}])

    # Calculer les probabilités pour ODR_LIBELLE
    proba_system_lib = np.dot(proba_system_n3, rb_projet.cpt("ODR_LIBELLE")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs}])

    # Calculer les probabilités pour TYPE_TRAVAIL
    proba_system_tra = np.dot(proba_system_lib, rb_projet.cpt("TYPE_TRAVAIL")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs}])

    # Créer un dictionnaire avec l'association nom de colonne et probabilité
    dictionnaire = {
        'SYSTEM_N1': dict(zip(colonnes, proba_system_n1)),
        'SYSTEM_N2': dict(zip(colonnes2, proba_system_n2)),
        'SYSTEM_N3': dict(zip(colonnes3, proba_system_n3)),
        'ODR_LIBELLE': dict(zip(colonnes4, proba_system_lib)),
        'TYPE_TRAVAIL': dict(zip(colonnes5, proba_system_tra))
    }

    return dictionnaire

sig_organe_choisi = "ECLAIRAGE FEUX EXTERIEURS"
sig_obs_choisi = "CASSE"
# sig_obs_choisi = "NE FONCTIONNE PAS"

sss = afficher_probabilites_tableau(sig_organe_choisi, sig_obs_choisi, rb_projet)
sss['TYPE_TRAVAIL']
