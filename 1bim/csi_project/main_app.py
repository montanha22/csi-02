import io
from typing import Any, Dict, Tuple
from flask.helpers import send_file

from werkzeug.datastructures import ImmutableDict
from csi_project.plots import (
    plot_acidentes_per_month,
    plot_acidentes_versus_vendas,
    plot_acidentes_with_filters,
    plot_vendas_per_month,
)
from csi_project.requests import (
    get_df_acidentes,
    get_df_vendas,
)
from flask import (
    Blueprint,
    render_template,
    request,
    Response,
)
import re
from flask_api import status
from datetime import date
import plotly


main_page_bp = Blueprint("main_app", __name__, url_prefix="/")
api_bp = Blueprint("api", __name__, url_prefix="/api/v1/")


@main_page_bp.route("/")
def welcome():
    return render_template("welcome_page.html")


@main_page_bp.route("/viz")
def viz():
    return render_template("visualization_page.html")


def validate_form_dates(form: Dict[str, str]) -> Tuple[bool, Any]:
    """
    Validates the form dates.
    :param form: The form with the date fields.
    :return: (ok, error_message)
    """
    needed_form_fields = {"start_month", "end_month"}

    if not set(form.keys()).issuperset(needed_form_fields):
        return (
            False,
            f"Não contém todos os campos necessários: {needed_form_fields}",
        )

    start_year_month = form.get("start_month")
    end_year_month = form.get("end_month")

    if not valid_year_month_format(start_year_month) or not valid_year_month_format(
        end_year_month
    ):
        return False, "Formatos de data inválidos"

    start_year, start_month = map(int, start_year_month.split("-"))
    end_year, end_month = map(int, end_year_month.split("-"))

    if (end_year, end_month) < (start_year, start_month):
        return (
            False,
            "A data final deve ser maior que a data inicial",
        )

    today_year, today_month = date.today().year, date.today().month
    if (end_year, end_month) > (today_year, today_month):
        return False, "A data final deve ser anterior a data de hoje."

    return True, None


def get_dates_from_form(form: Dict[str, str]) -> Tuple[date, date]:
    start_year_month = form.get("start_month")
    end_year_month = form.get("end_month")
    start_year, start_month = map(int, start_year_month.split("-"))
    end_year, end_month = map(int, end_year_month.split("-"))
    return start_year, start_month, end_year, end_month


@main_page_bp.route("/att-viz", methods=["POST"])
def att_viz():

    ok, err = validate_form_dates(request.form)
    if not ok:
        return Response(err, status.HTTP_400_BAD_REQUEST)

    start_year, start_month, end_year, end_month = get_dates_from_form(request.form)

    try:
        df_acidentes = get_df_acidentes(start_year, start_month, end_year, end_month)
    except Exception as e:
        return Response(
            f"""Erro ao conectar com servidor de dados de acidentes.""",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    try:
        df_vendas = get_df_vendas(start_year, start_month, end_year, end_month)
    except Exception as e:
        return Response(
            f"""Erro ao conectar com servidor de dados de vendas.""",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    
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


@api_bp.route("/acidentes", methods=["GET"])
def get_accidents():
    ok, err = validate_form_dates(request.form)
    if not ok:
        return Response(err, status.HTTP_400_BAD_REQUEST)
    start_year, start_month, end_year, end_month = get_dates_from_form(request.form)
    df_acidentes = get_df_acidentes(start_year, start_month, end_year, end_month)

    return df_acidentes.to_json(orient="records")

@api_bp.route("/vendas", methods=["GET"])
def get_sales():
    ok, err = validate_form_dates(request.form)
    if not ok:
        return Response(err, status.HTTP_400_BAD_REQUEST)
    start_year, start_month, end_year, end_month = get_dates_from_form(request.form)
    df_vendas = get_df_vendas(start_year, start_month, end_year, end_month)

    return df_vendas.to_json(orient="records")

@api_bp.route("/grafico-vendas-por-mes", methods = ["GET"])
def get_sales_per_month():
    ok, err = validate_form_dates(request.form)
    if not ok:
        return Response(err, status.HTTP_400_BAD_REQUEST)

    start_year, start_month, end_year, end_month = get_dates_from_form(request.form)
    df_vendas = get_df_vendas(start_year, start_month, end_year, end_month)
    vendas_per_month_fig = plot_vendas_per_month(df_vendas)

    image_binary = vendas_per_month_fig.to_image(format="jpeg")

    return send_file(
                io.BytesIO(image_binary),
                mimetype='image/jpeg',
                as_attachment=True,
                attachment_filename='vendas-por-mes.jpg')

@api_bp.route("/grafico-acidentes-fatais-por-mes", methods = ["GET"])
def get_fatal_accidents_per_month():
    ok, err = validate_form_dates(request.form)
    if not ok:
        return Response(err, status.HTTP_400_BAD_REQUEST)

    start_year, start_month, end_year, end_month = get_dates_from_form(request.form)
    df_acidentes = get_df_acidentes(start_year, start_month, end_year, end_month)
    acidentes_fatais_fig = plot_acidentes_with_filters(
        df_acidentes, [-1, 1, -1, -1], title="Acidentes fatais por mês"
    )

    image_binary = acidentes_fatais_fig.to_image(format="jpeg")

    return send_file(
                io.BytesIO(image_binary),
                mimetype='image/jpeg',
                as_attachment=True,
                attachment_filename='acidentes-fatais-por-mes.jpg')

@api_bp.route("/grafico-acidentes-por-mes", methods = ["GET"])
def get_accidents_per_month():
    ok, err = validate_form_dates(request.form)
    if not ok:
        return Response(err, status.HTTP_400_BAD_REQUEST)

    start_year, start_month, end_year, end_month = get_dates_from_form(request.form)
    df_acidentes = get_df_acidentes(start_year, start_month, end_year, end_month)
    acidentes_per_month = plot_acidentes_per_month(df_acidentes, True)

    image_binary = acidentes_per_month.to_image(format="jpeg")

    return send_file(
                io.BytesIO(image_binary),
                mimetype='image/jpeg',
                as_attachment=True,
                attachment_filename='acidentes-por-mes.jpg')

@api_bp.route("/grafico-acidentes-versus-vendas", methods = ["GET"])
def get_accidents_versus_sales():
    ok, err = validate_form_dates(request.form)
    if not ok:
        return Response(err, status.HTTP_400_BAD_REQUEST)

    start_year, start_month, end_year, end_month = get_dates_from_form(request.form)
    df_acidentes = get_df_acidentes(start_year, start_month, end_year, end_month)
    df_vendas = get_df_vendas(start_year, start_month, end_year, end_month)
    acid_vendas_fig = plot_acidentes_versus_vendas(df_acidentes, df_vendas)

    image_binary = acid_vendas_fig.to_image(format="jpeg")

    return send_file(
                io.BytesIO(image_binary),
                mimetype='image/jpeg',
                as_attachment=True,
                attachment_filename='acidentes-versus-vendas.jpg')

@api_bp.route("/docs", methods = ["GET"])
def get_docs():
    return render_template("docs.html")

def valid_year_month_format(year_month):
    match = bool(re.match(r"\d\d\d\d\-\d\d", year_month))
    if not match:
        return False
    _, month = map(int, year_month.split("-"))
    return 0 <= month <= 12
