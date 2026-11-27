"""
SAE 15 Mais que fait l'ANFR ?
Interactive map of the ANFR radio installations, with a Tkinter window to choose the filters
Put the data and ref folders given by the teacher next to this file, then run it
"""

import importlib
import sys

missing = []
for module in ("pandas", "folium"):
    try:
        importlib.import_module(module)
    except ImportError:
        missing.append(module)
if missing:
    print("Missing module(s):", ", ".join(missing), "- see requirements.txt to know what to install")
    sys.exit(1)

import html
import webbrowser
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import pandas as pd
import folium
from folium.plugins import FastMarkerCluster, HeatMap

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "resultats"

MAX_POINTS = 150000 # maximum number of displayed points to avoid lag
MOBILE_OPERATORS = ["ORANGE", "SFR", "BOUYGUES TELECOM", "FREE MOBILE"]
OPERATOR_COLORS = {"ORANGE": "#f47230", "SFR": "#ec4647", "BOUYGUES TELECOM": "#257de0",
                   "FREE MOBILE": "#6a4ce2"}
OTHER_COLOR = "#666666"

IGN_URL = ("https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0"
           "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&STYLE=normal&TILEMATRIXSET=PM"
           "&FORMAT=image/png&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}")

FAMILIES = [
    ("GSM R", "GSM-R (rail)"), ("GSM", "2G"), ("UMTS", "3G"), ("LTE", "4G"), ("5G NR", "5G"),
    ("FM", "Radio FM"), ("RDF DVB-T", "TNT"), ("RDF T-DAB", "Radio numérique (DAB+)"),
    ("FH", "Faisceau hertzien"), ("PMR", "PMR (radio pro)"), ("TETRA", "PMR (radio pro)"),
    ("SAT", "Satellite"), ("BLR", "Boucle locale radio"),
]
# Emitter label prefix => technology family
TECH_CHOICES = ["Toutes", "2G", "3G", "4G", "5G", "Radio FM", "TNT", "Faisceau hertzien",
                "GSM-R (rail)", "PMR (radio pro)"]
# Technologies the user can choose in the window
REGIONS = {
    "Auvergne-Rhône-Alpes": "01 03 07 15 26 38 42 43 63 69 73 74",
    "Bourgogne-Franche-Comté": "21 25 39 58 70 71 89 90",
    "Bretagne": "22 29 35 56",
    "Centre-Val de Loire": "18 28 36 37 41 45",
    "Corse": "20",
    "Grand Est": "08 10 51 52 54 55 57 67 68 88",
    "Hauts-de-France": "02 59 60 62 80",
    "Île-de-France": "75 77 78 91 92 93 94 95",
    "Normandie": "14 27 50 61 76",
    "Nouvelle-Aquitaine": "16 17 19 23 24 33 40 47 64 79 86 87",
    "Occitanie": "09 11 12 30 31 32 34 46 48 65 66 81 82",
    "Pays de la Loire": "44 49 53 72 85",
    "Provence-Alpes-Côte d'Azur": "04 05 06 13 83 84",
}
# Departments of each region (used to find the region from the postcode)
DEP_TO_REGION = {dep: region for region, deps in REGIONS.items() for dep in deps.split()}


def find_file(name):
    """Search the script folder (then its parent in case of) for a data file, also inside zip files if not extracted
    Return (path, None) for a normal file or (zip_path, member) for a file inside a zip"""
    for folder in (PROJECT_DIR, PROJECT_DIR.parent):
        for path in folder.rglob("*"):
            if "__MACOSX" in path.parts:
                continue
            if path.name.lower() == name:
                return path, None
            if path.suffix.lower() == ".zip":
                with zipfile.ZipFile(path) as archive:
                    for member in archive.namelist():
                        if Path(member).name.lower() == name and "__MACOSX" not in member:
                            return path, member
    raise FileNotFoundError(f"{name} not found: put the teacher's data and ref folders (or zips) next to {Path(__file__).name}")


def read(name, columns=None):
    """Read one ';'-separated ANFR file into a DataFrame, everything as text
    keeps the leading zeros of the IDs, helped by AI because the files were hard to reach to"""
    path, member = find_file(name)
    if member is None:
        return pd.read_csv(path, sep=";", dtype=str, usecols=columns)
    with zipfile.ZipFile(path) as archive, archive.open(member) as file:
        return pd.read_csv(file, sep=";", dtype=str, usecols=columns)


def family(system):
    """Return the technology family of an emitter label ex:'LTE 800' -> '4G'."""
    for prefix, fam in FAMILIES:
        if system.startswith(prefix):
            return fam
    return "Autre"


def dms_to_decimal(df, prefix, direction_col, negative_letter):
    """Convert degrees / minutes / seconds columns into decimal degrees
    negative for South or West and so it's more understandable by users"""
    value = (df[f"COR_NB_DG_{prefix}"].astype(float)
             + df[f"COR_NB_MN_{prefix}"].astype(float) / 60
             + df[f"COR_NB_SC_{prefix}"].astype(float) / 3600)
    return value.where(df[direction_col] != negative_letter, -value)


def year_of(dates):
    """Extract the year as a number from dd/mm/yyyy dates"""
    return pd.to_numeric(dates.str[-4:], errors="coerce")


def load_data():
    """Load the ANFR files once, clean them and join them into a main table"""
    support = read("sup_support.txt", ["SUP_ID", "STA_NM_ANFR", "NAT_ID", "COR_NB_DG_LAT", "COR_NB_MN_LAT",
                                       "COR_NB_SC_LAT", "COR_CD_NS_LAT", "COR_NB_DG_LON", "COR_NB_MN_LON",
                                       "COR_NB_SC_LON", "COR_CD_EW_LON", "SUP_NM_HAUT", "TPO_ID",
                                       "ADR_LB_LIEU", "ADR_LB_ADD1", "ADR_NM_CP"])
    station = read("sup_station.txt", ["STA_NM_ANFR", "ADM_ID", "DTE_EN_SERVICE"])
    emitter = read("sup_emetteur.txt", ["STA_NM_ANFR", "EMR_LB_SYSTEME", "EMR_DT_SERVICE"])
    operator_ref = read("sup_exploitant.txt")
    nature_ref = read("sup_nature.txt")

    support["lat"] = dms_to_decimal(support, "LAT", "COR_CD_NS_LAT", "S")
    support["lon"] = dms_to_decimal(support, "LON", "COR_CD_EW_LON", "W")
    postcode = support["ADR_NM_CP"].fillna("").str.zfill(5)
    overseas = postcode.str[:2].isin(["97", "98"])
    support["dep"] = postcode.str[:2].where(~overseas, postcode.str[:3])
    support["region"] = support["dep"].map(DEP_TO_REGION).fillna("Outre-mer et autres")
    support = support.merge(nature_ref, on="NAT_ID", how="left")
    support["adresse"] = (support["ADR_LB_ADD1"].fillna(support["ADR_LB_LIEU"]).fillna("")
                          .map(lambda a: html.escape(a.strip())))
    support = support.drop(columns=[c for c in support.columns if c.startswith("COR_")])

    station = station.merge(operator_ref, on="ADM_ID", how="left")
    station["exploitant"] = station["ADM_LB_NOM"].fillna("Inconnu")
    station["annee_station"] = year_of(station["DTE_EN_SERVICE"].fillna(""))

    emitter["famille"] = emitter["EMR_LB_SYSTEME"].fillna("").map(family)
    emitter["annee"] = year_of(emitter["EMR_DT_SERVICE"].fillna(""))

    station_tech = (emitter.groupby(["STA_NM_ANFR", "famille"])["annee"].min().reset_index())
    tech_text = (station_tech.groupby("STA_NM_ANFR")["famille"]
                 .agg(lambda f: ", ".join(sorted(f))).rename("technos").reset_index())

    base = (support.merge(station[["STA_NM_ANFR", "exploitant", "annee_station"]], on="STA_NM_ANFR")
                   .merge(tech_text, on="STA_NM_ANFR", how="left"))
    base["technos"] = base["technos"].fillna("")

    return {"base": base, "station": station, "station_tech": station_tech}


def apply_filters(data, zone, operators, techno, year_max, sup_id=""):
    """Return the rows of the main table above that match the zone, operators,
    technology and year chosen by the user in big, the filters chosen"""
    base = data["base"]
    if sup_id.strip():
        return base[base["SUP_ID"] == sup_id.strip()]
    mask = pd.Series(True, index=base.index)

    if zone.startswith("Région : "):
        mask &= base["region"] == zone.removeprefix("Région : ")
    elif zone.startswith("Département : "):
        mask &= base["dep"] == zone.removeprefix("Département : ")

    if operators:
        mask &= base["exploitant"].isin(operators)

    tech = data["station_tech"]
    tech = tech[tech["annee"].isna() | (tech["annee"] <= year_max)]
    if techno != "Toutes":
        tech = tech[tech["famille"] == techno]
    mask &= base["STA_NM_ANFR"].isin(tech["STA_NM_ANFR"])

    return base[mask]


def build_map(rows, zone, show_heat, show_deps, show_points):
    """Build the folium map from the filtered rows and save it in carte.html
    Return the path of the file and a message for the user for it to be understandable"""
    folium_map = folium.Map(location=[46.6, 2.4], zoom_start=6, tiles=None,
                            control_scale=True, prefer_canvas=True)
    folium.TileLayer(tiles=IGN_URL, attr="IGN-F / Géoplateforme", name="Plan IGN", max_zoom=19).add_to(folium_map)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap", show=False).add_to(folium_map)

    supports = rows.drop_duplicates("SUP_ID")
    message = f"{len(supports)} supports affichés."

    if show_heat and not supports.empty:
        if len(supports) > 30000:
            step = 0.02
            heat = (supports.assign(glat=(supports["lat"] / step).round() * step,
                                    glon=(supports["lon"] / step).round() * step)
                    .groupby(["glat", "glon"]).size().reset_index(name="n"))
            heat_points = heat[["glat", "glon", "n"]].values.tolist()
        else:
            heat_points = supports[["lat", "lon"]].values.tolist()
        layer = folium.FeatureGroup(name=f"Densité des supports ({len(supports)})")
        HeatMap(heat_points, radius=14, blur=12, max_zoom=10, min_opacity=0.3).add_to(layer)
        layer.add_to(folium_map)

    if show_deps:
        layer = folium.FeatureGroup(name="Bilan par département")
        for dep, group in rows.groupby("dep"):
            n_supports = group["SUP_ID"].nunique()
            per_op = group.groupby("exploitant")["SUP_ID"].nunique().sort_values(ascending=False).head(6)
            n_5g = group.loc[group["technos"].str.contains("5G"), "SUP_ID"].nunique()
            text = (f"<b>Département {dep}</b> ({group['region'].iloc[0]})<br>{n_supports} supports<br>"
                    f"dont {n_5g} avec de la 5G<br><br><i>Principaux exploitants :</i><br>"
                    + "<br>".join(f"{html.escape(op)} : {n}" for op, n in per_op.items()))
            folium.CircleMarker(
                location=[group["lat"].median(), group["lon"].median()],
                radius=5 + n_supports ** 0.5 / 4, color="#257de0", weight=2,
                fill=True, fill_opacity=0.35,
                tooltip=f"Dép. {dep} : {n_supports} supports",
                popup=folium.Popup(text, max_width=260),
            ).add_to(layer)
        layer.add_to(folium_map)

    if show_points:
        points = rows.drop_duplicates(["SUP_ID", "exploitant"])
        if len(points) > MAX_POINTS:
            message += (f" Détail des supports non affiché ({len(points)} points > {MAX_POINTS}) :"
                        " choisis une région, un département ou moins d'exploitants.")
        else:
            callback = """function (row) {
                var m = L.circleMarker(new L.LatLng(row[0], row[1]),
                    {radius: 6, color: row[3], weight: 2, fillOpacity: 0.7});
                m.bindPopup(row[2]); m.bindTooltip(row[4]); return m; }"""
            for operator, group in points.groupby("exploitant"):
                color = OPERATOR_COLORS.get(operator, OTHER_COLOR)
                data = [[r.lat, r.lon,
                         f"<b>{html.escape(operator)}</b><br>{r.adresse}<br>{r.ADR_NM_CP}"
                         f"<br>Support : {r.NAT_LB_NOM}, {r.SUP_NM_HAUT} m"
                         f"<br>Technologies : {r.technos or 'non renseignées'}"
                         f"<br>En service depuis : {'' if pd.isna(r.annee_station) else int(r.annee_station)}",
                         color, operator]
                        for r in group.itertuples()]
                layer = folium.FeatureGroup(name=f"{operator} ({len(group)})")
                FastMarkerCluster(data, callback=callback).add_to(layer)
                layer.add_to(folium_map)

    if zone != "France entière" and not supports.empty:
        folium_map.fit_bounds([[supports["lat"].min(), supports["lon"].min()],
                               [supports["lat"].max(), supports["lon"].max()]])

    folium.LayerControl(collapsed=False).add_to(folium_map)
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "carte.html"
    folium_map.save(path)
    return path, message


class RemoteControl(tk.Tk):

    """Tkinter window used as a remote control to choose the filters and generate the map."""
    def __init__(self):
        """Create the window and start loading the data."""
        super().__init__()
        self.title("SAE 15 - carte ANFR")
        self.status = tk.Label(self, text="Chargement des données...")
        self.status.pack()
        self.after(200, self.load)

    def load(self):
        """Load the data, then build the widgets shows an error if the files are missing"""
        try:
            self.data = load_data()
        except FileNotFoundError as error:
            messagebox.showerror("Erreur", str(error))
            self.destroy()
            return
        self.status.destroy()
        self.build_widgets()
        self.update_counter()

    def build_widgets(self):
        """Create the filter widgets: zone, operators, technology, year, layers and button."""
        base = self.data["base"]

        tk.Label(self, text="Zone :").pack(anchor="w")
        self.zones = (["France entière"] + [f"Région : {r}" for r in sorted(base["region"].unique())]
                      + [f"Département : {d}" for d in sorted(base["dep"].unique()) if d.strip("0")])
        self.zone_list = tk.Listbox(self, height=6, width=40, exportselection=False)
        for zone in self.zones:
            self.zone_list.insert("end", zone)
        self.zone_list.selection_set(self.zones.index("Région : Normandie"))
        self.zone_list.see(self.zones.index("Région : Normandie"))
        self.zone_list.pack(fill="x")
        self.zone_list.bind("<<ListboxSelect>>", lambda e: self.update_counter())

        tk.Label(self, text="Exploitants (ctrl + clic) :").pack(anchor="w")
        self.operator_names = self.data["station"]["exploitant"].value_counts().head(30).index.tolist()
        self.operator_list = tk.Listbox(self, selectmode="extended", height=6, exportselection=False)
        for i, name in enumerate(self.operator_names):
            self.operator_list.insert("end", name)
            if name in MOBILE_OPERATORS:
                self.operator_list.selection_set(i)
        self.operator_list.pack(fill="x")
        self.operator_list.bind("<<ListboxSelect>>", lambda e: self.update_counter())

        tk.Label(self, text="Technologie :").pack(anchor="w")
        self.techno = tk.StringVar(value="Toutes")
        tk.OptionMenu(self, self.techno, *TECH_CHOICES, command=lambda v: self.update_counter()).pack(anchor="w")

        tk.Label(self, text="Année :").pack(anchor="w")
        self.year = tk.IntVar(value=2026)
        tk.Scale(self, from_=1995, to=2026, orient="horizontal", variable=self.year,
                 command=lambda v: self.update_counter()).pack(fill="x")

        tk.Label(self, text="SUP_ID (optionnel) :").pack(anchor="w")
        self.sup_id = tk.Entry(self)
        self.sup_id.pack(fill="x")
        self.sup_id.bind("<KeyRelease>", lambda e: self.update_counter())

        self.show_heat = tk.BooleanVar(value=False)
        self.show_deps = tk.BooleanVar(value=True)
        self.show_points = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text="Heatmap", variable=self.show_heat).pack(anchor="w")
        tk.Checkbutton(self, text="Bilan par département", variable=self.show_deps).pack(anchor="w")
        tk.Checkbutton(self, text="Supports", variable=self.show_points).pack(anchor="w")

        self.counter = tk.Label(self, text="")
        self.counter.pack(anchor="w")
        tk.Button(self, text="Générer la carte", command=self.open_map).pack()
        self.message = tk.Label(self, text="", wraplength=300, justify="left")
        self.message.pack(anchor="w")

    def selected_zone(self):
        """Return the zone selected in the list France entière by default"""
        selection = self.zone_list.curselection()
        return self.zones[selection[0]] if selection else "France entière"

    def selected_operators(self):
        """Return the names of the selected operators."""
        return [self.operator_names[i] for i in self.operator_list.curselection()]

    def current_rows(self):
        """Return the data matching the current filters."""
        return apply_filters(self.data, self.selected_zone(), self.selected_operators(),
                             self.techno.get(), self.year.get(), self.sup_id.get())

    def update_counter(self):
        """Update the number of supports matching the filters."""
        rows = self.current_rows()
        self.counter.config(text=f"{rows['SUP_ID'].nunique()} supports")

    def open_map(self):
        """Generate the map with the current filters and open it in the browser."""
        rows = self.current_rows()
        if rows.empty:
            self.message.config(text="Aucun support avec ces filtres.")
            return
        self.message.config(text="Génération...")
        self.update_idletasks()
        zone = "SUP_ID" if self.sup_id.get().strip() else self.selected_zone()
        path, text = build_map(rows, zone, self.show_heat.get(),
                               self.show_deps.get(), self.show_points.get())
        webbrowser.open(path.resolve().as_uri())
        self.message.config(text=text)


if __name__ == "__main__":
    RemoteControl().mainloop()
