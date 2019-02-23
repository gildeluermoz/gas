from flask import (
    Flask, render_template, Blueprint, flash, session
)

route = Blueprint('login', __name__)


@route.route('/', methods=['GET'])
def auth():
    next = ''
    if 'url' in session:
        next = session['url']
    return render_template('login.html', id_app=0, next=next)
