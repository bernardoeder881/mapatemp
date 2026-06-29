import os
import zipfile
import pandas as pd
import geopandas as gpd
import folium
import fiona
import streamlit as st
import streamlit.components.v1 as components

# Habilitar o suporte de leitura e escrita para KML/KMZ no fiona
fiona.drvsupport.supported_drivers['KML'] = 'rw'
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

def gerar_mapa_html():
    # 1. Resolver caminhos absolutos (evita erros de "File Not Found" na nuvem)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Nomes reais dos seus arquivos
    excel_file = os.path.join(current_dir, "Temp Máx e Umi Mín.xlsx")
    kmz_file = os.path.join(current_dir, "cidades.kmz")
    output_html = os.path.join(current_dir, "mapa_severidade_rj.html")

    # 2. Extração do KMZ
    kml_extracted = os.path.join(current_dir, 'doc.kml')
    with zipfile.ZipFile(kmz_file, 'r') as zip_ref:
        kml_files = [f for f in zip_ref.namelist() if f.endswith('.kml')]
        if kml_files:
            zip_ref.extract(kml_files[0], path=current_dir)
            # Renomeia para um nome padrão temporário
            os.rename(os.path.join(current_dir, kml_files[0]), kml_extracted)
        else:
            raise FileNotFoundError("Arquivo KML não encontrado dentro do KMZ.")

    # 3. Carregar limites municipais
    gdf_municipios = gpd.read_file(kml_extracted, driver='KML')

    # 4. Processar dados meteorológicos
    df = pd.read_excel(excel_file)
    
    # Separação das coordenadas (Latitude e Longitude)
    df[['Latitude', 'Longitude']] = df['Coordenadas'].str.replace('"', '').str.split(',', expand=True).astype(float)

    # 5. Criação do Mapa Base
    mapa = folium.Map(location=[-22.25, -42.50], zoom_start=8, tiles='cartodbpositron')

    # Adicionar a malha dos municípios
    folium.GeoJson(
        gdf_municipios,
        name="Limites Municipais",
        style_function=lambda feature: {
            'fillColor': '#EAECEE',
            'color': '#7F8C8D',
            'weight': 1,
            'fillOpacity': 0.3
        }
    ).add_to(mapa)

    # Dicionário de cores da legenda
    cores = {
        'Muito Baixo': '#2ECC71',
        'Baixo': '#3498DB',
        'Moderado': '#F1C40F',
        'Alto': '#E67E22',
        'Muito Alto': '#E74C3C',
        'Crítico': '#922B21'
    }

    # Adicionar os marcadores de cada estação ao mapa
    for idx, row in df.iterrows():
        nivel = str(row['Nível de Severidade Meteorológica']).strip()
        cor = cores.get(nivel, '#34495E') # Cor padrão caso não encontre
        
        # Estrutura do pop-up
        popup_html = f"""
        <div style="font-family: Arial; min-width: 150px;">
            <h4 style="margin-top: 0; color: #2C3E50;">{row['Estação']}</h4>
            <b>Temp. Máxima:</b> {row['Temperatura Máxima (°C)']} °C<br>
            <b>Umidade Mínima:</b> {row['Umidade Mínima (%)']}%<br>
            <b>Severidade:</b> <span style="color: {cor}; font-weight: bold;">{nivel}</span>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['Estação'],
            color='black',
            weight=1,
            fill=True,
            fill_color=cor,
            fill_opacity=0.9
        ).add_to(mapa)

    # Inserção da Legenda Flutuante via HTML customizado
    legenda_html = '''
    <div style="position: fixed; 
         bottom: 30px; right: 30px; width: 150px; height: 190px; 
         background-color: rgba(255, 255, 255, 0.9); border: 2px solid #BDC3C7; z-index:9999; font-size:12px; font-family: Arial;
         padding: 12px; border-radius: 8px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">
         <b style="font-size: 13px;">Severidade</b><br><br>
         <i style="background:#2ECC71; width: 14px; height: 14px; float: left; margin-right: 8px; border: 1px solid black; border-radius: 50%;"></i>Muito Baixo<br><br>
         <i style="background:#3498DB; width: 14px; height: 14px; float: left; margin-right: 8px; border: 1px solid black; border-radius: 50%;"></i>Baixo<br><br>
         <i style="background:#F1C40F; width: 14px; height: 14px; float: left; margin-right: 8px; border: 1px solid black; border-radius: 50%;"></i>Moderado<br><br>
         <i style="background:#E67E22; width: 14px; height: 14px; float: left; margin-right: 8px; border: 1px solid black; border-radius: 50%;"></i>Alto<br><br>
         <i style="background:#E74C3C; width: 14px; height: 14px; float: left; margin-right: 8px; border: 1px solid black; border-radius: 50%;"></i>Muito Alto<br><br>
         <i style="background:#922B21; width: 14px; height: 14px; float: left; margin-right: 8px; border: 1px solid black; border-radius: 50%;"></i>Crítico
    </div>
    '''
    mapa.get_root().html.add_child(folium.Element(legenda_html))

    mapa.save(output_html)
    
    # Limpeza do ficheiro KML temporário
    if os.path.exists(kml_extracted):
        os.remove(kml_extracted)

if __name__ == "__main__":
    # Configura a página para usar a largura total (opcional, mas fica melhor para mapas)
    st.set_page_config(layout="wide", page_title="Mapa de Severidade RJ")
    
    st.title("Mapa de Severidade Meteorológica - RJ")
    
    # Mostra um indicador visual enquanto o mapa é gerado nos bastidores
    with st.spinner("Processando dados e gerando o mapa..."):
        gerar_mapa_html()
    
    # Caminho onde o arquivo HTML foi salvo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_html = os.path.join(current_dir, "mapa_severidade_rj.html")
    
    # Lê o HTML e renderiza na tela
    with open(output_html, "r", encoding="utf-8") as f:
        mapa_html = f.read()
        
    components.html(mapa_html, height=700)
