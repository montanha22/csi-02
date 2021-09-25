import zeep
import json
import urllib

import pandas as pd
from unidecode import unidecode


from datetime import date, timedelta
import requests

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

basedir = os.path.abspath(os.path.dirname(__file__))
fachada_wssgs = os.path.join(basedir, "static/py/FachadaWSSGS.wsdl")
acidentes_csv = os.path.join(basedir, "static/py/cat_acidentes.csv")


def get_df_acidentes(start_year, start_month, end_year, end_month):
    next_month_date = date(end_year, end_month, 1) + timedelta(31)
    no_inclusive_end_year, no_inclusive_end_month = (
        next_month_date.year,
        next_month_date.month,
    )

    sql_query = f"""sql=SELECT * from "b56f8123-716a-4893-9348-23945f1ea1b9" WHERE data >= '{start_year}-{start_month}-01' and data < '{no_inclusive_end_year}-{no_inclusive_end_month}-01' """
    url = (
        f"""https://dadosabertos.poa.br/api/3/action/datastore_search_sql?{sql_query}"""
    )
    try:
        r = requests.get(
            url,
            timeout=0.1,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
            },
        )
        data_json = r.json()
        df_acidentes = pd.DataFrame.from_dict(data_json["result"]["records"])
    except:
        df_acidentes = pd.read_csv(acidentes_csv, sep=";")

    df_acidentes["data"] = pd.to_datetime(
        df_acidentes["data"], format="%Y-%m-%d 00:00:00", errors="coerce"
    )
    df_acidentes = df_acidentes[
        (df_acidentes["data"].dt.date >= date(start_year, start_month, 1))
        & (
            df_acidentes["data"].dt.date
            < date(no_inclusive_end_year, no_inclusive_end_month, 1)
        )
    ]
    df_acidentes.reset_index(inplace=True, drop=True)
    df_acidentes["dia"] = df_acidentes["data"].dt.day
    df_acidentes["mes"] = df_acidentes["data"].dt.month
    df_acidentes["ano"] = df_acidentes["data"].dt.year
    df_acidentes["tipo_acid"] = df_acidentes["tipo_acid"].apply(
        lambda x: unidecode(x.lower())
    )

    df_acidentes = df_acidentes[
        [
            "dia",
            "mes",
            "ano",
            "tipo_acid",
            "feridos",
            "fatais",
            "caminhao",
            "moto",
            "latitude",
            "longitude",
        ]
    ]

    return df_acidentes


def get_df_vendas(start_year, start_month, end_year, end_month):
    next_month_date = date(end_year, end_month, 1)  # + timedelta(31)
    start_date = date(start_year, start_month, 1)
    end_date = date(next_month_date.year, next_month_date.month, 1)

    client = zeep.Client(wsdl=fachada_wssgs)
    long_array_type = client.get_type("ns0:ArrayOfflong")
    r = client.service.getValoresSeriesVO(
        long_array_type([7384]),
        start_date.strftime("%d/%m/%Y"),
        end_date.strftime("%d/%m/%Y"),
    )
    aux = zeep.helpers.serialize_object(r[0]["valores"])
    df_vendas = pd.DataFrame(aux)
    df_vendas["valor"] = df_vendas["valor"].apply(lambda x: int(x["_value_1"]))
    df_vendas = df_vendas.rename(columns={"valor": "vendas"})
    df_vendas = df_vendas[["mes", "ano", "vendas"]]

    return df_vendas


def plot_acidentes_with_filters(
    df, cat_values=[-1, -1, -1, -1], title="Acidentes por mês"
):

    cat_list = ["feridos", "fatais", "caminhao", "moto"]

    df = df.sort_values(["ano", "mes"]).copy()
    df["ano-mês"] = df["ano"].astype(str) + " - " + df["mes"].astype(str)
    for (
        col,
        value,
    ) in zip(cat_list, cat_values):
        if value > 0:
            df = df[df[col] == value]

    fig = px.histogram(df, x="ano-mês", barmode="group", title=title)
    fig.update_layout(showlegend=False, bargap=0.2)
    return fig


def plot_acidentes_per_month(df, tipo_acid=False):

    df = df.sort_values(["ano", "mes"]).copy()
    df["ano-mês"] = df["ano"].astype(str) + " - " + df["mes"].astype(str)
    if not tipo_acid:
        fig = px.histogram(
            df,
            x="dia",
            barmode="group",
            labels={"dia": "Dia do mês"},
            title="Acidentes por dia",
        )
        fig.update_layout(showlegend=False, bargap=0.2)
    else:
        fig = px.histogram(
            df,
            x="ano-mês",
            color="tipo_acid",
            barmode="group",
            labels={"mes": "Mês"},
            title="Acidentes por mês",
        )
        fig.update_layout(showlegend=True, bargap=0.2)
        fig.update_layout(
            legend=dict(orientation="h", yanchor="top", y=1.05, xanchor="left", x=0)
        )
    return fig


def plot_vendas_per_month(df):

    # df_aux = df[(df['ano'] == year)]
    df = df.sort_values(["ano", "mes"]).copy()
    df["ano-mês"] = df["ano"].astype(str) + " - " + df["mes"].astype(str)
    fig = px.bar(
        df,
        x="ano-mês",
        y="vendas",
        labels={"ano-mês": "Mês", "vendas": "Número de vendas"},
        title="Vendas por mês",
    )
    fig.update_layout(showlegend=False, bargap=0.2)
    fig.update_yaxes(secondary_y=True)
    return fig


def plot_acidentes_versus_vendas(df_acidentes, df_vendas):

    df_acid_aux = df_acidentes.sort_values(["ano", "mes"]).copy()
    df_acid_aux["ano-mês"] = (
        df_acid_aux["ano"].astype(str) + " - " + df_acid_aux["mes"].astype(str)
    )

    df_vend_aux = df_vendas.sort_values(["ano", "mes"]).copy()
    df_vend_aux["ano-mês"] = (
        df_vend_aux["ano"].astype(str) + " - " + df_vend_aux["mes"].astype(str)
    )

    df_acid_aux = (
        df_acid_aux[["ano", "mes", "dia", "ano-mês"]]
        .groupby(by=["ano", "mes", "ano-mês"])
        .count()
        .reset_index()
        .rename(columns={"dia": "acidentes"})
    )
    df_vend_aux = df_vend_aux.drop(columns=["ano"]).reset_index(drop=True)

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=df_vend_aux["ano-mês"], y=df_vend_aux["vendas"], name="Vendas"),
        secondary_y=True,
    )

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=df_acid_aux["ano-mês"], y=df_acid_aux["acidentes"], name="Acidentes"
        ),
        secondary_y=False,
    )

    # Add figure title
    fig.update_layout(title_text="Número de vendas versus acidentes")

    # Set x-axis title
    fig.update_xaxes(title_text="Mês")

    # Set y-axes titles
    fig.update_yaxes(title_text="Número de acidentes", secondary_y=False)
    fig.update_yaxes(title_text="Número de vendas", tickprefix="\t", secondary_y=True)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=1.05, xanchor="left", x=0)
    )
    return fig
