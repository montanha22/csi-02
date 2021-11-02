import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
