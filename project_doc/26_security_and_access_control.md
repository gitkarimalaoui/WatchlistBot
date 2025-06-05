# 📘 Chapitre 26 – Security & Access Control

## 🎯 Objectif de ce module

Assurer la sécurité du système en gérant l’authentification, les autorisations, la gestion des clés et la traçabilité des actions critiques.

## 🧠 Modules et acteurs impliqués

* **UI** : Pages de login, gestion des utilisateurs et rôles
* **Bot** : Authentifie les requêtes API et gère la rotation des clés
* **AI** : Vérifie l’intégrité des appels et anomalies de comportement
* **DB** : Stocke les utilisateurs, rôles, clés chiffrées et logs de sécurité
* **Admin/Security Officer** : Supervise les accès, modifie les permissions

## 🗃️ Tables utilisées

| Table          | Description                                     |
| -------------- | ----------------------------------------------- |
| `users`        | Informations des utilisateurs (hashed password) |
| `roles`        | Définition des rôles et permissions associées   |
| `api_keys`     | Clés API chiffrées et métadonnées               |
| `security_log` | Journal des connexions et actions critiques     |

## 📜 User Stories de cet EPIC

* US-SEC-001 : En tant qu’admin, je veux créer des utilisateurs avec rôles (Admin, Trader, Viewer)
* US-SEC-002 : En tant qu’utilisateur, je veux me connecter via mot de passe + 2FA
* US-SEC-003 : En tant que bot, je veux stocker et chiffrer les clés API
* US-SEC-004 : En tant qu’admin, je veux consulter le journal des connexions (`security_log`)
* US-SEC-005 : En tant que security officer, je veux forcer la rotation des clés API tous les X jours

## ⚙️ Conditions critiques

* Tentative de connexion échouée > 5 fois → temporaire lock user
* Clé API compromise → rotation immédiate et journalisation
* Tentative d’accès non autorisé → log et alerte

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_26_security_access_control.png`

## 🧠 Prompt IA utilisé

```
Generate a BPMN diagram for EPIC 'Security & Access Control' with:
- Swimlanes: UI, Bot, AI, DB, Admin
- Tasks: user auth, 2FA, role assignment, key encryption, log access
- Decisions: auth success? permission ok?
```

## ⚠️ Limites connues

* 2FA non implémentée techniquement
* Pas de SSO ou integration OAuth

## 🔁 Références croisées

| Fonction       | EPIC concerné                   |
| -------------- | ------------------------------- |
| Reporting      | EPIC 25 – Automated Reporting   |
| Initialization | EPIC 01 – System Initialization |

## 💡 Leçon clé

La sécurité et le contrôle d’accès sont essentiels pour protéger les données sensibles et garantir la continuité opérationnelle.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 26](../images/bpmn_epic_26_security_access_control.png)
