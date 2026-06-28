import os
import zipfile
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
csv_file = 'Temp Máx e Umi Mín.xlsx - Página1.csv'
kmz_file = 'Cidades RJ.kmz'
output_map = 'mapa_severidade_rj.png'

# --- 2. TRATAMENTO DO ARQUIVO KMZ (Extração do KML) ---
print("Extraindo dados geográficos do KMZ...")
kml_extracted = 'doc.kml'
with zipfile.ZipFile(kmz_file, 'r') as zip_ref:
    # Localiza o arquivo .kml dentro do pacote KMZ
    kml_files = [f for f in zip_ref.namelist() if f.endswith('.kml')]
    if kml_files:
        zip_ref.extract(kml_files[0], path='.')
        os.rename(kml_files[0], kml_extracted)
    else:
        raise FileNotFoundError("Nenhum arquivo KML encontrado dentro do KMZ.")

# Habilita o suporte a KML no fiona/geopandas
gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
gdf_municipios = gpd.read_file(kml_extracted, driver='KML')

# --- 3. PROCESSAMENTO DOS DADOS DA TABELA (CSV) ---
print("Processando dados meteorológicos...")
df_dados = pd.read_csv(csv_file)

# Conversão da coluna de coordenadas texto "-21.714722, -41.343611" em Latitude e Longitude numéricas
df_dados[['Latitude', 'Longitude']] = df_dados['Coordenadas'].str.split(',', expand=True).astype(float)

# Criação do GeoDataFrame de pontos (Estações Meteorológicas)
geometry = [Point(lon, lat) for lat, lon in zip(df_dados['Latitude'], df_dados['Longitude'])]
gdf_estacoes = gpd.GeoDataFrame(df_dados, geometry=geometry, crs="EPSG:4326")

# Garantir que a malha municipal do KMZ use o mesmo sistema de coordenadas geográficas
gdf_municipios = gdf_municipios.to_crs(epsg=4326)

# --- 4. MAPEAMENTO DE CORES PARA A LEGENDA ---
colors = {
    'Muito Baixo': '#2ECC71',
    'Baixo': '#3498DB',
    'Moderado': '#F1C40F',
    'Alto': '#E67E22',
    'Muito Alto': '#E74C3C',
    'Crítico': '#922B21'
}

# Adiciona a coluna de cor baseada no nível de severidade
gdf_estacoes['cor'] = gdf_estacoes['Nível de Severidade Meteorológica'].map(colors).fillna('#7F8C8D')

# --- 5. RENDERIZAÇÃO DO MAPA GEORREFERENCIADO ---
print("Gerando o mapa final...")
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)

# Plot da base geográfica dos municípios (KMZ)
gdf_municipios.plot(ax=ax, color='#EAECEE', edgecolor='#BDC3C7', linewidth=0.5, label='Limites Municipais')

# Plot dos pontos das estações meteorológicas coloridos por severidade
for nivel, group in gdf_estacoes.groupby('Nível de Severidade Meteorológica'):
    group.plot(
        ax=ax, 
        color=colors.get(nivel, '#7F8C8D'), 
        markersize=60, 
        edgecolor='black', 
        linewidth=0.8,
        label=f'Severidade: {nivel}'
    )

# Configurações estéticas e elementos cartográficos
ax.set_title('Mapa de Monitoramento Meteorológico - Estado do RJ\nDistribuição de Severidade por Estação', fontsize=14, pad=15, fontweight='bold')
ax.set_xlabel('Longitude (WGS84)', fontsize=10)
ax.set_ylabel('Latitude (WGS84)', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.5)

# Inserção da legenda estruturada
ax.legend(title="Legenda de Severidade", loc="lower right", frameon=True, facecolor='white', edgecolor='#BDC3C7')

# Salvar o mapa gerado
plt.tight_layout()
plt.savefig(output_map, bbox_inches='tight')
print(f"Mapa gerado com sucesso e salvo como: {output_map}")

# Limpeza do arquivo temporário extraído
if os.path.exists(kml_extracted):
    os.remove(kml_extracted)
