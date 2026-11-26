from pathlib import Path

import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap

DOSSIER_PROJET = Path(__file__).resolve().parent

DEPARTEMENT_DETAIL = "76"
FILTRE_TECHNO = None
OPERATEURS = {"ORANGE": "orange", "SFR": "red", "BOUYGUES TELECOM": "blue", "FREE MOBILE": "gray"}
URL_IGN = ("https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0"
           "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&STYLE=normal&TILEMATRIXSET=PM"
           "&FORMAT=image/png&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}")
GENERATIONS = {"GSM 900": "2G", "GSM 1800": "2G", "UMTS": "3G", "LTE": "4G", "5G NR": "5G"}


def trouver_fichier(nom):
    for dossier in (DOSSIER_PROJET, DOSSIER_PROJET.parent):
        for chemin in dossier.rglob(nom):
            if "__MACOSX" not in chemin.parts:
                return chemin
    raise FileNotFoundError(f"{nom} introuvable : mettre les dossiers data et ref dans {DOSSIER_PROJET}")


def lire(nom, colonnes=None):
    return pd.read_csv(trouver_fichier(nom), sep=";", dtype=str, usecols=colonnes)


def generation(systeme):
    for debut, gen in GENERATIONS.items():
        if systeme.startswith(debut):
            return gen
    return None


def charger_donnees():
    support = lire("sup_support.txt", ["SUP_ID", "STA_NM_ANFR", "COR_NB_DG_LAT", "COR_NB_MN_LAT",
                                       "COR_NB_SC_LAT", "COR_CD_NS_LAT", "COR_NB_DG_LON", "COR_NB_MN_LON",
                                       "COR_NB_SC_LON", "COR_CD_EW_LON", "SUP_NM_HAUT", "ADR_LB_ADD1", "ADR_NM_CP"])
    station = lire("sup_station.txt", ["STA_NM_ANFR", "ADM_ID"])
    exploitant = lire("sup_exploitant.txt")
    emetteur = lire("sup_emetteur.txt", ["STA_NM_ANFR", "EMR_LB_SYSTEME"])

    support["lat"] = (support["COR_NB_DG_LAT"].astype(float)
                      + support["COR_NB_MN_LAT"].astype(float) / 60
                      + support["COR_NB_SC_LAT"].astype(float) / 3600)
    support["lon"] = (support["COR_NB_DG_LON"].astype(float)
                      + support["COR_NB_MN_LON"].astype(float) / 60
                      + support["COR_NB_SC_LON"].astype(float) / 3600)
    support.loc[support["COR_CD_NS_LAT"] == "S", "lat"] *= -1
    support.loc[support["COR_CD_EW_LON"] == "W", "lon"] *= -1

    cp = support["ADR_NM_CP"].fillna("").str.zfill(5)
    support["departement"] = cp.str[:2].where(~cp.str.startswith("97"), cp.str[:3])

    emetteur["generation"] = emetteur["EMR_LB_SYSTEME"].fillna("").map(generation)
    technos = (emetteur.dropna(subset=["generation"])
               .groupby("STA_NM_ANFR")["generation"]
               .agg(lambda g: ", ".join(sorted(set(g))))
               .rename("technos")
               .reset_index())

    donnees = (support.merge(station, on="STA_NM_ANFR")
                      .merge(exploitant, on="ADM_ID")
                      .merge(technos, on="STA_NM_ANFR", how="left"))
    donnees["technos"] = donnees["technos"].fillna("")
    return support, donnees


def construire_carte(support, donnees):
    mobiles = donnees[donnees["ADM_LB_NOM"].isin(OPERATEURS)]
    if FILTRE_TECHNO:
        mobiles = mobiles[mobiles["technos"].str.contains(FILTRE_TECHNO)]

    carte = folium.Map(location=[46.6, 2.4], zoom_start=6, tiles=None, control_scale=True)
    folium.TileLayer(tiles=URL_IGN, attr="IGN-F / Géoplateforme", name="Plan IGN", max_zoom=19).add_to(carte)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(carte)

    points = support.drop_duplicates("SUP_ID")[["lat", "lon"]].values.tolist()
    calque_chaleur = folium.FeatureGroup(name=f"Densité de tous les supports ({len(points)})")
    HeatMap(points, radius=8, blur=10).add_to(calque_chaleur)
    calque_chaleur.add_to(carte)

    calque_dep = folium.FeatureGroup(name="Bilan par département")
    for dep, groupe in mobiles.groupby("departement"):
        nb_supports = groupe["SUP_ID"].nunique()
        par_operateur = groupe.groupby("ADM_LB_NOM")["SUP_ID"].nunique()
        nb_5g = groupe[groupe["technos"].str.contains("5G")]["SUP_ID"].nunique()
        texte = f"<b>Département {dep}</b><br>{nb_supports} supports mobiles<br>"
        texte += "<br>".join(f"{op} : {nb}" for op, nb in par_operateur.items())
        texte += f"<br>Supports avec de la 5G : {nb_5g}"
        folium.CircleMarker(
            location=[groupe["lat"].mean(), groupe["lon"].mean()],
            radius=4 + nb_supports ** 0.5 / 4,
            color="purple",
            fill=True,
            fill_opacity=0.5,
            tooltip=f"Département {dep} : {nb_supports} supports",
            popup=folium.Popup(texte, max_width=250),
        ).add_to(calque_dep)
    calque_dep.add_to(carte)

    detail = mobiles[mobiles["departement"] == DEPARTEMENT_DETAIL].drop_duplicates(["SUP_ID", "ADM_LB_NOM"])
    for operateur, groupe in detail.groupby("ADM_LB_NOM"):
        calque = folium.FeatureGroup(name=f"{operateur} – détail du {DEPARTEMENT_DETAIL} ({len(groupe)})")
        cluster = MarkerCluster().add_to(calque)
        for ligne in groupe.itertuples():
            adresse = ligne.ADR_LB_ADD1 if isinstance(ligne.ADR_LB_ADD1, str) else ""
            folium.CircleMarker(
                location=[ligne.lat, ligne.lon],
                radius=6,
                color=OPERATEURS[operateur],
                fill=True,
                fill_opacity=0.7,
                tooltip=operateur,
                popup=folium.Popup(f"<b>{operateur}</b><br>{adresse}<br>{ligne.ADR_NM_CP}"
                                   f"<br>Hauteur : {ligne.SUP_NM_HAUT} m<br>Technologies : {ligne.technos}",
                                   max_width=250),
            ).add_to(cluster)
        calque.add_to(carte)

    folium.LayerControl(collapsed=False).add_to(carte)
    fichier = DOSSIER_PROJET / "map.html"
    carte.save(fichier)
    return fichier


if __name__ == "__main__":
    support, donnees = charger_donnees()
    fichier = construire_carte(support, donnees)
    print("Carte enregistrée :", fichier)
