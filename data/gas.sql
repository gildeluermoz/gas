--Run this script with the database owner
SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--Ensure to have uuid-ossp extension installed before running this script
--You must be superuser to add an extension in your database 
--CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS gas;

SET search_path = gas, pg_catalog;

-------------
--FUNCTIONS--
-------------

CREATE OR REPLACE FUNCTION modify_date_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.date_insert := now();
    NEW.date_update := now();
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION modify_date_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.date_update := now();
    RETURN NEW;
END;
$$;

SET default_tablespace = '';
SET default_with_oids = false;

----------------------
--TABLES & SEQUENCES--
----------------------
CREATE TABLE IF NOT EXISTS t_profils (
    id_profil serial NOT NULL,
    profil_code character varying(20),
    profil_name character varying(255),
    profil_comment text
);
COMMENT ON TABLE t_profils IS 'Users profil. To define users permissions';


CREATE TABLE IF NOT EXISTS t_groups (
    id_group serial NOT NULL,
    group_name character varying(50) NOT NULL,
    group_leader character varying(100),
    group_comment text,
    group_main_email character varying(250),
    group_main_tel character varying(250),
    active boolean DEFAULT true,
    date_insert timestamp without time zone,
    date_update timestamp without time zone
);


CREATE TABLE IF NOT EXISTS t_users (
    id_user serial NOT NULL,
    id_group integer,
    identifiant character varying(100),
    first_name character varying(50),
    last_name character varying(50),
    pass_plus text,
    email character varying(250),
    user_comment text,
    active boolean DEFAULT true,
    date_insert timestamp without time zone,
    date_update timestamp without time zone
);

CREATE TABLE IF NOT EXISTS cor_user_profil (
    id_user integer NOT NULL,
    id_profil integer NOT NULL
);

CREATE TABLE IF NOT EXISTS t_deliveries (
    id_delivery serial NOT NULL,
    delivery_name character varying(50),
    delivery_date date,
    delivery_discount decimal DEFAULT 0,
    delivery_comment text,
    active boolean DEFAULT true,
    date_insert timestamp without time zone,
    date_update timestamp without time zone
);


CREATE TABLE IF NOT EXISTS t_products (
    id_product serial NOT NULL,
    id_delivery integer NOT NULL,
    product_name character varying(50),
    buying_price decimal NOT NULL,
    selling_price decimal NOT NULL,
    case_weight integer NOT NULL,
    product_comment text,
    active boolean DEFAULT true
);


CREATE TABLE IF NOT EXISTS t_orders (
    id_group integer NOT NULL,
    id_product integer NOT NULL,
    product_case_number integer NOT NULL,
    date_insert timestamp without time zone,
    date_update timestamp without time zone
);


----------------
--PRIMARY KEYS--
----------------
ALTER TABLE ONLY t_profils ADD CONSTRAINT pk_t_profils PRIMARY KEY (id_profil);

ALTER TABLE ONLY t_groups ADD CONSTRAINT pk_t_groups PRIMARY KEY (id_group);

ALTER TABLE ONLY t_users ADD CONSTRAINT pk_t_users PRIMARY KEY (id_user);

ALTER TABLE ONLY cor_user_profil ADD CONSTRAINT pk_cor_user_profil PRIMARY KEY (id_user, id_profil);

ALTER TABLE ONLY t_deliveries ADD CONSTRAINT pk_t_deliveries PRIMARY KEY (id_delivery);

ALTER TABLE ONLY t_products ADD CONSTRAINT pk_t_products PRIMARY KEY (id_product);

ALTER TABLE ONLY t_orders ADD CONSTRAINT pk_t_orders PRIMARY KEY (id_group, id_product);


------------
--TRIGGERS--
------------
CREATE TRIGGER tri_modify_date_insert_t_groups BEFORE INSERT ON t_groups FOR EACH ROW EXECUTE PROCEDURE modify_date_insert();
CREATE TRIGGER tri_modify_date_update_t_groups BEFORE UPDATE ON t_groups FOR EACH ROW EXECUTE PROCEDURE modify_date_update();

CREATE TRIGGER tri_modify_date_insert_t_users BEFORE INSERT ON t_users FOR EACH ROW EXECUTE PROCEDURE modify_date_insert();
CREATE TRIGGER tri_modify_date_update_t_users BEFORE UPDATE ON t_users FOR EACH ROW EXECUTE PROCEDURE modify_date_update();

CREATE TRIGGER tri_modify_date_insert_t_deliveries BEFORE INSERT ON t_deliveries FOR EACH ROW EXECUTE PROCEDURE modify_date_insert();
CREATE TRIGGER tri_modify_date_update_t_deliveries BEFORE UPDATE ON t_deliveries FOR EACH ROW EXECUTE PROCEDURE modify_date_update();

CREATE TRIGGER tri_modify_date_insert_t_orders BEFORE INSERT ON t_orders FOR EACH ROW EXECUTE PROCEDURE modify_date_insert();
CREATE TRIGGER tri_modify_date_update_t_orders BEFORE UPDATE ON t_orders FOR EACH ROW EXECUTE PROCEDURE modify_date_update();


----------------
--FOREIGN KEYS--
----------------
ALTER TABLE ONLY t_users ADD CONSTRAINT t_users_id_group_fkey FOREIGN KEY (id_group) REFERENCES t_groups(id_group) ON UPDATE CASCADE;

ALTER TABLE ONLY cor_user_profil ADD CONSTRAINT cor_user_profil_id_profil_fkey FOREIGN KEY (id_profil) REFERENCES t_profils(id_profil) ON UPDATE CASCADE;
ALTER TABLE ONLY cor_user_profil ADD CONSTRAINT cor_user_profil_id_user_fkey FOREIGN KEY (id_user) REFERENCES t_users(id_user) ON UPDATE CASCADE;

ALTER TABLE ONLY t_products ADD CONSTRAINT t_products_id_delivery_fkey FOREIGN KEY (id_delivery) REFERENCES t_deliveries(id_delivery) ON UPDATE CASCADE;

ALTER TABLE ONLY t_orders ADD CONSTRAINT t_orders_id_group_fkey FOREIGN KEY (id_group) REFERENCES t_groups(id_group) ON UPDATE CASCADE;
ALTER TABLE ONLY t_orders ADD CONSTRAINT t_orders_id_product_fkey FOREIGN KEY (id_product) REFERENCES t_products(id_product) ON UPDATE CASCADE;


---------
--VIEWS--
---------
CREATE OR REPLACE VIEW gas.v_userslist_for_gas AS (
SELECT u.id_user, 0 as id_application, u.identifiant, u.pass_plus, c.id_profil
FROM gas.t_users u
JOIN gas.cor_user_profil c ON c.id_user = u.id_user
WHERE u.active = true
);

-- DROP VIEW gas.v_group_orders_sum;
-- DROP VIEW gas.v_orders_result;
-- DROP VIEW gas.v_group_orders_detail;


CREATE OR REPLACE VIEW gas.v_group_orders_detail AS
SELECT 
  d.id_delivery, 
  g.id_group, 
  d.delivery_name, 
  g.group_name, 
  p.id_product, 
  p.product_name, 
  o.product_case_number, 
  p.selling_price * o.product_case_number AS selling_price, 
  p.buying_price * o.product_case_number AS buying_price,
  p.case_weight  * o.product_case_number AS weight
FROM gas.t_orders o
JOIN gas.t_groups g ON g.id_group = o.id_group
JOIN gas.t_products p ON p.id_product = o.id_product
JOIN gas.t_deliveries d ON d.id_delivery = p.id_delivery
ORDER BY d.id_delivery, p.id_product, g.id_group;

CREATE OR REPLACE VIEW gas.v_group_orders_sum AS
SELECT id_delivery, id_group, delivery_name, group_name, sum(selling_price) AS total
FROM gas.v_group_orders_detail
GROUP BY id_delivery, id_group, delivery_name, group_name;

CREATE OR REPLACE VIEW gas.v_orders_result AS
SELECT 
  v.id_delivery,
  v.id_product, 
  v.delivery_name,
  d.delivery_discount, 
  v.product_name, 
  sum(v.product_case_number) AS case_number, 
  sum(v.selling_price) AS selling_price,
  sum(v.buying_price-(v.buying_price*COALESCE(d.delivery_discount,0))) AS buying_price,
  sum(v.selling_price) - sum(v.buying_price-(v.buying_price*COALESCE(d.delivery_discount,0))) AS benefice,
  sum(v.weight) as weight
FROM gas.v_group_orders_detail v
JOIN gas.t_deliveries d ON d.id_delivery = v.id_delivery
GROUP BY v.id_delivery, v.id_product, v.delivery_name, d.delivery_discount, v.product_name;