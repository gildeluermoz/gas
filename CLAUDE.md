# GAS - Groupements d'Achats Solidaires

Application web de gestion de commandes groupées pour des associations de consommateurs (inspirée des GAS italiens). Déployée sur `commandes2.senspresses.fr`.

## Stack technique

- **Backend :** Flask (Python) + PostgreSQL (SQLAlchemy 1.4)
- **Frontend :** Bootstrap 4, jQuery, DataTables, Font Awesome, Toastr
- **PDF :** WeasyPrint
- **Auth :** pypnusershub (JWT via cookie)
- **Formulaires :** WTForms + Flask-Bootstrap
- **Déploiement :** Gunicorn + Supervisor, derrière nginx en reverse proxy

## Architecture

Pattern **Blueprint par module** avec un `GenericRepository` abstrait (CRUD de base). Templates Jinja2.

### Modules (Blueprints)

| Module | Chemin | Rôle |
|--------|--------|------|
| `t_users` | `app/t_users/` | Gestion des utilisateurs |
| `t_groups` | `app/t_groups/` | Gestion des relais (points de distribution) |
| `t_deliveries` | `app/t_deliveries/` | Gestion des livraisons + PDF |
| `t_products` | `app/t_products/` | Catalogue produits par livraison |
| `t_orders` | `app/t_orders/` | Commandes (coeur de l'appli, ~1000 LOC) |
| `t_profils` | `app/t_profils/` | Gestion des rôles/permissions |
| `login` | `app/login/` | Page de connexion |
| `pypnusershub` | `app/pypnusershub/` | Auth, sessions, décorateurs |

### Fichiers clés

- `server.py` - Initialisation Flask, enregistrement des blueprints
- `app/models.py` - Tous les modèles SQLAlchemy
- `app/genericRepository.py` - Classe abstraite CRUD (get_one, get_all, post, update, delete)
- `config/config.py` - Configuration Flask (DB, URL, secrets, feature flags)
- `config/settings.ini` - Paramètres d'installation (PostgreSQL, Gunicorn)

## Base de données (schéma `gas`)

- **t_users** - Utilisateurs (UUID, identifiant, mot de passe bcrypt, lié à un group)
- **t_groups** - Relais/points de distribution (nom, responsable, email, tel)
- **t_deliveries** - Livraisons (date, date limite commande, remise %, frais de port)
- **t_products** - Produits par livraison (nom, unité, prix achat/vente, poids)
- **t_orders** - Table de jonction group x product (quantité, remise par groupe)
- **t_profils** - Types de rôles
- **cor_user_profil** - Association utilisateur-rôle
- **Vues :** `v_orders_result`, `v_group_orders_detail`, `v_group_orders_sum` (agrégation/marges)

## Permissions (profils)

| Profil | Rôle | Droits |
|--------|------|--------|
| 2 | Adhérent | Voir son profil, commander pour son relais |
| 3 | Responsable relais | + gérer les commandes de son relais, voir ses membres |
| 4 | Gestionnaire | + CRUD livraisons/produits, remises, voir tous les utilisateurs |
| 6 | Super Admin | Accès total (utilisateurs, groupes, profils, tout) |

Protection des routes via `@fnauth.check_auth(min_profil_id, ...)`.

## Logique métier

- Les **produits sont liés à une livraison** (les prix varient d'une livraison à l'autre), avec duplication possible
- **Remises par relais** configurables (0% à 100%)
- Calcul automatique de la **rentabilité** (prix achat vs. vente)
- Commandes **verrouillées** après la date de livraison
- Impossible de supprimer un produit ayant des commandes associées
- Export **CSV** et génération **PDF** (commandes, livraisons, bandelettes par relais)

## Commandes utiles

- `install_app.sh` - Installation complète (venv, deps, npm, supervisor)
- `install_db.sh` - Création du schéma PostgreSQL
- `gunicorn_start.sh` - Lancement du serveur de production
- `data/gas.sql` / `data/gas-data.sql` - Schéma et données de seed
