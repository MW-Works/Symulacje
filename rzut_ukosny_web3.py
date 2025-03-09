import math
import time
import numpy as np
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
from scipy.integrate import solve_ivp

# Konfiguracja strony
st.set_page_config(page_title="Rzut ukośny", layout="wide", page_icon="🎯")
st.title("🎯 Ultimate Symulator Rzutu 3000")
st.markdown("## Zobacz jak np. masa i grawitacja wpływają na trajektorie rzutu!")

# Układ interfejsu – suwaki do parametrów
col1, col2, col3, col4 = st.columns(4)
with col1:
    v0 = st.slider("Prędkość początkowa (m/s)", min_value=0.0, max_value=1000.0, value=100.0, step=1.0)
with col2:
    angle = st.slider("Kąt początkowy (°)", min_value=0, max_value=90, value=45, step=1)
with col3:
    drag = st.slider("Współczynnik oporu b (N·s²/m²)", min_value=0.0, max_value=0.05, value=0.005, step=0.0001, format="%.4f")
with col4:
    mass = st.slider("Masa obiektu (kg)", min_value=0.1, max_value=1000.0, value=10.0, step=0.1)

# Suwak do grawitacji (umożliwia eksperymenty np. z Marsjaną)
g = st.slider("Grawitacja (m/s²)", min_value=0.0, max_value=24.79, value=9.81, step=0.1)

# Przyciski – "Ognia!" i "Wyczyść"
colA, colB = st.columns(2)
with colA:
    fire = st.button("🚀 Ognia!")
with colB:
    clear = st.button("🔄 Wyczyść")

# Utrzymanie historii trajektorii
if 'trajectories' not in st.session_state:
    st.session_state['trajectories'] = []

if clear:
    st.session_state['trajectories'] = []

# Funkcja obliczeniowa – teraz z masą i grawitacją
def projectile_ode(t, state, g, drag, mass):
    x, y, vx, vy = state
    v = math.sqrt(vx**2 + vy**2)
    ax = - (drag / mass) * v * vx
    ay = - g - (drag / mass) * v * vy
    return [vx, vy, ax, ay]

def hit_ground(t, state, g, drag, mass):
    return state[1]
hit_ground.terminal = True
hit_ground.direction = -1

@st.cache_data(show_spinner=False)
def compute_trajectory(v0, angle, g, drag, mass):
    angle_rad = math.radians(angle)
    # Ustawiamy początkową wysokość na niewielką wartość, aby uniknąć natychmiastowego zakończenia
    initial_state = [0.0, 1e-6, v0 * math.cos(angle_rad), v0 * math.sin(angle_rad)]
    sol = solve_ivp(
        fun=lambda t, y: projectile_ode(t, y, g, drag, mass),
        t_span=(0, 1000),
        y0=initial_state,
        events=lambda t, y: hit_ground(t, y, g, drag, mass),
        dense_output=True,
        rtol=1e-7,
        atol=1e-9
    )
    if sol.t_events[0].size > 0:
        t_hit = sol.t_events[0][0]
    else:
        t_hit = sol.t[-1]
    t_vals = np.linspace(0, t_hit, 300)
    sol_vals = sol.sol(t_vals)
    x = sol_vals[0]
    y = sol_vals[1]
    vx = sol_vals[2]
    vy = sol_vals[3]
    max_height = np.max(y)
    range_val = x[-1]
    final_speed = math.sqrt(vx[-1]**2 + vy[-1]**2)
    return t_vals, x, y, vx, vy, max_height, range_val, final_speed

import plotly.graph_objects as go

# Funkcja do generowania wykresu prędkości
def plot_velocity(t_vals, vx, vy):
    v = np.sqrt(vx**2 + vy**2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t_vals, y=v, mode="lines", name="Prędkość"))
    fig.update_layout(
        title="Prędkość w funkcji czasu",
        xaxis_title="Czas [s]",
        yaxis_title="Prędkość [m/s]",
        template="plotly_white"
    )
    return fig

# Funkcja do generowania wykresu przyspieszenia
def plot_acceleration(t_vals, vx, vy):
    ax = np.gradient(vx, t_vals)
    ay = np.gradient(vy, t_vals)
    a = np.sqrt(ax**2 + ay**2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t_vals, y=a, mode="lines", name="Przyspieszenie"))
    fig.update_layout(
        title="Przyspieszenie w funkcji czasu",
        xaxis_title="Czas [s]",
        yaxis_title="Przyspieszenie [m/s²]",
        template="plotly_white"
    )
    return fig


# Obliczanie trajektorii po kliknięciu "Ognia!"
if fire:
    t_vals, x, y, vx, vy, max_height, range_val, final_speed = compute_trajectory(v0, angle, g, drag, mass)
    traj = {
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'v0': v0,
        'angle': angle,
        'drag': drag,
        'mass': mass,
        'g': g,
        't': t_vals,
        'x': x,
        'y': y,
        'vx': vx,
        'vy': vy,
        'max_height': max_height,
        'range': range_val,
        'final_speed': final_speed
    }
    st.session_state['trajectories'].append(traj)

# Rysowanie wykresu wszystkich trajektorii
fig = go.Figure()
colors = ["red", "blue", "green", "orange", "purple", "brown"]
for i, traj in enumerate(st.session_state['trajectories']):
    color = colors[i % len(colors)]
    fig.add_trace(go.Scatter(x=traj['x'], y=traj['y'],
                             mode="lines",
                             name=f"#{i+1}: v0={traj['v0']}, kąt={traj['angle']}°",
                             line=dict(color=color, width=2)))
fig.update_layout(
    title="Trajektorie rzutu ukośnego",
    xaxis_title="Odległość [m]",
    yaxis_title="Wysokość [m]",
    xaxis=dict(scaleanchor="y", scaleratio=1),
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

# Wyświetlenie odczytów ostatniego rzutu
if st.session_state['trajectories']:
    last_traj = st.session_state['trajectories'][-1]
    st.markdown("### Odczyty ostatniego rzutu:")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Czas ruchu", f"{last_traj['t'][-1]:.2f} s")
    col2.metric("Zasięg", f"{last_traj['range']:.2f} m")
    col3.metric("Wysokość maksymalna", f"{last_traj['max_height']:.2f} m")
    col4.metric("Prędkość końcowa", f"{last_traj['final_speed']:.2f} m/s")

    # Generowanie i wyświetlanie wykresów
    velocity_fig = plot_velocity(last_traj['t'], last_traj['vx'], last_traj['vy'])
    acceleration_fig = plot_acceleration(last_traj['t'], last_traj['vx'], last_traj['vy'])

    st.plotly_chart(velocity_fig, use_container_width=True)
    st.plotly_chart(acceleration_fig, use_container_width=True)
