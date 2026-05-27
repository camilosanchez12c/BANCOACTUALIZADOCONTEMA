# =============================================================================
# TAB 2: SERIES TEMPORALES
# =============================================================================
with tab2:
    st.markdown('<div class="section-header">Series Temporales de Tasas</div>', unsafe_allow_html=True)
    
    # Aplicar filtros del sidebar al historico
    hist_series = hist_filtrado.copy()
    hist_total_series = hist_total_filtrado.copy()
    
    # Determinar que bancos mostrar basado en el filtro principal
    bancos_historico = historico_df["banco"].unique().tolist()
    if banco_sel != "Todos":
        # Si hay filtro de banco, mostrar solo ese banco
        bancos_a_mostrar = [banco_sel]
    else:
        # Si no hay filtro, mostrar los 5 bancos con mas datos
        bancos_a_mostrar = bancos_historico[:5]
    
    # Grafico de lineas
    st.markdown("#### Evolucion Historica de Tasas por Banco")
    
    fig_series = go.Figure()
    
    # Linea del sistema (promedio total) - usando datos filtrados por mes
    if len(hist_total_series) > 0:
        fig_series.add_trace(go.Scatter(
            x=hist_total_series["mes"],
            y=hist_total_series["tasa_prom"],
            mode="lines",
            name="Promedio Sistema",
            line=dict(color="#94a3b8", width=3, dash="dash"),
            hovertemplate="<b>Sistema</b><br>Mes: %{x}<br>Tasa: %{y:.2f}%<extra></extra>"
        ))
    
    # Lineas por banco - usando filtros del sidebar
    colors = ["#38bdf8", "#818cf8", "#22c55e", "#f472b6", "#fbbf24", "#ef4444", "#c084fc", "#06b6d4"]
    
    for i, banco in enumerate(bancos_a_mostrar):
        banco_data = historico_df[historico_df["banco"] == banco].sort_values("mes")
        if len(banco_data) > 0:
            color = colors[i % len(colors)]
            fig_series.add_trace(go.Scatter(
                x=banco_data["mes"],
                y=banco_data["tasa_ponderada"],
                mode="lines+markers",
                name=banco,
                line=dict(color=color, width=2),
                marker=dict(size=6),
                hovertemplate=f"<b>{banco}</b><br>Mes: %{{x}}<br>Tasa: %{{y:.2f}}%<extra></extra>"
            ))
    
    fig_series.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(title="Mes", gridcolor="rgba(148, 163, 184, 0.1)", tickangle=-45),
        yaxis=dict(title="Tasa (%)", gridcolor="rgba(148, 163, 184, 0.1)"),
        margin=dict(l=0, r=0, t=50, b=50)
    )
    st.plotly_chart(fig_series, use_container_width=True)
    
    # Nota explicativa
    filtro_activo = ""
    if banco_sel != "Todos":
        filtro_activo = f" (Filtrado por: {banco_sel})"
    if mes_sel != "Todos":
        filtro_activo += f" (Mes: {mes_sel})"
   
    st.markdown(f"""
    <div class="info-box">
    <strong>Nota:</strong> El historico muestra la bajada real del sistema de 33.6% (oct-2023) a 22.9% (feb-2026). 
    Las tasas en Colombia bajaron significativamente en ese periodo debido a las politicas monetarias del Banco de la Republica.
    La linea punteada gris representa el promedio ponderado del sistema financiero completo.{filtro_activo}
    </div>
    """, unsafe_allow_html=True)
    
    # Grafico de barras: Tasa promedio por mes (reemplaza el heatmap)
    st.markdown("#### Tasa Promedio del Sistema por Mes")
    
    if len(hist_total_series) > 0:
        fig_barras_mes = px.bar(
            hist_total_series.sort_values("mes"),
            x="mes",
            y="tasa_prom",
            color_discrete_sequence=["#38bdf8"]
        )
        fig_barras_mes.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            height=350,
            xaxis=dict(title="Mes", gridcolor="rgba(148, 163, 184, 0.1)", tickangle=-45),
            yaxis=dict(title="Tasa Promedio (%)", gridcolor="rgba(148, 163, 184, 0.1)"),
            margin=dict(l=0, r=0, t=10, b=80)
        )
        st.plotly_chart(fig_barras_mes, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
