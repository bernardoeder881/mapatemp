import os
import zipfile
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import fiona

# Habilitar o suporte de leitura e escrita para KML no fiona (usado pelo geopandas)
fiona.drvsupport.supported_drivers['KML'] = 'rw'

def gerar_mapa_severidade():
    csv_file = 'Temp Máx e Umi Mín.xlsx - Página1.csv'
    kmz_file = 'Cidades RJ.kmz'
    output_map = 'mapa_severidade_rj.png'

    # 1. Extração do ficheiro KML de dentro do pacote KMZ
    kml_extracted = 'doc.kml'
    with zipfile.ZipFile(kmz_file, 'r') as zip_ref:
        kml_files = [f for f in zip_ref.namelist() if f.endswith('.kml')]
        if kml_files:
            zip_ref.extract(kml_files[0], path='.')
            os.rename(kml_files[0], kml_extracted)
        else:
            raise FileNotFoundError("Ficheiro KML não encontrado no KMZ.")

    # 2. Carregamento da malha geográfica dos municípios do RJ
    gdf_municipios = gpd.read_file(kml_extracted, driver='KML')
    gdf_municipios = gdf_municipios.to_crs(epsg=4326)

    # 3. Processamento direto da folha de cálculo (CSV)
    df_dados = pd.read_csv(csv_file)
    
    # Limpeza e separação das coordenadas (Latitude e Longitude)
    df_dados[['Latitude', 'Longitude']] = df_dados['Coordenadas'].str.replace('"', '').str.split(',', expand=True).astype(float)

    # Criação da estrutura espacial para as estações
    geometry = [Point(lon, lat) for lat, lon in zip(df_dados['Latitude'], df_dados['Longitude'])]
    gdf_estacoes = gpd.GeoDataFrame(df_dados, geometry=geometry, crs="EPSG:4326")

    # 4. Definição da paleta de cores para a legenda
    colors = {
        'Muito Baixo': '#2ECC71', # Verde
        'Baixo': '#3498DB',       # Azul
        'Moderado': '#F1C40F',    # Amarelo
        'Alto': '#E67E22',        # Laranja
        'Muito Alto': '#E74C3C',  # Vermelho
        'Crítico': '#922B21'      # Vermelho Escuro
    }

    # 5. Renderização Cartográfica
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
    
    # Fundo do estado (Limites)
    gdf_municipios.plot(ax=ax, color='#EAECEE', edgecolor='#BDC3C7', linewidth=0.8, alpha=0.7)

    # Plotagem dos pontos sobrepostos com categorização
    for nivel, group in gdf_estacoes.groupby('Nível de Severidade Meteorológica'):
        group.plot(
            ax=ax, 
            color=colors.get(nivel, '#7F8C8D'), 
            markersize=80, 
            edgecolor='black', 
            linewidth=1,
            label=f'{nivel}'
        )

    # Formatação visual (Títulos e Eixos)
    ax.set_title('Monitorização Meteorológica - Nível de Severidade', fontsize=16, pad=20, fontweight='bold')
    ax.set_xlabel('Longitude', fontsize=10)
    ax.set_ylabel('Latitude', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.3)

    # Construção da Legenda (replicando o estilo partilhado)
    ax.legend(title="Severidade", loc="lower right", frameon=True, facecolor='white', edgecolor='black', title_fontsize=12, fontsize=10)

    # Salvar a imagem com alta resolução
    plt.tight_layout()
    plt.savefig(output_map, bbox_inches='tight')
    plt.close()
    
    # Limpeza dos ficheiros temporários
    if os.path.exists(kml_extracted):
        os.remove(kml_extracted)
        
    print(f"Artefato gerado com sucesso: {output_map}")

# Executar a função
gerar_mapa_severidade()
