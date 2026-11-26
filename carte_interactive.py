# fichier brouillon a supprimer plus tard


import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
carte = folium.Map(location=[49.44, 1.10], zoom_start=10, tiles="OpenStreetMap", control_scale=True)

# Un cluster par opérateur : chaque cluster est aussi une couche dans le menu
cluster_orange = MarkerCluster(name="Orange").add_to(carte)   # name = texte affiché dans le menu
cluster_free = MarkerCluster(name="Free").add_to(carte)

# CircleMarker est plus léger que Marker quand il y a beaucoup de points
folium.CircleMarker(
    location=[49.44, 1.10],
    radius=5,             # taille du rond en pixels
    color="orange",       # couleur du contour
    fill=True,            # rond rempli ou vide
    fill_opacity=0.7,     # transparence du remplissage (0 = invisible, 1 = opaque)
    popup="Antenne Orange",
).add_to(cluster_orange)  # on ajoute le point AU CLUSTER, pas à la carte

folium.CircleMarker(
    location=[49.45, 1.08],
    radius=5,
    color="red",
    fill=True,
    fill_opacity=0.7,
    popup="Antenne Free",
).add_to(cluster_free)

points = [[49.44, 1.10], [49.45, 1.08], [49.43, 1.09]]

# plus tard pour pandas :
# df = pd.read_csv("antennes.csv")
# clusters = {"Orange": cluster_orange, "Free": cluster_free}
# for _, ligne in df.iterrows():
#     folium.CircleMarker(
#         location=[ligne["latitude"], ligne["longitude"]],
#         radius=5, fill=True, popup=ligne["operateur"],
#     ).add_to(clusters[ligne["operateur"]])



folium.LayerControl().add_to(carte)   # le menu à cocher, toujours en dernier

carte.save("map.html")  # fichier HTML à ouvrir dans un navigateur
