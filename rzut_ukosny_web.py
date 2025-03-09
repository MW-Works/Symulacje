import math
import streamlit as st
import plotly.graph_objects as go
import time  # Dodajemy opóźnienie dla efektu animacji

def calculate_trajectory(angle, v0, k1, m, g, dt, speed_factor):
    t = 0
    x_points = []
    y_points = []
    
    while True:
        angle_rad = math.radians(angle)
        x = ((v0 * m / k1) * math.cos(angle_rad)) * (1 - math.exp(-k1 * t / m))
        y = (((v0 * m / k1) * math.sin(angle_rad)) + (m * g / k1)) * (1 - math.exp(-k1 * t / m)) - (m * g * t / k1)
        
        if y < 0:
            break
            
        x_points.append(x)
        y_points.append(y)
        t += dt * speed_factor
    
    return x_points, y_points

# Konfiguracja strony
st.set_page_config(page_title="Symulacja rzutu ukośnego", layout="wide")
st.title("🏹 Symulacja rzutu ukośnego z oporem powietrza")

# Widgety w sidebarze
with st.sidebar:
    st.header("Parametry")
    angle = st.slider("Kąt [°]", 0, 90, 45)
    v0 = st.slider("Prędkość [m/s]", 10, 1000, 500)
    k1 = st.slider("Opór powietrza [kg/s]", 0.1, 10.0, 1.0)
    m = st.slider("Masa [kg]", 1.0, 100.0, 10.0)
    g = st.slider("Grawitacja [m/s²]", 0.0, 20.0, 9.81)
    speed_factor = st.slider("Przyspieszenie symulacji", 1.0, 100.0, 1.0)
    simulate_button = st.button("Uruchom symulację")

# Główny obszar
if simulate_button:
    # Oblicz pełną trajektorię
    x_full, y_full = calculate_trajectory(angle, v0, k1, m, g, 0.005, speed_factor)
    
    # Inicjalizacja wykresu
    fig = go.Figure()
    plot = st.empty()  # Kontener na dynamiczny wykres
    
    # Animacja krokowa
    for i in range(1, len(x_full)+1):
        x = x_full[:i]
        y = y_full[:i]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x, 
            y=y, 
            mode='lines+markers',
            line=dict(color='blue', width=2),
            marker=dict(size=5, color='red')
        ))
        fig.update_layout(
            title="Animacja trajektorii",
            xaxis_title="Pozycja X [m]",
            yaxis_title="Pozycja Y [m]",
            showlegend=False
        )
        
        plot.plotly_chart(fig, use_container_width=True)
        time.sleep(0.05)  # Opóźnienie dla efektu animacji