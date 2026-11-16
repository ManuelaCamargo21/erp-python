import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Configuración de la página
st.set_page_config(page_title="ERP DROGUERIA", layout="wide")
st.title(" ERP Drogueria - Control EOQ y Líneas de Espera")
st.markdown("---")

# 2. Base de datos en memoria (Requisito: 3 productos)
productos_db = {
    "Acetaminofén 500mg": {
        "ventas_historicas": [1200, 1350, 1420, 1500, 1680, 1800], 
        "costo_pedido": 15000,
        "costo_mantenimiento": 1600,
        "lead_time": 5
    },
    "Ensure Nutricional 400g": {
        "ventas_historicas": [450, 480, 520, 590, 630, 700],
        "costo_pedido": 25000,
        "costo_mantenimiento": 9750,
        "lead_time": 3
    },
    "Pañales Etapa 3": {
        "ventas_historicas": [800, 850, 890, 930, 980, 1050],
        "costo_pedido": 18000,
        "costo_mantenimiento": 8000,
        "lead_time": 4
    }
}

# 3. Selector de producto en la interfaz
producto_seleccionado = st.selectbox(" Seleccione un producto del catálogo para analizar:", list(productos_db.keys()))
datos = productos_db[producto_seleccionado]

# 4. Motor Matemático
anios = np.array([2020, 2021, 2022, 2023, 2024, 2025])
ventas = np.array(datos["ventas_historicas"])

# Cálculo de Regresión Lineal (W - Proyección)
coeficientes = np.polyfit(anios, ventas, 1)
m, b = coeficientes[0], coeficientes[1]
demanda_proyectada = int(m * 2026 + b)

# Cálculo Lote Económico de Pedido (Q)
D = demanda_proyectada
Cp = datos["costo_pedido"]
Cm = datos["costo_mantenimiento"]
Q = int(np.sqrt((2 * D * Cp) / Cm))

# Cálculo Punto de Reorden (ROP)
demanda_diaria = D / 365
ROP = int(demanda_diaria * datos["lead_time"])

# 5. Interfaz: Cuadro de Resultados (Como en el tablero)
st.subheader(" Panel de Decisión Logística (EOQ)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("D (Demanda Histórica 2025)", f"{ventas[-1]} unid.")
col2.metric("W (Proyección 2026)", f"{D} unid.")
col3.metric("Q (Lote Económico)", f"{Q} unid.")
col4.metric("ROP (Punto Reorden)", f"{ROP} unid.")

st.markdown("---")

# 6. MEJORA: Tabla de Data y Asistente de Compras
col_tabla, col_alerta = st.columns([1, 2])

with col_tabla:
    st.subheader(" Histórico (Data)")
    df_historico = pd.DataFrame({"Año": anios, "Unidades Vendidas": ventas})
    # Mostramos la tablita de datos que simula la base de datos
    st.dataframe(df_historico, use_container_width=True, hide_index=True)

with col_alerta:
    st.subheader(" Asistente Automático ERP")
    st.info(f"**Política de Inventario para {producto_seleccionado}:**\n\nEl sistema ERP recomienda que cuando el inventario físico en bodega llegue exactamente a **{ROP} unidades**, se debe emitir una orden de compra al proveedor por un Lote Económico (Q) de **{Q} unidades**.")
    st.error(f"**Parámetros Financieros:** Costo por pedir: ${Cp:,.0f} COP | Costo de mantenimiento: ${Cm:,.0f} COP")

st.markdown("---")

# 7. Interfaz: Gráficos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader(" Proyección de Demanda")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.plot(anios, ventas, marker='o', color='#2E86C1', label="Datos Reales (2020-2025)")
    
    anios_extendidos = np.append(anios, 2026)
    tendencia = m * anios_extendidos + b
    ax1.plot(anios_extendidos, tendencia, linestyle='--', color="#E73CBC", label="Tendencia (W)")
    ax1.scatter([2026], [demanda_proyectada], color="#E73CB4", zorder=5, s=100)
    
    ax1.set_xlabel("Año")
    ax1.set_ylabel("Unidades")
    ax1.legend()
    ax1.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig1)

with col_graf2:
    st.subheader(" Modelo EOQ (Dientes de Sierra)")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    
    dias_ciclo = int(Q / demanda_diaria)
    tiempo = [0, dias_ciclo, dias_ciclo, dias_ciclo*2, dias_ciclo*2]
    inventario = [Q, 0, Q, 0, Q]
    
    ax2.plot(tiempo, inventario, color='#27AE60', linewidth=2, label="Nivel Físico de Inventario")
    ax2.axhline(y=ROP, color='#C0392B', linestyle='--', label=f'Punto de Reorden (ROP = {ROP})')
    
    ax2.set_xlabel("Días Transcurridos")
    ax2.set_ylabel("Cantidad en Bodega")
    ax2.legend()
    ax2.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig2)