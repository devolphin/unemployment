import pandas as pd
import geopandas as gpd
import folium

dane_gus_ludnosc_file = 'ludno.csv'
dane_gus_bezrobocie_file = 'rynek.csv'

ludnosc_gus = pd.read_csv(dane_gus_ludnosc_file, delimiter=';')
ludnosc_gus.head()

ludnosc_gus = ludnosc_gus.iloc[:, 0:3]
ludnosc_gus.columns = ['TERYT', 'Nazwa', 'Ludnosc']
ludnosc_gus.head()

bezrobocie_gus = pd.read_csv(dane_gus_bezrobocie_file, delimiter=';')
bezrobocie_gus.head()

bezrobocie_gus = bezrobocie_gus.iloc[:, [0, 2]]
bezrobocie_gus.columns = ['TERYT', 'Bezrobotni']
bezrobocie_gus.head()

dane_gus = pd.merge(ludnosc_gus, bezrobocie_gus, how='inner', on='TERYT')

dane_gus['Stopa_bezrobocia'] = 100* dane_gus['Bezrobotni'] / dane_gus['Ludnosc']

dane_gus.sample(10)

mapa_woj = gpd.read_file('gis/WojewĘdztwa.shp')
print(mapa_woj.dtypes)

mapa_gmn = gpd.read_file('gis/Gminy.shp')
print(mapa_gmn.dtypes)

mapa_woj = mapa_woj[['JPT_KOD_JE', "geometry"]]

mapa_gmn = mapa_gmn[['JPT_KOD_JE', "geometry"]]
mapa_gmn.head()

dane_gus['TERYT_gmn'] = dane_gus.TERYT.apply(lambda x: '0'+str(x) if len(str(x)) < 7 else str(x))

dane_gus['TERYT_woj'] = dane_gus.TERYT_gmn.apply(lambda s: s[:2])

dane_gus.head()


dane_gus = dane_gus[dane_gus['TERYT'] != '0']
dane_gus_woj = dane_gus[dane_gus.TERYT_gmn.str[2:7] == '00000']
print(dane_gus_woj)

dane_gus_gmn = dane_gus[dane_gus.TERYT_gmn.str[4:7] != '000']
print(dane_gus_gmn)

dane_mapa_woj = pd.merge(mapa_woj, dane_gus_woj, how='left', left_on='JPT_KOD_JE', right_on='TERYT_woj')
print(dane_mapa_woj)

# gmina
print('\n\n--------please wait, downloading---------')
mapa_gmn.geometry = mapa_gmn.geometry.simplify(0.1)
gmn_geoPath = mapa_gmn.to_json()
mapa = folium.Map([52, 19], zoom_start=6)

folium.Choropleth(geo_data=gmn_geoPath,
                  data=dane_gus_gmn,
                  columns=['TERYT_gmn', 'Stopa_bezrobocia'],
                  key_on='feature.properties.JPT_KOD_JE',
                  fill_color='YlOrRd',
                  fill_opacity=1.5,
                  line_opacity=0.6,
                  legend_name="Stopa bezrobocia w gminie [%]").add_to(mapa)


mapa.save('mapa_bezrobocie_gmina.html', "Thanks, you downloaded.")

# województwo
mapa2 = folium.Map([52, 19], zoom_start=6)
mapa_woj.geometry = mapa_woj.geometry.simplify(0.1)
woj_geoPath = mapa_woj.to_json()

folium.Choropleth(geo_data=woj_geoPath,
                  data=dane_gus_woj,
                  columns=['TERYT_woj', 'Stopa_bezrobocia'],
                  key_on='feature.properties.JPT_KOD_JE',
                  fill_color='YlOrRd',
                  fill_opacity=1.5,
                  line_opacity=0.6,
                  legend_name="Stopa bezrobocia w województwie [%]").add_to(mapa2)


mapa2.save('mapa_bezrobocia_wojewodztwo.html', "Thanks, you downloaded.")


