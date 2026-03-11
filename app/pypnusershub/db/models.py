# coding: utf8

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

'''
mappings applications et utilisateurs
'''

import hashlib
from bcrypt import checkpw

from flask_sqlalchemy import SQLAlchemy

from flask import current_app

from sqlalchemy.orm import relationship
from sqlalchemy import Sequence, func
db = current_app.config['DB']

def fn_check_password(self, pwd):
    if (current_app.config['PASS_METHOD'] == 'hash'):
        if not self._password_plus:
            raise ValueError('User %s has no password' % (self.identifiant))
        return checkpw(pwd.encode('utf8'), self._password_plus.encode('utf8'))
    else:
        raise ValueError('Undefine crypt method (PASS_METHOD)')

class User(db.Model):
    __tablename__ = 't_users'
    __table_args__ = {'schema': 'gas'}

    TABLE_ID = Sequence(
        't_users_id_seq',
        schema="gas",
    )
    id_user = db.Column(
        db.Unicode,
        TABLE_ID,
        primary_key=True,
    )

    # TODO: make that unique ?
    identifiant = db.Column(db.Unicode)
    last_name = db.Column(db.Unicode)
    first_name = db.Column(db.Unicode)
    user_comment = db.Column(db.Unicode)
    _password_plus = db.Column('pass_plus', db.Unicode)
    email = db.Column(db.Unicode)
    id_group = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    date_insert = db.Column(db.DateTime)
    date_update = db.Column(db.DateTime)

    # applications_droits = db.relationship('AppUser', lazy='joined')

    @property
    def password(self):
        if (current_app.config['PASS_METHOD'] == 'hash'):
            return self._password_plus
        else:
            raise

    # TODO: change password digest algorithm for something stronger such
    # as bcrypt. This need to be done at usershub level first.
    # @password.setter
    # def password(self, pwd):
    #     self._password = hashlib.md5(pwd.encode('utf8')).hexdigest()
    
    check_password = fn_check_password

    def to_json(self):
        out = {
            'id': self.id_user,
            'login': self.identifiant,
            'email': self.email,
            'applications': []
        }
        for app_data in self.applications_droits:
            app = {
                'id': app_data.application_id,
                'nom': 'gas',
                'niveau': app_data.id_profil
            }
            out['applications'].append(app)
        return out

    def __repr__(self):
        return "<User '{!r}' id='{}'>".format(self.identifiant, self.id_user)

    def __str__(self):
        return self.identifiant or ''

    def as_dict(self, recursif=False, columns=()):
        last_name = self.last_name or ''
        first_name = self.first_name or ''
        return {
            'id_user': self.id_user,
            'identifiant': self.identifiant,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'nom_complet': last_name+' '+first_name
        }


class AppUser(db.Model):
    '''
    Droits des utilisateurs
    '''
    __tablename__ = 'v_userslist_for_gas'
    __table_args__ = {'schema': 'gas'}

    id_user = db.Column(
        db.Unicode,
        db.ForeignKey('gas.t_users.id_user'),
        primary_key=True
    )
    user = relationship("User", backref="app_users")
    id_application = db.Column(
        db.Integer,
        primary_key=True
    )
    identifiant = db.Column(db.Unicode)
    _password_plus = db.Column('pass_plus', db.Unicode)
    id_profil = db.Column(db.Integer, primary_key=True)
    id_group = db.Column(db.Integer)

    @property
    def password(self):
        return self._password

    check_password = fn_check_password


    def as_dict(self):
        cols = (c for c in self.__table__.columns if (c.name != 'pass_plus'))
        return {c.name: getattr(self, c.name) for c in cols}

    def __repr__(self):
        return "<AppUser user='{}' app='{}'>".format(
            self.id_user, self.id_application
        )
    
