import os
from datetime import date, timedelta

import pandas as pd
import zeep
from unidecode import unidecode

import requests

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
