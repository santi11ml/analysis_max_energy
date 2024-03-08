import streamlit as st
import pandas as pd

from curva_pato.create import dataframe_curve

st.sidebar.header("POTENCIA GENERADORES")

gen_1 = st.sidebar.slider(
    "Generador 1 [kWh]", min_value=0, max_value=150, value=140, step=1)
gen_2 = st.sidebar.slider(
    "Generador 2 [kWh]", min_value=0, max_value=120, value=100, step=1)

st.sidebar.header("DATOS INDUSTRIALES")

st.sidebar.subheader("DESPULPADORA")

despulpadoras = st.sidebar.slider(
    "Cantidad de Despulpadoras - [1.5 kWh]", min_value=0, max_value=100, value=100, step=1)
start_desp, end_desp = st.sidebar.select_slider(
    'SELECCIONAR HORARIO DESPULPADORA',
    options=range(1, 25),
    value=(15, 18))

st.sidebar.subheader("SILOS")
silos = st.sidebar.slider(
    "Cantidad de Silos - [10.0 kWh]", min_value=0, max_value=20, value=20, step=1)
start_silo, end_silo = st.sidebar.select_slider(
    'SELECCIONAR HORARIO SILOS',
    options=range(1, 25),
    value=(1, 24))

st.sidebar.subheader("TOSTADORA")
tostadoras = st.sidebar.slider(
    "Cantidad de Tostadora de Café - [2 kWh]", min_value=0, max_value=5, value=3, step=1)
start_tost, end_tost = st.sidebar.select_slider(
    'SELECCIONAR HORARIO TOSTADORAS',
    options=range(1, 25),
    value=(10, 17))

st.sidebar.subheader("TRILLADORA")
trilladoras = st.sidebar.slider(
    "Cantidad de Trilladora - [0.5 kWh]", min_value=0, max_value=5, value=2, step=1)
start_tril, end_tril = st.sidebar.select_slider(
    'SELECCIONAR HORARIO TRILLADORAS',
    options=range(1, 25),
    value=(12, 17))

st.sidebar.header("DATOS RESIDENCIALES")

total_casas = st.sidebar.number_input("Cantidad de Casas", value=680)
casa_1 = st.sidebar.slider(
    "Cantidad de Casas Con Medidores", min_value=0, max_value=total_casas, value=306, step=1)
casa_2 = st.sidebar.slider(
    "Cantidad de Casas Sin Medidores", min_value=0, max_value=total_casas, value=total_casas - casa_1, step=1)

st.sidebar.subheader("CONSUMO PROMEDIO DIARIO DATOS RESIDENCIALES")

con_casa_1 = st.sidebar.slider(
    "Consumo Diario Casas Con Medidores", min_value=0.0, max_value=40.0, value=7.0, step=0.2)
con_casa_2 = st.sidebar.slider(
    "Consumo Diario Casas Sin Medidores", min_value=0.0, max_value=40.0, value=10.0, step=0.2)


# ------------------------------------------------------------------------------------------------------ #

st.title("ANALISIS DE DATOS PICO")

st.header("GENERACIÓN")

col1, col2, col3 = st.columns(3)
col1.metric("Generación 1", f"{gen_1} kWh", f"{round(gen_1 * 100 / 140 - 100, 2)} %")
col2.metric("Generación 2", f"{gen_2} kWh", f"{round(gen_2 * 100 / 100 - 100, 2)} %")
col3.metric("Generación Total", f"{gen_1 + gen_2} kWh", f"{round((gen_1 + gen_2) * 100 / 240 - 100, 2)} %")

col1, col2 = st.columns(2)

col1.metric("Generación Díaria", f"{(gen_1 + gen_2) * 24:,} kW",
            f"{round((gen_1 + gen_2) * 24 * 100 / (240 * 24) - 100, 2)} %")
col2.metric("Generación Mes", f"{(gen_1 + gen_2) * 24 * 30:,} kW")

list_hours = range(1, 25)

df_horas = pd.DataFrame({
    "HORAS": list_hours
}).set_index("HORAS")


def create_df(name: str, start_hour: float, end_hour: float, consume: float, cantidad: float):
    list_hours = range(start_hour, end_hour + 1)
    df = pd.DataFrame({
        f"HORAS": list_hours,
        f"CONSUMO_{name}": (len(list_hours) * [consume*cantidad])
    })

    return df

df_desp = create_df(name="DESPULPADORA", start_hour=start_desp, end_hour=end_desp, consume=1.5, cantidad=despulpadoras).set_index("HORAS")
df_silo = create_df(name="SILO", start_hour=start_silo, end_hour=end_silo, consume=10, cantidad=silos).set_index("HORAS")
df_tost = create_df(name="TOSTADORA", start_hour=start_tost, end_hour=end_tost, consume=2, cantidad=tostadoras).set_index("HORAS")
df_tril = create_df(name="TRILLADORA", start_hour=start_tril, end_hour=end_tril, consume=0.5, cantidad=trilladoras).set_index("HORAS")

df_ind = pd.concat([df_desp, df_silo, df_tost, df_tril], axis=1).reset_index()
df_ind.fillna(0, inplace=True)

col_1, col_2, = st.columns(2)

with col_1:
    st.header("CONSUMO INDUSTRIAL")

    st.line_chart(
        df_ind, x="HORAS", y=["CONSUMO_DESPULPADORA", "CONSUMO_SILO", "CONSUMO_TOSTADORA", "CONSUMO_TRILLADORA"]
    )

    col1, col2 = st.columns(2)
    col1.metric("Consumo Despulpadora Diario", f"{df_ind.CONSUMO_DESPULPADORA.sum():,} kW")
    col2.metric("Consumo Silos Diario", f"{df_ind.CONSUMO_SILO.sum():,} kW")

    col3, col4 = st.columns(2)
    col3.metric("Consumo Tostadora Diario", f"{df_ind.CONSUMO_TOSTADORA.sum():,} kW")
    col4.metric("Consumo Trilladora Diario", f"{df_ind.CONSUMO_TRILLADORA.sum():,} kW")

    col1, col2 = st.columns(2)
    col1.metric("Consumo Industrial Diaria",
                f"""{df_ind.CONSUMO_DESPULPADORA.sum() + df_ind.CONSUMO_SILO.sum() +
                     df_ind.CONSUMO_TOSTADORA.sum() + df_ind.CONSUMO_TRILLADORA.sum():,} kW""")

    col2.metric("Consumo Industrial Mes", f"""{
    (df_ind.CONSUMO_DESPULPADORA.sum() + df_ind.CONSUMO_SILO.sum() +
     df_ind.CONSUMO_TOSTADORA.sum() + df_ind.CONSUMO_TRILLADORA.sum()) * 30:,} kW""")

with col_2:
    st.header("CONSUMO RESIDENCIAL")

    df_tmp = dataframe_curve()
    df_tmp["PORC_2"] = df_tmp.PORC / df_tmp.PORC.sum()
    df_tmp["CONSUMO CASAS CON MEDIDORES [kW]"] = df_tmp.PORC_2 * casa_1 * con_casa_1
    df_tmp["CONSUMO CASAS SIN MEDIDORES [kW]"] = df_tmp.PORC_2 * casa_2 * con_casa_2

    st.line_chart(
        df_tmp, x="HORAS", y=["CONSUMO CASAS CON MEDIDORES [kW]", "CONSUMO CASAS SIN MEDIDORES [kW]"]
    )

    col1, col2 = st.columns(2)
    col1.metric("Consumo Diario Casas Con Medidores", f"{int(df_tmp['CONSUMO CASAS CON MEDIDORES [kW]'].sum()):,} kWh")
    col2.metric("Consumo Diario Casas Sin Medidores", f"{int(df_tmp['CONSUMO CASAS SIN MEDIDORES [kW]'].sum()):,} kWh")

    col1, col2 = st.columns(2)
    col1.metric("Consumo Residencial Diario",
                f"""{int(df_tmp['CONSUMO CASAS CON MEDIDORES [kW]'].sum() + df_tmp['CONSUMO CASAS SIN MEDIDORES [kW]'].sum()):,} kW""")

    col2.metric("Consumo Residencial Mes", f"""{
    int(df_tmp['CONSUMO CASAS CON MEDIDORES [kW]'].sum() + df_tmp['CONSUMO CASAS SIN MEDIDORES [kW]'].sum()) * 30:,} kW""")


st.header("CONSUMO TOTAL")

df = pd.concat([df_ind.set_index("HORAS"), df_tmp.set_index("HORAS")], axis=1).reset_index()
df["CONSUMO RESIDENCIAL"] = (df['CONSUMO CASAS CON MEDIDORES [kW]'] + df_tmp['CONSUMO CASAS SIN MEDIDORES [kW]'])
df["CONSUMO INDUSTRIAL"] = df["CONSUMO_DESPULPADORA"] + df["CONSUMO_SILO"] + df["CONSUMO_TOSTADORA"] + df["CONSUMO_TRILLADORA"]
df["CONSUMO TOTAL"] = df["CONSUMO RESIDENCIAL"] + df["CONSUMO INDUSTRIAL"]
df["GENERACIÓN"] = (gen_1 + gen_2)

st.line_chart(
    df, x="HORAS", y=["CONSUMO RESIDENCIAL", "CONSUMO INDUSTRIAL", "GENERACIÓN", "CONSUMO TOTAL"]
)

## st.dataframe(df)

