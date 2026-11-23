import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Квантовое туннелирование", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0a0a14; color: white; }
    h1, h2, h3 { color: #00ffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("⚛️ 3D-модель квантового туннелирования")
st.write("Двигайте ползунки слева (и отпускайте). График можно крутить мышкой. Красная точка показывает вашу вероятность.")

e_charge, hbar, m_e = 1.602e-19, 1.055e-34, 9.11e-31

def calculate_probability(E, U0, a, mass_multiplier):
    m = m_e * mass_multiplier
    if E >= U0:
        k1 = np.sqrt(2 * m * E * e_charge) / hbar
        k2 = np.sqrt(2 * m * (E - U0) * e_charge) / hbar
        if E == U0:
            return 1 / (1 + (m * U0 * e_charge * (a * 1e-9)**2) / (2 * hbar**2))
        return 1 / (1 + ((k1**2 - k2**2)**2) / (4 * k1**2 * k2**2) * np.sin(k2 * a * 1e-9)**2)
    else:
        k1 = np.sqrt(2 * m * E * e_charge) / hbar
        kappa = np.sqrt(2 * m * (U0 - E) * e_charge) / hbar
        return 1 / (1 + ((k1**2 + kappa**2)**2) / (4 * k1**2 * kappa**2) * np.sinh(kappa * a * 1e-9)**2)

# Умное форматирование текста
def format_prob(p):
    if p > 0.01:
        return f"{p*100:.2f} %"
    elif p > 1e-6:
        return f"{p*100:.4f} %"
    else:
        return "< 0.0001 % (очень мала)"

# Ползунки
st.sidebar.header("Параметры системы")
U0 = st.sidebar.slider("Высота барьера U0 (эВ)", 0.5, 5.0, 2.0, 0.1)
mass_multiplier = st.sidebar.slider("Масса (в массах e)", 1.0, 2000.0, 1.0, 1.0)
E_current = st.sidebar.slider("Текущая Энергия E (эВ)", 0.1, 4.9, 1.0, 0.1)
a_current = st.sidebar.slider("Текущая Ширина a (нм)", 0.1, 2.0, 0.5, 0.1)

# Сетка для 3D
E_vals = np.linspace(0.1, 4.9, 40)
a_vals = np.linspace(0.1, 2.0, 40) 
E_mesh, a_mesh = np.meshgrid(E_vals, a_vals)

Z = np.zeros_like(E_mesh)
for i in range(E_mesh.shape[0]):
    for j in range(E_mesh.shape[1]):
        Z[i, j] = calculate_probability(E_mesh[i, j], U0, a_mesh[i, j], mass_multiplier)

Z_log = np.log10(np.clip(Z, 1e-20, 1.0))

current_prob = calculate_probability(E_current, U0, a_current, mass_multiplier)
z_point_log = np.log10(np.clip(current_prob, 1e-20, 1.0))

# --- РИСУЕМ 3D ГРАФИК ---
fig = go.Figure()

fig.add_trace(go.Surface(z=Z_log, x=E_mesh, y=a_mesh, colorscale='Viridis', opacity=0.9))

# Красная точка с красивым текстом
prob_text = format_prob(current_prob)
fig.add_trace(go.Scatter3d(
    x=[E_current], y=[a_current], z=[z_point_log],
    mode='markers+text',
    marker=dict(size=8, color='red', line=dict(color='white', width=2)),
    text=[f"D = {prob_text}"],
    textposition="top center",
    textfont=dict(color='red', size=14, family="Arial Black"),
    name="Ваша точка"
))

fig.add_trace(go.Scatter3d(
    x=[E_current, E_current], y=[a_current, a_current], z=[-20, z_point_log],
    mode='lines', line=dict(color='red', width=4), showlegend=False
))

fig.update_layout(
    scene=dict(
        xaxis_title='Энергия E (эВ)', yaxis_title='Ширина a (нм)', zaxis_title='log₁₀(D)',
        xaxis=dict(backgroundcolor="#0a0a14", gridcolor="#333333", color="white"),
        yaxis=dict(backgroundcolor="#0a0a14", gridcolor="#333333", color="white"),
        zaxis=dict(backgroundcolor="#0a0a14", gridcolor="#333333", color="white"),
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
    ),
    paper_bgcolor='#0a0a14', font=dict(color='white'), margin=dict(l=0, r=0, b=0, t=0), height=700
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.info("💡 **Совет:** Поставьте энергию E = 3.0 эВ, а высоту барьера U0 = 2.0 эВ. Вы увидите, что вероятность будет высокой, и буква 'e' пропадет.")

if current_prob > 0.01:
    st.success(f"Вероятность для выбранных параметров: {format_prob(current_prob)}")
else:
    st.warning(f"Вероятность для выбранных параметров: {format_prob(current_prob)}")