from csi_project.plots import (
    get_df_acidentes,
    get_df_vendas,
    plot_acidentes_per_month,
    plot_acidentes_versus_vendas,
    plot_acidentes_with_filters,
    plot_vendas_per_month,
)
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    Response,
)
import re
from flask_api import status
from datetime import date, timedelta
import requests
import plotly


# Other

import requests
from unidecode import unidecode


main_page_bp = Blueprint("main_app", __name__, url_prefix="/")


@main_page_bp.route("/")
def welcome():
    return render_template("welcome_page.html")


@main_page_bp.route("/viz")
def viz():
    return render_template("visualization_page.html")


@main_page_bp.route("/att-viz", methods=["POST"])
def att_viz():
    needed_form_fields = {"start_month", "end_month"}

    if not set(request.form.keys()).issuperset(needed_form_fields):
        return Response(
            f"Não contém todos os campos necessários: {needed_form_fields}",
            status.HTTP_400_BAD_REQUEST,
        )

    start_year_month = request.form.get("start_month")
    end_year_month = request.form.get("end_month")

    if not valid_year_month_format(start_year_month) or not valid_year_month_format(
        end_year_month
    ):
        return Response("Formatos de data inválidos", status.HTTP_400_BAD_REQUEST)

    start_year, start_month = map(int, start_year_month.split("-"))
    end_year, end_month = map(int, end_year_month.split("-"))

    if (end_year, end_month) < (start_year, start_month):
        return Response(
            "A data final deve ser maior que a data inicial",
            status.HTTP_400_BAD_REQUEST,
        )

    today_year, today_month = date.today().year, date.today().month
    if (end_year, end_month) > (today_year, today_month):
        return Response(
            "A data final deve ser anterior a data de hoje.",
            status.HTTP_400_BAD_REQUEST,
        )

    try:
        df_acidentes = get_df_acidentes(start_year, start_month, end_year, end_month)
    except Exception as e:
        return Response(
            f"""Erro ao conectar com servidor de dados de acidentes.""",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    df_vendas = get_df_vendas(start_year, start_month, end_year, end_month)

    vendas_per_month_fig = plot_vendas_per_month(df_vendas)
    acidentes_fatais_fig = plot_acidentes_with_filters(
        df_acidentes, [-1, 1, -1, -1], title="Acidentes fatais por mês"
    )
    acidentes_per_month = plot_acidentes_per_month(df_acidentes, True)
    acid_vendas_fig = plot_acidentes_versus_vendas(df_acidentes, df_vendas)

    return dict(
        plots=[
            plotly.io.to_html(vendas_per_month_fig, full_html=False),
            plotly.io.to_html(acidentes_fatais_fig, full_html=False),
            plotly.io.to_html(acidentes_per_month, full_html=False),
            plotly.io.to_html(acid_vendas_fig, full_html=False),
        ],
        status_code=status.HTTP_200_OK,
    )


def valid_year_month_format(year_month):
    return bool(re.match(r"\d\d\d\d\-\d\d", year_month))
