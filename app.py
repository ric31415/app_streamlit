import streamlit as st
import sympy as sp
import math 
import pandas as pd

# Unidades
Tn = 1000  # kgf
Tn_m2 = 0.1  # kgf/cm²
Tn_m3 = 0.001  # kgf/cm³
m = 100  # cm

# Datos iniciales mediante la interfaz de Streamlit
st.title("Cálculo de Cargas y Refuerzos")

P_D = st.number_input("Carga Muerta (P_D) en Tn", min_value=0.0, value=180.0) * Tn
P_L = st.number_input("Carga Viva (P_L) en Tn", min_value=0.0, value=65.0) * Tn
qadm = st.number_input("Carga admisible (qadm) en kgf/cm²", min_value=0.0, value=38.0) * Tn_m2
fc = st.number_input("Resistencia del concreto (fc) en kgf/cm²", min_value=0, value=210)
fy = st.number_input("Resistencia del acero (fy) en kgf/cm²", min_value=0, value=4200)
sc = st.number_input("Esfuerzo admisible (sc) en kgf/cm²", min_value=0.0, value=0.500) * Tn_m2
eB = st.number_input("Excentricidad (eB) en cm", min_value=0.0, value=0.25) * m
Pe = st.number_input("Peso específico (Pe) en kgf/cm³", min_value=0.0, value=2.1) * Tn_m3
D_f = st.number_input("Profundidad de cimentación (D_f) en m", min_value=0.0, value=1.7) * m
rec = st.number_input("Recubrimiento (rec) en cm", min_value=0.0, value=5.0)
t1 = st.number_input("Espesor (t1) en cm", min_value=0.0, value=80.0)
t2 = st.number_input("Espesor (t2) en cm", min_value=0.0, value=55.0)

# Cálculos
q = D_f * Pe
B, L = sp.symbols("B L")
P = P_D + P_L
M = eB * P
B = L
qn = qadm - q - sc
q1 = P / (B * L) - 6 * M / (B ** 2 * L)
q2 = P / (B * L) + 6 * M / (B ** 2 * L)
eq1 = sp.Eq(qn, q2)
sol_L = sp.nsolve(eq1, L, 10)
L = sp.ceiling(sol_L / 50) * 50
B = L
q2 = P / (B * L) + 6 * M / (B ** 2 * L)
q1 = P / (B * L) - 6 * M / (B ** 2 * L)

st.header("Dimensionamiento en Estado Límite de Servicio")
st.write(f"P = {P:.2f} kgf")
st.write(f"M = {M:.2f} kgf·cm")
st.write(f"qn = {qn:.2f} kgf/cm²")
st.write(f"B = {B:.0f} cm")
st.write(f"L = {L:.0f} cm")
st.write(f"q1 = {q1:.2f} kgf/cm²")
st.write(f"q2 = {q2:.2f} kgf/cm²")

# Diseño en Estado Límite Último
Pu = 1.2 * P_D + 1.6 * P_L
Mu = Pu * eB
qu1 = Pu / (B * L) - 6 * Mu / (B ** 2 * L)
qu2 = Pu / (B * L) + 6 * Mu / (B ** 2 * L)

st.header("Diseño en Estado Límite Último")
st.write(f"Pu = {Pu:.2f} kgf")
st.write(f"Mu = {Mu:.2f} kgf·cm")
st.write(f"qu1 = {qu1:.2f} kgf/cm²")
st.write(f"qu2 = {qu2:.2f} kgf/cm²")

# Diseño por Corte
x, d = sp.symbols("x d")
quy = qu1 + (qu2 - qu1) / B * x
qu3 = quy.subs(x, B / 2 + t1 / 2 + d)
vu = (qu2 + qu3) / 2 * (B / 2 - t1 / 2 - d) * L
vu1 = 0.75 * 0.53 * sp.sqrt(fc) * L * d
eq2 = sp.Eq(vu, vu1)
d = sp.nsolve(eq2, d, 10)
h = math.ceil((d  + rec) / 5) * 5
d = h - rec
bo = 2 * (t1 + d) + 2 * (t2 + d)
qu3 = quy.subs(x, B/2 + t1/2 + d)
vu = (qu2 + qu3) / 2 * (B / 2 - t1 / 2 - d) * L

st.header("Diseño por Corte")
st.write(f"h = {h:.2f} cm")
st.write(f"d = {d:.2f} cm")
st.write(f"bo = {bo:.2f}")
st.write(f"Vu = {vu:.2f} kgf")

# Análisis de Refuerzo Longitudinal
qu6 = quy.subs(x, B / 2 + t1 / 2 + d / 2)
Mu = (qu6 + qu2) / 2 * (B / 2 - t1 / 2) ** 2 * L * 1 / 2
y = sp.symbols("y")
Mu1 = 0.9 * 0.85 * fc * B * y * (h - rec - y / 2)
y1 = sp.nsolve(Mu - Mu1, y, 5)
Nc = 0.9 * 0.85 * fc * B * y1
As = Nc / (0.9 * fy)

diametros = [12, 16, 20, 25, 32]
areas = [1.13, 2.01, 3.14, 4.90, 8.04]
separacion_teo = []
separacion = []

for area in areas:
    barras = As / area
    sep1 = B / barras
    sep = math.floor((B / barras) / 5) * 5
    separacion.append(sep)
    separacion_teo.append(round(sep1, 2))

df = pd.DataFrame({
    "D [mm]": diametros,
    "A [cm²]": areas,
    "Sep teórica [cm]": separacion_teo,
    "Sep adoptada [cm]": separacion
})

st.header("Análisis de Refuerzo Longitudinal")
st.write(f"Nc = {Nc:.2f} kgf")
st.write(f"As = {As:.2f} cm²")
st.write(df)
