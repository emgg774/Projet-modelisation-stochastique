import pyAgrum as gum
import pandas as pd
import os
# import pyAgrum.lib.ipython as gnb 
import numpy as np

class Projet:
    def __init__(self):
        # Chargement des données à partir des fichiers CSV
        self.ot_odr_df = pd.read_csv(os.path.join(".", "OT_ODR.csv.bz2"), compression="bz2", sep=";")
        self.equipements_df = pd.read_csv(os.path.join(".", 'EQUIPEMENTS.csv'), sep=";")
        self.ot_odr_df = pd.merge(self.ot_odr_df, self.equipements_df, on="EQU_ID", how="inner")
        self.rb_projet =  gum.BayesNet("Projet")
        
        # Variables catégorielles
        var_cat = ['ODR_LIBELLE', 'TYPE_TRAVAIL',
           'SYSTEM_N1', 'SYSTEM_N2', 'SYSTEM_N3', 
           'SIG_ORGANE', 'SIG_CONTEXTE', 'SIG_OBS', "CONSTRUCTEUR"
           ]
        
        # Conversion des variables en catégories
        for var in var_cat:
            self.ot_odr_df[var] = self.ot_odr_df[var].astype('category')

        def Create_noeud(nom_du_noeud, ot_odr_df):
            # Création d'une variable pour le noeud avec les étiquettes correspondantes
            Nombre_element = ot_odr_df[nom_du_noeud].value_counts()
            va = gum.LabelizedVariable(nom_du_noeud, nom_du_noeud, len(Nombre_element))
            i = 0
            for liste in ot_odr_df[nom_du_noeud].unique():
                try:
                    va.changeLabel(i, str(liste))
                except gum.DuplicateElement as e:
                    # En cas de duplication d'une étiquette, ajuster l'indice et afficher un message d'erreur
                    i -= 1
                    print(f"Erreur de duplication dans le noeud '{nom_du_noeud}' pour la valeur : {liste}")
                i += 1
            return va
        
        # Création des variables pour les noeuds du réseau bayésien
        va_SIG_ORGANE = Create_noeud('SIG_ORGANE',self.ot_odr_df)
        va_SIG_OBS = Create_noeud('SIG_OBS',self.ot_odr_df)
        va_CONSTRUCTEUR = Create_noeud('CONSTRUCTEUR',self.ot_odr_df)
        va_SYSTEM_N1 = Create_noeud('SYSTEM_N1',self.ot_odr_df)
        va_SYSTEM_N2 = Create_noeud('SYSTEM_N2',self.ot_odr_df)
        va_SYSTEM_N3 = Create_noeud('SYSTEM_N3',self.ot_odr_df)
        va_TYPE_TRAVAIL = Create_noeud('TYPE_TRAVAIL',self.ot_odr_df)
        va_ODR_LIBELLE = Create_noeud('ODR_LIBELLE',self.ot_odr_df)

        # Ajout des variables au réseau bayésien
        for va in [va_SIG_ORGANE,va_SYSTEM_N1,va_SYSTEM_N2,va_SYSTEM_N3,va_TYPE_TRAVAIL,va_ODR_LIBELLE,va_SIG_OBS,va_CONSTRUCTEUR]:
            self.rb_projet.add(va)
            
        # Définition des arcs entre les noeuds
        self.rb_projet.addArc("SIG_ORGANE","SYSTEM_N1")
        self.rb_projet.addArc("SIG_OBS","SYSTEM_N1")
        self.rb_projet.addArc("CONSTRUCTEUR","SYSTEM_N1")

        self.rb_projet.addArc("SYSTEM_N1","SYSTEM_N2")
        self.rb_projet.addArc("SYSTEM_N2","SYSTEM_N3")

        self.rb_projet.addArc("SYSTEM_N3","ODR_LIBELLE")

        self.rb_projet.addArc("ODR_LIBELLE","TYPE_TRAVAIL")

        def Create_Probabilite(df,element,all_element):
            longueur_df = len(df)
            count_element = []
            for liste in all_element:
                if liste in df[element].unique():
                    count_element.append(len(df.loc[df[element] == liste]) / longueur_df)
                else: # On met un 0 si le champ n'est pas remplit, si la probabilité n'existe pas
                    count_element.append(0)
            total_prob = sum(count_element)
            if total_prob == 0:
                return [1/len(count_element)]*len(count_element)
                
            return count_element
        
        # Calcul des probabilités conditionnelles pour chaque variable
        self.rb_projet.cpt("SIG_ORGANE")[:] = Create_Probabilite(self.ot_odr_df,"SIG_ORGANE",self.ot_odr_df["SIG_ORGANE"].unique())
        self.rb_projet.cpt("SIG_OBS")[:] = Create_Probabilite(self.ot_odr_df,"SIG_OBS",self.ot_odr_df["SIG_OBS"].unique())
        self.rb_projet.cpt("CONSTRUCTEUR")[:] = Create_Probabilite(self.ot_odr_df,"CONSTRUCTEUR",self.ot_odr_df["CONSTRUCTEUR"].unique())

        for sig_organe in self.ot_odr_df['SIG_ORGANE'].unique():
            ot_odf_sig_organe = self.ot_odr_df.loc[self.ot_odr_df['SIG_ORGANE'] == sig_organe]
            
            for sig_obs in self.ot_odr_df['SIG_OBS'].unique():
                ot_odf_sig_obs = ot_odf_sig_organe.loc[ot_odf_sig_organe['SIG_OBS'] == sig_obs]

                for sig_cons in self.ot_odr_df['CONSTRUCTEUR'].unique():
                    ot_odf_cons = ot_odf_sig_obs.loc[ot_odf_sig_obs['CONSTRUCTEUR'] == sig_cons]

                    self.rb_projet.cpt("SYSTEM_N1")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs, "CONSTRUCTEUR": sig_cons}] = Create_Probabilite(ot_odf_cons, "SYSTEM_N1", self.ot_odr_df["SYSTEM_N1"].unique())

        for liste_N1 in self.ot_odr_df['SYSTEM_N1'].unique():
            ot_odf_SYSTEM_N1 = self.ot_odr_df.loc[self.ot_odr_df['SYSTEM_N1'] == liste_N1]

            self.rb_projet.cpt("SYSTEM_N2")[{"SYSTEM_N1":liste_N1}] = Create_Probabilite(ot_odf_SYSTEM_N1,"SYSTEM_N2",self.ot_odr_df["SYSTEM_N2"].unique())

        for liste_N2 in self.ot_odr_df['SYSTEM_N2'].unique():
            ot_odf_SYSTEM_N2 = self.ot_odr_df.loc[self.ot_odr_df['SYSTEM_N2'] == liste_N2]
            self.rb_projet.cpt("SYSTEM_N3")[{"SYSTEM_N2":liste_N2}] = Create_Probabilite(ot_odf_SYSTEM_N2,"SYSTEM_N3",self.ot_odr_df["SYSTEM_N3"].unique())
        
        for liste_N3 in self.ot_odr_df['SYSTEM_N3'].unique():
            ot_odf_SYSTEM_N3 = self.ot_odr_df.loc[self.ot_odr_df['SYSTEM_N3'] == liste_N3]
            self.rb_projet.cpt("ODR_LIBELLE")[{"SYSTEM_N3":liste_N3}] = Create_Probabilite(ot_odf_SYSTEM_N3,"ODR_LIBELLE",self.ot_odr_df["ODR_LIBELLE"].unique())

        for liste_ODR_LIBELLE in self.ot_odr_df['ODR_LIBELLE'].unique():
            ot_odf_ODR_LIBELLE = self.ot_odr_df.loc[self.ot_odr_df['ODR_LIBELLE'] == liste_ODR_LIBELLE]
            self.rb_projet.cpt("TYPE_TRAVAIL")[{"ODR_LIBELLE":liste_ODR_LIBELLE}] = Create_Probabilite(ot_odf_ODR_LIBELLE,"TYPE_TRAVAIL",self.ot_odr_df["TYPE_TRAVAIL"].unique())

    def Affichage_rb_projet(self):
        gnb.showBN(self.rb_projet)
    

    def afficher_probabilites_tableau(self,sig_organe, sig_obs, sig_cons):
        dictionnaire = {}
        colonnes = self.ot_odr_df['SYSTEM_N1'].unique()
        colonnes2 = self.ot_odr_df['SYSTEM_N2'].unique()
        colonnes3 = self.ot_odr_df['SYSTEM_N3'].unique()
        colonnes4 = self.ot_odr_df['ODR_LIBELLE'].unique()
        colonnes5 = self.ot_odr_df['TYPE_TRAVAIL'].unique()

        # Calculer la probabilité conditionnelle pour SYSTEM_N1
        proba_system_n1 = self.rb_projet.cpt("SYSTEM_N1")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs, "CONSTRUCTEUR": sig_cons}]

        # Définir la valeur choisie pour SIG_ORGANE
        self.rb_projet.cpt("SIG_ORGANE")[{"SIG_ORGANE": sig_organe}] = 1.0
        self.rb_projet.cpt("SIG_OBS")[{"SIG_OBS": sig_obs}] = 1.0
        self.rb_projet.cpt("CONSTRUCTEUR")[{"CONSTRUCTEUR": sig_cons}] = 1.0

        # Calculer les probabilités pour SYSTEM_N2
        proba_system_n2 = np.dot(proba_system_n1, self.rb_projet.cpt("SYSTEM_N2")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs, "CONSTRUCTEUR": sig_cons}])

        # Calculer les probabilités pour SYSTEM_N3
        proba_system_n3 = np.dot(proba_system_n2, self.rb_projet.cpt("SYSTEM_N3")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs, "CONSTRUCTEUR": sig_cons}])

        # Calculer les probabilités pour ODR_LIBELLE
        proba_system_lib = np.dot(proba_system_n3, self.rb_projet.cpt("ODR_LIBELLE")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs, "CONSTRUCTEUR": sig_cons}])

        # Calculer les probabilités pour TYPE_TRAVAIL
        proba_system_tra = np.dot(proba_system_lib, self.rb_projet.cpt("TYPE_TRAVAIL")[{"SIG_ORGANE": sig_organe, "SIG_OBS": sig_obs, "CONSTRUCTEUR": sig_cons}])

        # Créer un dictionnaire avec l'association nom de colonne et probabilité
        dictionnaire = {
            'SYSTEM_N1': dict(zip(colonnes, proba_system_n1)),
            'SYSTEM_N2': dict(zip(colonnes2, proba_system_n2)),
            'SYSTEM_N3': dict(zip(colonnes3, proba_system_n3)),
            'ODR_LIBELLE': dict(zip(colonnes4, proba_system_lib)),
            'TYPE_TRAVAIL': dict(zip(colonnes5, proba_system_tra))
        }

        return dictionnaire
    
projet =Projet()

print(projet.afficher_probabilites_tableau("ECLAIRAGE FEUX EXTERIEURS","CASSE","C007"))