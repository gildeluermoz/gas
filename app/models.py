import hashlib

from app.env import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import select, func


from flask_bcrypt import (
    generate_password_hash
)

from app.utils.utilssqlalchemy import serializable
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, distinct, and_, desc
from app.genericRepository import GenericRepository
from config import config


"""Fichier contenant les models de la base de données"""


@serializable
class TOrders(GenericRepository):
    """ Classe de correspondance entre la table t_groups et la table t_products"""

    __tablename__ = 't_orders'
    __table_args__= {'schema':'gas'}
    id_group = db.Column(db.Integer,ForeignKey('gas.t_groups.id_group'), primary_key = True)
    id_product = db.Column(db.Integer, ForeignKey('gas.t_products.id_product'),primary_key = True)
    product_case_number = db.Column(db.Integer)

    @classmethod
    def add_cor(cls,id_group, products_number):
        """
        Methode qui ajoute des relations group <-> produits --> nombre de caisses

        Avec pour paramètres un id de group et un id_produit et un nombre de caisse
        """

        dict_add = dict()
        dict_add["id_group"] = id_group
        for p in products_number:
            dict_add["id_product"] = p.id_produit
            dict_add["product_case_number"] = p.product_case_number
            cls.post(dict_add)

    @classmethod
    def del_cor(cls,id_group,ids_product):
        """
        Methode qui supprime des relations group <-> produit

        Avec pour paramètres un id de group et un tableau d'id de produit
        """

        for p in ids_product:
            cls.query.filter(cls.id_group == id_group).filter(cls.id_produit == p).delete()
            db.session.commit()



@serializable
class CorUserProfil(GenericRepository):
    """Classe de correspondance entre la table t_user, t_profils"""

    __tablename__= "cor_user_profil"
    __table_args__={'schema':'gas'}
    id_user = db.Column(db.Integer,ForeignKey('gas.t_users.id_user'), primary_key = True)
    id_profil = db.Column(db.Integer,ForeignKey('gas.t_profils.id_profil'), primary_key = True)

    @classmethod
    def add_cor(cls, ids_user, id_profil):
        dict_add = dict()
        dict_add["id_profil"] = id_profil
        for d in ids_user:
            dict_add["id_user"] = d
            cls.post(dict_add)

    @classmethod
    def del_cor(cls,ids_user, id_profil):
        for d in ids_user:
            cls.query.filter(cls.id_profil == id_profil).filter(cls.id_user == d).delete()
            db.session.commit()


@serializable
class TGroups(GenericRepository):
    """
    Model de la table t_groups
    """

    __tablename__ = 't_groups'
    __table_args__={'schema':'gas', 'extend_existing': True}
    id_group = db.Column(db.Integer, primary_key = True)
    group_name = db.Column(db.Unicode)
    group_leader = db.Column(db.Unicode)
    group_comment = db.Column(db.Unicode)
    group_main_email = db.Column(db.Unicode)
    group_main_tel = db.Column(db.Unicode)
    active = db.Column(db.Boolean)

    @classmethod
    def selectActiveGroups(cls):
        """
        Methode qui retourne un tableau de tuples de id_group et de nom de relais actif
        """
        q = db.session.query(cls)
        q = q.order_by(desc(cls.group_name))
        q = q.filter(TGroups.active == True)
        return [(g.id_group, g.group_name) for g in q.all()]

@serializable
class TUsers(GenericRepository):
    """
    Model de la table t_users
    """

    __tablename__ = 't_users'
    __table_args__={'schema':'gas', 'extend_existing': True}
    id_user = db.Column(db.Integer, primary_key = True)
    id_group =db.Column(db.Unicode, ForeignKey('gas.t_groups.id_group'))
    identifiant = db.Column(db.Unicode)
    last_name = db.Column(db.Unicode)
    first_name = db.Column(db.Unicode)
    user_comment = db.Column(db.Unicode)
    pass_plus = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    active = db.Column(db.Boolean)
    group_rel = relationship("TGroups")


    def fill_password(self, password, password_confirmation):
        (self.pass_plus) = self.set_password( password, password_confirmation)

    @classmethod
    def set_password(cls, password, password_confirmation):
        if not password:
            raise ValueError("Password is null")
        if password != password_confirmation:
            raise ValueError("Password doesn't match")

        try:
            pass_plus = generate_password_hash(password.encode('utf-8')).decode('utf-8')
        except Exception as e:
            raise e

        return (pass_plus)

    def get_full_name(self):
        """
        Methode qui concatène le nom et prénom d'un utilisateur'
        retourne un nom complet
        """

        if self.first_name == None:
            full_name = self.last_name
        else :
            full_name = self.last_name + ' '+ self.first_name
        return full_name

    def as_dict_full_name(self):
        """
        Methode qui ajout le nom complet d'un user au dictionnaire qui le défini
        retourne un dictionnaire d'un utilisateur avec une nouvelle 'full_name'
        """

        full_name = self.get_full_name()
        user_as_dict = self.as_dict()
        user_as_dict['full_name'] = full_name
        return user_as_dict

    @classmethod
    def get_users_in_profil(cls, id_profil):
        """
        Methode qui retourne un dictionnaire des users d'un profil
        Avec pour paramètre un id_profil
        """

        q = db.session.query(cls)
        q = q.order_by(desc(cls.last_name))
        q = q.join(CorUserProfil)
        q = q.filter(id_profil == CorUserProfil.id_profil  ) 
        return [data.as_dict_full_name() for data in q.all()]

    @classmethod
    def get_users_out_profil(cls,id_profil):
        """
        Methode qui retourne un dictionnaire de users n'appartenant pas à un profil
        Avec pour paramètre un id_profil
        """

        q = db.session.query(cls)
        q = q.order_by(desc(cls.last_name))
        subquery = db.session.query(CorUserProfil.id_user).filter(CorUserProfil.id_profil == id_profil)
        q = q.filter(cls.id_user.notin_(subquery))
        #TODO filtrer les users actifs
        return [data.as_dict_full_name() for data in q.all()]


@serializable
class TDeliveries(GenericRepository):
    """
    Model de la table t_deliveries
    """

    __tablename__='t_deliveries'
    __table_args__ = {'schema':'gas', 'extend_existing': True}
    id_delivery = db.Column(db.Integer, primary_key = True)
    delivery_name = db.Column(db.Unicode)
    delivery_date = db.Column(db.Date)
    delivery_comment = db.Column(db.Unicode)
    active = db.Column(db.Boolean)

    @classmethod
    def selectActiveDelivery(cls):
        """
        Methode qui retourne un tableau de tuples de id_delivery et de nom de la livraison
        Avec pour paramètres un id_order et un nom de livraison
        """
        q = db.session.query(cls)
        q = q.order_by(desc(cls.delivery_date))
        q = q.filter(TDeliveries.active == True)
        return [(o.id_delivery, o.delivery_name) for o in q.all()]


@serializable
class TProducts(GenericRepository):

    """
    Model de la table t_products
    """

    __tablename__='t_products'
    __table_args__ = {'schema':'gas', 'extend_existing': True}
    id_product = db.Column(db.Integer, primary_key = True)
    id_delivery =db.Column(db.Unicode, ForeignKey('gas.t_deliveries.id_delivery'))
    product_name = db.Column(db.Unicode)
    buying_price = db.Column(db.Numeric)
    selling_price = db.Column(db.Numeric)
    case_weight = db.Column(db.Integer)
    product_comment = db.Column(db.Unicode)
    active = db.Column(db.Boolean)
    delivery_rel = relationship("TDeliveries")

@serializable
class TProfils(GenericRepository):
    """
    Model de la classe t_profils
    """

    __tablename__ = 't_profils'
    __table_args__ = {'schema':'gas', 'extend_existing': True}
    id_profil = db.Column(db.Integer,primary_key = True)
    profil_code = db.Column(db.Unicode)
    profil_name = db.Column(db.Unicode)
    profil_comment = db.Column(db.Unicode)

    @classmethod
    def choixSelect(cls,profil_code,profil_name):
        """
        Methode qui retourne un tableau de tuples de code profil et de nom de profil
        Avec pour paramètres un code de profil et un nom de profil
        """
        return [(d[profil_code], d[profil_name]) for d in cls.get_all()]
