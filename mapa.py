# Adicionar os marcadores de cada estação ao mapa
    for idx, row in df.iterrows():
        nivel = str(row['Nível de Severidade Meteorológica']).strip()
        cor = cores.get(nivel, '#34495E') # Cor padrão caso não encontre
        
        # Estrutura do pop-up (mantida para quando o usuário clicar no ponto)
        popup_html = f"""
        <div style="font-family: Arial; min-width: 150px;">
            <h4 style="margin-top: 0; color: #2C3E50;">{row['Estação']}</h4>
            <b>Temp. Máxima:</b> {row['Temperatura Máxima (°C)']} °C<br>
            <b>Umidade Mínima:</b> {row['Umidade Mínima (%)']}%<br>
            <b>Severidade:</b> <span style="color: {cor}; font-weight: bold;">{nivel}</span>
        </div>
        """
        
        # Estrutura do texto que ficará sempre visível no mapa
        texto_permanente = f"<div style='font-size: 11px; font-weight: bold; color: #2C3E50;'>{row['Temperatura Máxima (°C)']}°C | {row['Umidade Mínima (%)']}%</div>"
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8,
            popup=folium.Popup(popup_html, max_width=300),
            # O truque está aqui: permanent=True faz o texto ficar fixo na tela
            tooltip=folium.Tooltip(
                texto_permanente, 
                permanent=True, 
                direction='right', # Joga o texto para a direita do círculo
                opacity=0.8 # Deixa o fundo levemente transparente
            ),
            color='black',
            weight=1,
            fill=True,
            fill_color=cor,
            fill_opacity=0.9
        ).add_to(mapa)
