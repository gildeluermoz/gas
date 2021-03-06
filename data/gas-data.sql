----------------
--MINIMAL DATA--
----------------

SET search_path = gas, pg_catalog;

-- Insert administrator 
INSERT INTO t_groups (id_group, group_name, group_comment, active) VALUES
(0,'Aucun','Relais par défaut. Permet de créer un utilisateur qui n''appartient à aucun relais.',TRUE);
SELECT pg_catalog.setval('t_groups_id_group_seq', (SELECT max(id_group)+1 FROM t_groups), false);

INSERT INTO t_users (id_user, id_group, identifiant, last_name, first_name, user_comment, email, pass_plus) VALUES 
('2734d3f237e741dbae27ba9c2ec04f3a', 0, 'admin', 'Administrateur', 'test', 'administrateur par défaut', NULL, '$2y$13$TMuRXgvIg6/aAez0lXLLFu0lyPk4m8N55NDhvLoUHh/Ar3rFzjFT.')
,('0', 0, NULL, 'non identifié', NULL, 'Utilisateur générique utilisé pour l''accès aux pages non protégées', NULL, NULL)
;

INSERT INTO t_profils (id_profil, profil_code, profil_name, profil_comment) VALUES
(0, '0', 'Aucun', 'Aucun droit')
,(1, '1', 'Lecteur', 'Ne peut que consulter')
,(2, '2', 'Adhérent', 'Il peux écrire ce qui concerne sa commande')
,(3, '3', 'Relais', 'Il peux écrire ce qui concerne les commandes de son relais')
,(4, '4', 'Modérateur', 'Il peut gérer les utilisateurs, les relais, les livraisons et les produits.')
--,(5, '5', 'Validateur', 'Il valide bien sur')
,(6, '6', 'Administrateur', 'Il a tous les droits');
SELECT pg_catalog.setval('t_profils_id_profil_seq', (SELECT max(id_profil)+1 FROM t_profils), false);

INSERT INTO cor_user_profil (id_profil, id_user) VALUES
(6, '2734d3f237e741dbae27ba9c2ec04f3a')
,(0, '0')
;
