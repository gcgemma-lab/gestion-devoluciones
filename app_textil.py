import streamlit as st
import pandas as pd
from datetime import date
import io
import os
import plotly.express as px

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Gestión de Devoluciones de Clientes", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = []

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { background-color: #1e3a8a; color: white; font-weight: bold; border-radius: 8px; height: 3.5em; }
    .area-comercial { padding: 15px; border-radius: 10px; background-color: #eff6ff; border-left: 10px solid #3b82f6; margin-bottom: 20px; }
    .area-operaciones { padding: 15px; border-radius: 10px; background-color: #fff7ed; border-left: 10px solid #f97316; }
    .res-aceptada { color: #166534; font-weight: bold; background-color: #dcfce7; padding: 15px; border-radius: 8px; border: 1px solid #166534; }
    .res-rechazada { color: #991b1b; font-weight: bold; background-color: #fee2e2; padding: 15px; border-radius: 8px; border: 1px solid #991b1b; }
    </style>
    """, unsafe_allow_html=True)

# 2. CABECERA (Logo más grande y nuevo título)
col_l, col_t = st.columns([1.5, 4]) # Ajustado ratio para logo más grande
with col_l:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=250) # Tamaño aumentado de 150 a 250
    else:
        st.info("📌 Logo Corporativo")
with col_t:
    st.title("🧵 Gestión de Devoluciones de Clientes")
    st.write("Control de Calidad Textil | Flujo Comercial - Operaciones")

st.divider()

# 3. FORMULARIO INTEGRADO
with st.form("formulario_principal"):
    
    # --- ÁREA COMERCIAL ---
    st.markdown('<div class="area-comercial"><h3>🔵 ÁREA COMERCIAL (Registro)</h3></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        cliente = st.text_input("Cliente")
        n_pedido = st.text_input("Nº Pedido / Factura")
        fecha_entrega = st.date_input("Fecha Entrega", max_value=date.today())
    with c2:
        lote = st.text_input("Nº Lote / Partida")
        metraje = st.number_input("Metros Afectados", min_value=0.0)
        incidencia = st.selectbox("Tipo de Incidencia", [
            "Error de Envío", "Diferencia de Tonalidad", "Manchas/Suciedad", 
            "Falla Estampación", "Agujeros", "Ancho Insuficiente", "Otras"
        ])
    with c3:
        st.write("**Composición del Tejido**")
        # Fibra 1
        comp1_tipo = st.selectbox("Fibra 1", ["Algodón", "Poliéster", "Lino", "Viscosa", "Elastano", "Seda"])
        comp1_perc = st.number_input("% Fibra 1", 0, 100, 100)
        # Fibra 2
        comp2_tipo = st.selectbox("Fibra 2", ["N/A", "Elastano", "Algodón", "Poliéster", "Lino", "Viscosa"])
        comp2_perc = st.number_input("% Fibra 2", 0, 100, 0)
        
    cc1, cc2 = st.columns([2, 1])
    with cc1:
        comentarios_comercial = st.text_area("Observaciones del Comercial")
    with cc2:
        persona_registra = st.text_input("Registrado por (Comercial)")
        estado_tela = st.selectbox("Estado de la tela", ["Pieza Entera", "Cortada/Confeccionada"])

    st.write("") 
    
    # --- ÁREA OPERACIONES ---
    st.markdown('<div class="area-operaciones"><h3>🟠 ÁREA DE OPERACIONES (Resolución)</h3></div>', unsafe_allow_html=True)
    o1, o2 = st.columns(2)
    with o1:
        comentarios_op = st.text_area("Dictamen de Calidad / Operaciones")
        persona_autoriza = st.text_input("Autorizado por (Operaciones)")
    with o2:
        decision = st.radio("Resolución Final", ["ACEPTADA", "RECHAZADA"])
        tipo_resolucion = st.selectbox("Tipo de devolución", ["Ninguna", "1- Devolución total dinero", "2- Devolución parcial"])

    submit = st.form_submit_button("REGISTRAR Y FINALIZAR")

# 4. PROCESAMIENTO
if submit:
    if (comp1_perc + comp2_perc) != 100:
        st.error(f"❌ Error en Composición: La suma es {comp1_perc + comp2_perc}%. Debe ser 100%.")
    else:
        composicion_final = f"{comp1_perc}% {comp1_tipo}"
        if comp2_tipo != "N/A": composicion_final += f" / {comp2_perc}% {comp2_tipo}"

        st.session_state.db.append({
            "Fecha": date.today(),
            "Cliente": cliente,
            "Pedido": n_pedido,
            "Composición": composicion_final,
            "Metros": metraje,
            "Incidencia": incidencia,
            "Registra": persona_registra,
            "Resolución": decision,
            "Tipo Dev": tipo_resolucion,
            "Autoriza": persona_autoriza,
            "Obs. Operaciones": comentarios_op
        })
        
        estilo = "res-aceptada" if decision == "ACEPTADA" else "res-rechazada"
        st.markdown(f'<div class="{estilo}">REGISTRO EXITOSO: {decision}</div>', unsafe_allow_html=True)

# 5. ESTADÍSTICAS Y REPORTES (Siempre usan todo el historial)
st.divider()
tab1, tab2, tab3 = st.tabs(["📊 Estadísticas Históricas", "📁 Exportar Excel", "📋 Historial Completo"])

with tab1:
    if st.session_state.db:
        df = pd.DataFrame(st.session_state.db)
        g1, g2 = st.columns(2)
        
        with g1:
            st.write("**Balance de Resoluciones**")
            fig_res = px.bar(df, x='Resolución', color='Resolución',
                             color_discrete_map={'ACEPTADA': '#166534', 'RECHAZADA': '#991b1b'},
                             title="Aceptadas vs Rechazadas")
            st.plotly_chart(fig_res, use_container_width=True)
            
        with g2:
            st.write("**Motivos Técnicos (Historial)**")
            fig_inc = px.pie(df, names='Incidencia', title="Distribución de Incidencias",
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_inc, use_container_width=True)
    else:
        st.info("No hay datos históricos para mostrar en los gráficos.")

with tab2:
    if st.session_state.db:
        df_ex = pd.DataFrame(st.session_state.db)
        towrite = io.BytesIO()
        df_ex.to_excel(towrite, index=False, engine='xlsxwriter')
        st.download_button("📥 Descargar Reporte Excel Completo", towrite.getvalue(), f"reporte_devoluciones_{date.today()}.xlsx")

with tab3:
    if st.session_state.db:
        st.dataframe(pd.DataFrame(st.session_state.db), use_container_width=True)