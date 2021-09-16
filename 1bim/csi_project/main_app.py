from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

main_page_bp = Blueprint('main_app', __name__, url_prefix='/')


@main_page_bp.route('/')
def welcome():
    return render_template('welcome_page.html') 

@main_page_bp.route('/viz')
def viz():
    return render_template('visualization_page.html')
