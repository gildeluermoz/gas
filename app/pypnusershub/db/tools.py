# coding: utf8

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)
"""
    DB tools not related to any model in particular.
"""

from flask import current_app

from sqlalchemy.orm.exc import NoResultFound
import sqlalchemy as sa

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          SignatureExpired, BadSignature)

from app.pypnusershub.db import models, db
from app.pypnusershub.utils import text_resource_stream


class AccessRightsError(Exception):
    pass


class CruvedImplementationError(Exception):
    pass


class InsufficientRightsError(AccessRightsError):
    pass


class AccessRightsExpiredError(AccessRightsError):
    pass


class UnreadableAccessRightsError(AccessRightsError):
    pass


def init_schema(con_uri):

    with text_resource_stream('schema.sql', 'pypnusershub.db') as sql_file:
        sql = sql_file.read()

    engine = sa.create_engine(con_uri)
    with engine.connect():
        engine.execute(sql)
        engine.execute("COMMIT")


def delete_schema(con_uri):

    engine = sa.create_engine(con_uri)
    with engine.connect():
        engine.execute("DROP SCHEMA IF EXISTS utilisateurs CASCADE")
        engine.execute("COMMIT")


def reset_schema(con_uri):
    delete_schema(con_uri)
    init_schema(con_uri)


def load_fixtures(con_uri):
    with text_resource_stream('fixtures.sql', 'pypnusershub.db') as sql_file:

        engine = sa.create_engine(con_uri)
        with engine.connect():
            for line in sql_file:
                if line.strip():
                    engine.execute(line)
            engine.execute("COMMIT")


def user_from_token(token=None, secret_key=None):
    """Given a, authentification token, return the matching AppUser instance"""
    secret_key = secret_key or current_app.config['SECRET_KEY']

    try:
        s = Serializer(current_app.config['SECRET_KEY'])
        if token is not None:
            data = s.loads(token)
            id_user = data['id_user']
            id_app = data['id_application']
            return (models.AppUser
                        .query
                        .filter(models.AppUser.id_user == id_user)
                        .filter(models.AppUser.id_application == id_app)
                        .one())
        else:
            return (models.AppUser
                      .query
                      .filter(models.AppUser.id_user == "0")
                      .filter(models.AppUser.id_application == "0")
                      .one())

    except NoResultFound:
        raise UnreadableAccessRightsError(
            'No user withd id "{}" for app "{}"'.format(id_user, id_app)
        )
    except SignatureExpired:
        raise AccessRightsExpiredError("Token expired")

    except BadSignature:
        raise UnreadableAccessRightsError('Token BadSignature', 403)
