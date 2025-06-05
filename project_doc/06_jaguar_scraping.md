# EPIC 06 – Jaguar Scraping 📰🤖

| Clé | Valeur |
|-----|--------|
| **Projet** | WatchlistBot V7 |
| **Version** | V7.03 |
| **EPIC** | 06 – Jaguar Scraping |
| **Objectif** | Récupérer quotidiennement les tickers détectés par DrJaguar (Forum) puis les insérer proprement dans la base `watchlist` avec provenance = “Jaguar”. |

---

## User-Stories (fichier `user_stories_epic_06.json`)

| ID | En tant que | Je veux | Afin de |
|----|-------------|--------|---------|
| **TUS006-1** | Bot | Scraper les nouveaux messages du forum DrJaguar | Alimenter la watch-list sans effort manuel |
| **TUS006-2** | Bot | Détecter et extraire les tickers (regex `[A-Z]{1,5}\.US` → `TICK`) | Standardiser le format |
| **TUS006-3** | Bot | Filtrer les doublons (déjà présents dans `watchlist`) | Éviter les entrées redondantes |
| **TUS006-4** | Bot | Valider le ticker via API Finnhub / yFinance | Ne garder que les tickers réellement listés |
| **TUS006-5** | Système | Logger chaque run dans `scrape_log` (OK / erreurs) | Audit & debug |
| **TUS006-6** | Trader | Lancer le scraping depuis l’UI (`🔄 Jaguar Scraping`) | Rafraîchir la liste en un clic |
| **TUS006-7** | UI | Afficher le nombre de tickers ajoutés + liens vers la source | Transparence et traçabilité |

---

## Schéma BPMN

Le diagramme se trouve dans `project_doc/images/bpmn_epic_06_jaguar_scraping.png`.  
(Legende : pools = *Trader / UI-Streamlit / Bot / DB*.)

![Jaguar Scraping BPMN](images/bpmn_epic_06_jaguar_scraping.png)

---

## Scripts / Modules

| Fichier | Rôle principal |
|---------|----------------|
| `scripts/scraper_jaguar.py` | Récupère le fil DrJaguar, parse les tickers |
| `scripts/load_watchlist.py` | Insère les tickers validés dans `watchlist` |
| `ui/app_unifie_watchlistbot.py` | Bouton « 🔄 Jaguar Scraping » ← déjà en place |
| `db/schema.sql` | Table `scrape_log` (id, run_at, added, errors) |

---

## Done / To Do

- ✅ BPMN validé (EPIC 05)
- 🟡 **En cours : EPIC 06**  
  - [ ] Implémentation `scraper_jaguar.py` v1  
  - [ ] Tests + Logging  
  - [ ] Marquer BPMN validé (step 08/100)



---

## 📊 Diagramme BPMN

❌ No BPMN diagram available for EPIC 06.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 06](../images/bpmn_epic_06_jaguar_scraping.png)
