from flask import (
    Flask, render_template, Blueprint, flash
)

route = Blueprint('login', __name__)


@route.route('/', methods=['GET'])
def auth():
    return render_template('login.html', id_app=0)
