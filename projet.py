import pandas as pd
import os
import pyAgrum as gum # La librairie pyAgrum

# Vérification des versions
{
    "pyagrum": gum.__version__, 
}

ot_odr_filename = os.path.join(".", "OT_ODR.csv.bz2")
ot_odr_df = pd.read_csv(ot_odr_filename, compression="bz2", sep=";")

equipements_filename = os.path.join(".", 'EQUIPEMENTS.csv')
equipements_df = pd.read_csv(equipements_filename, sep=";")

resultat_df = pd.merge(ot_odr_df, equipements_df, on="EQU_ID", how="inner")

bn = gum.BayesNet("ProjetMS")
bn_SYG_ORGANE = gum.LabelizedVariable("SYS_ORGANE", "Signalement du conducteur sur la partie organe ?", len(resultat_df["SIG_ORGANE"].value_counts()))
bn_SYSTEM_N1 = gum.LabelizedVariable("SYSTEM_N1", "Identifiant de système de niveau 1 concerné par l'ODR ?", len(resultat_df["SYSTEM_N1"].value_counts()))


df_tmp = resultat_df["SIG_ORGANE"].value_counts()
df_tmp = df_tmp.reset_index()

for va in resultat_df["SIG_ORGANE"].value_counts():
  va.changeLabel(0, "non")
  va.changeLabel(1, "oui")