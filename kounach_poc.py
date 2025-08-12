import streamlit as st
from datetime import date, datetime
import pandas as pd

# ------------------------
# POC Streamlit — BOTV8 (Kounach + Références Inde)
# ------------------------
# - Bilingue FR/AR (l'arabe en RTL)
# - Données mockées en mémoire (session_state)
# - Kounach: clients, mouvements, encaissements
# - Téléchargement CSV
# - Page d'inspiration (Khatabook / OkCredit / BharatPe)
# ------------------------

st.set_page_config(page_title="BOTV8 – POC Kounach", layout="wide")

# ===== i18n =====
I18N = {
    "fr": {
        "title": "BOTV8 – POC Kounach",
        "lang": "Langue",
        "home": "Accueil",
        "kounach": "Kounach (crédit famille)",
        "clients": "Clients",
        "ledger": "Grand livre",
        "collections": "Encaissements",
        "reports": "Rapports & KPI",
        "settings": "Paramètres",
        "india": "Références Inde (Khatabook / OkCredit / BharatPe)",
        "add_client": "Ajouter un client",
        "name": "Nom",
        "phone": "Téléphone",
        "limit": "Plafond (MAD)",
        "balance": "Solde (MAD)",
        "due": "Prochaine échéance",
        "kyc": "Niveau KYC",
        "notes": "Notes",
        "save": "Enregistrer",
        "edit": "Modifier",
        "delete": "Supprimer",
        "select_client": "Sélectionner un client",
        "entry": "Nouvelle écriture",
        "date": "Date",
        "label": "Libellé",
        "amount": "Montant (MAD)",
        "add_entry": "Ajouter l'écriture",
        "success_add": "Écriture ajoutée.",
        "encaisser": "Encaisser (Carte/Wallet/Cash - mock)",
        "encaisser_ok": "Encaissement simulé — solde remis à 0.",
        "export_csv": "Exporter CSV",
        "clients_table": "Table des clients",
        "ledger_table": "Grand livre (mouvements)",
        "collections_table": "Historique encaissements",
        "seed": "Recharger données d'exemple",
        "n1": "N1 (≤ 1 000 MAD/jour)",
        "n2": "N2 (≤ 5 000 MAD/jour)",
        "search": "Recherche",
        "filters": "Filtres",
        "from": "Du",
        "to": "Au",
        "generate": "Générer",
        "kpis": "Indicateurs clés",
        "total_outstanding": "Encours total (MAD)",
        "top_clients": "Top clients par solde",
        "payments_month": "Encaissements ce mois (MAD)",
        "product": "Produit",
        "add_purchase": "Ajouter l'achat",
        "client_total": "Total par client",
        "regler_compte": "Régler compte",
        "reset_ok": "Compte remis à zéro.",
        "rtl_css": """
            <style>
                [dir="rtl"] * { direction: rtl; text-align: right; }
            </style>
        """,
        "india_md": """
### Pourquoi ces références ?
Ces applications indiennes ciblent les micro-commerçants avec des fonctions proches du **kounach** marocain.

**Khatabook**  
- Grand livre clients (udhar), rappels WhatsApp/SMS, encaissement UPI/QR.  
- Freemium, monétisation via services (paiements, crédit marchand).

**OkCredit**  
- Ledger simple, multi-langues, relances automatisées, synchronisation multi-appareils.  
- Gratuit pour l'acquisition, services payants additionnels.

**BharatPe**  
- Acceptation QR (UPI), SoftPOS/TPE, offre de **crédit marchand** basée sur flux.  
- Modèle MDR faible, subventionné par services financiers.

**Adaptation Maroc**  
- Rails: cartes locales + wallets + (bientôt) **eMAD**.  
- KYC gradué (N1/N2) et plafonds d'encaissement.  
- Prévoir pré-autorisation pour cafés (fin de mois) et module facture.
        """
    },
    "ar": {
        "title": "BOTV8 – نموذج الكناش",
        "lang": "اللغة",
        "home": "الرئيسية",
        "kounach": "الكناش (دفتر دَين العائلة)",
        "clients": "الزبناء",
        "ledger": "الدفتر",
        "collections": "التحصيل",
        "reports": "التقارير والمؤشرات",
        "settings": "الإعدادات",
        "india": "مراجع الهند (Khatabook / OkCredit / BharatPe)",
        "add_client": "إضافة زبون",
        "name": "الاسم",
        "phone": "الهاتف",
        "limit": "السقف (درهم)",
        "balance": "الرصيد (درهم)",
        "due": "الاستحقاق القادم",
        "kyc": "مستوى التحقق",
        "notes": "ملاحظات",
        "save": "حفظ",
        "edit": "تعديل",
        "delete": "حذف",
        "select_client": "اختر الزبون",
        "entry": "قيد جديد",
        "date": "التاريخ",
        "label": "الوصف",
        "amount": "المبلغ (درهم)",
        "add_entry": "إضافة القيد",
        "success_add": "تمت إضافة القيد.",
        "encaisser": "تحصيل (بطاقة/محفظة/نقدي – تجريبي)",
        "encaisser_ok": "تم التحصيل شكلياً — تصفير الرصيد.",
        "export_csv": "تصدير CSV",
        "clients_table": "جدول الزبناء",
        "ledger_table": "الدفتر (الحركات)",
        "collections_table": "سجل التحصيل",
        "seed": "تحميل بيانات تجريبية",
        "n1": "المستوى 1 (≤ 1000 درهم/يوم)",
        "n2": "المستوى 2 (≤ 5000 درهم/يوم)",
        "search": "بحث",
        "filters": "مرشحات",
        "from": "من",
        "to": "إلى",
        "generate": "إنشاء",
        "kpis": "المؤشرات الرئيسية",
        "total_outstanding": "إجمالي الديون (درهم)",
        "top_clients": "أفضل الزبناء حسب الرصيد",
        "payments_month": "التحصيل هذا الشهر (درهم)",
        "product": "المنتج",
        "add_purchase": "إضافة الشراء",
        "client_total": "المجموع للزبون",
        "regler_compte": "تصفية الحساب",
        "reset_ok": "تم تصفير الحساب.",
        "rtl_css": """
            <style>
                [dir="rtl"] * { direction: rtl; text-align: right; }
            </style>
        """,
        "india_md": """
### لماذا هذه المراجع؟
تركّز هذه التطبيقات الهندية على صغار التجّار بوظائف قريبة من **الكناش** المغربي.

**Khatabook**  
- دفتر ديون للعملاء، تذكير عبر واتساب/SMS، تحصيل عبر QR.  
- نموذج Freemium وخدمات مدفوعة إضافية.

**OkCredit**  
- دفتر بسيط متعدد اللغات، تذكير آلي، مزامنة.  
- مجاني للاكتساب، مع خدمات مدفوعة لاحقاً.

**BharatPe**  
- قبول QR وSoftPOS، **تمويل التاجر** اعتماداً على التدفقات.  
- عمولات منخفضة، تعويضها بخدمات مالية.

**التكييف للمغرب**  
- السكك: بطاقات + محافظ + قريباً **الدرهم الرقمي**.  
- KYC متدرّج وحدود تحصيل.  
- دعم التفويض المسبق للمقاهي وخيارات الفوترة.
        """
    }
}

if "lang" not in st.session_state:
    st.session_state.lang = "fr"

# Lang selector
colL, colR = st.columns([6,2])
with colR:
    lang_choice = st.selectbox(I18N[st.session_state.lang]["lang"], ["FR","AR"], index=0 if st.session_state.lang=="fr" else 1)
    st.session_state.lang = "fr" if lang_choice=="FR" else "ar"
L = I18N[st.session_state.lang]

# Apply RTL for Arabic
if st.session_state.lang == "ar":
    st.markdown(f'<div dir="rtl"></div>', unsafe_allow_html=True)
    st.markdown(L["rtl_css"], unsafe_allow_html=True)

st.title(L["title"])

# ===== Seed data =====
SEED_CLIENTS = [
    {"id":"c1","nom":"Famille A","tel":"06 11 22 33 44","plafond":1000,"solde":120,"echeance":str(date.today()),"kycLevel":"N1","notes":""},
    {"id":"c2","nom":"Famille B","tel":"06 22 33 44 55","plafond":1500,"solde":0,"echeance":str(date.today()),"kycLevel":"N2","notes":"voisin"},
    {"id":"c3","nom":"Voisin C","tel":"06 33 44 55 66","plafond":800,"solde":60,"echeance":str(date.today()),"kycLevel":"N1","notes":""},
]
SEED_MOVES = [
    {"id":"m1","clientId":"c1","date":str(date.today()),"libelle":"Pain & Lait","montant":20},
    {"id":"m2","clientId":"c1","date":str(date.today()),"libelle":"Sucre","montant":10},
    {"id":"m3","clientId":"c3","date":str(date.today()),"libelle":"Huile","montant":60},
]
SEED_COLL = []

if "clients" not in st.session_state:
    st.session_state.clients = SEED_CLIENTS.copy()
if "moves" not in st.session_state:
    st.session_state.moves = SEED_MOVES.copy()
if "colls" not in st.session_state:
    st.session_state.colls = SEED_COLL.copy()
if "kounach_data" not in st.session_state:
    st.session_state.kounach_data = {}

# Helpers

def find_client(cid: str):
    for c in st.session_state.clients:
        if c["id"] == cid:
            return c
    return None

# Sidebar menu
menu = st.sidebar.radio("Menu", [L["home"], L["kounach"], L["clients"], L["ledger"], L["collections"], L["reports"], L["india"], L["settings"]])

# HOME
if menu == L["home"]:
    st.success("POC prêt : gérez vos clients Kounach, ajoutez des écritures et encaissez en fin de mois (simulation).")
    st.info("Astuce : changez la langue en haut à droite. L'arabe s'affiche en RTL.")
    st.button(L["seed"], on_click=lambda: (st.session_state.update({"clients":SEED_CLIENTS.copy(),"moves":SEED_MOVES.copy(),"colls":SEED_COLL.copy(),"kounach_data":{}})))

# KOUNACH PAGE
elif menu == L["kounach"]:
    st.subheader(L["kounach"])
    cids = {f"{c['nom']} ({c['tel']})": c["id"] for c in st.session_state.clients}
    selected = st.selectbox(L["select_client"], list(cids.keys()))
    cid = cids[selected]
    with st.form("achat_form", clear_on_submit=True):
        prod = st.text_input(L["product"], "")
        amt = st.number_input(L["amount"], min_value=0.0, value=0.0, step=1.0)
        d = st.date_input(L["date"], value=date.today())
        submitted = st.form_submit_button(L["add_purchase"])
        if submitted and prod:
            mid = f"m{len(st.session_state.moves)+1}"
            st.session_state.moves.append({"id":mid,"clientId":cid,"date":str(d),"libelle":prod,"montant":amt})
            c = find_client(cid)
            if c:
                c["solde"] = float(c.get("solde",0)) + float(amt)
            st.success(L["success_add"])
    client_moves = [m for m in st.session_state.moves if m["clientId"]==cid]
    dfm = pd.DataFrame(client_moves)
    st.dataframe(dfm.sort_values("date", ascending=False), use_container_width=True)
    total = sum([m["montant"] for m in client_moves])
    st.write(f"{L['client_total']}: {total:.2f} MAD")
    if st.button(L["regler_compte"], disabled=total<=0):
        coll_id = f"r{len(st.session_state.colls)+1}"
        st.session_state.colls.append({"id":coll_id,"clientId":cid,"date":str(date.today()),"moyen":"N/A","montant":total})
        mid = f"m{len(st.session_state.moves)+1}"
        st.session_state.moves.append({"id":mid,"clientId":cid,"date":str(date.today()),"libelle":L["regler_compte"],"montant":-total})
        client = find_client(cid)
        if client:
            client["solde"] = 0.0
        st.success(L["reset_ok"])

# CLIENTS
elif menu == L["clients"]:
    st.subheader(L["clients"])
    with st.expander(L["add_client"], expanded=False):
        cols = st.columns(3)
        with cols[0]:
            nom = st.text_input(L["name"], "")
            tel = st.text_input(L["phone"], "")
            kyc = st.selectbox(L["kyc"], ["N1","N2"])
        with cols[1]:
            plafond = st.number_input(L["limit"], min_value=0.0, value=1000.0, step=50.0)
            solde = st.number_input(L["balance"], min_value=0.0, value=0.0, step=10.0)
        with cols[2]:
            echeance = st.date_input(L["due"], value=date.today())
            notes = st.text_input(L["notes"], "")
        if st.button(L["save"]):
            new_id = f"c{len(st.session_state.clients)+1}"
            st.session_state.clients.append({"id":new_id,"nom":nom,"tel":tel,"plafond":plafond,"solde":solde,"echeance":str(echeance),"kycLevel":kyc,"notes":notes})
            st.success("Client ajouté.")
    dfc = pd.DataFrame(st.session_state.clients)
    st.dataframe(dfc, use_container_width=True)
    csv = dfc.to_csv(index=False).encode('utf-8')
    st.download_button(L["export_csv"], data=csv, file_name="clients.csv", mime="text/csv")

# LEDGER
elif menu == L["ledger"]:
    st.subheader(L["ledger"])
    cids = {f"{c['nom']} ({c['tel']})": c["id"] for c in st.session_state.clients}
    selected = st.selectbox(L["select_client"], list(cids.keys()))
    cid = cids[selected]
    colA, colB, colC, colD = st.columns([1,1,2,1])
    with colA:
        d = st.date_input(L["date"], value=date.today())
    with colB:
        amt = st.number_input(L["amount"], min_value=0.0, value=10.0, step=1.0)
    with colC:
        lib = st.text_input(L["label"], "")
    with colD:
        if st.button(L["add_entry"]):
            mid = f"m{len(st.session_state.moves)+1}"
            st.session_state.moves.append({"id":mid,"clientId":cid,"date":str(d),"libelle":lib,"montant":amt})
            c = find_client(cid)
            if c:
                c["solde"] = float(c.get("solde",0)) + float(amt)
            st.success(L["success_add"])
    dfm = pd.DataFrame([m for m in st.session_state.moves if m["clientId"]==cid])
    st.dataframe(dfm.sort_values("date", ascending=False), use_container_width=True)

# COLLECTIONS
elif menu == L["collections"]:
    st.subheader(L["collections"])
    cids = {f"{c['nom']} ({c['tel']})": c["id"] for c in st.session_state.clients}
    selected = st.selectbox(L["select_client"], list(cids.keys()))
    cid = cids[selected]
    client = find_client(cid)
    solde_actuel = float(client["solde"]) if client else 0.0
    st.info(f"Solde actuel: {solde_actuel:.2f} MAD")
    moyen = st.selectbox("Moyen", ["Carte","Wallet","Cash"])
    if st.button(L["encaisser"], disabled=solde_actuel<=0):
        coll_id = f"r{len(st.session_state.colls)+1}"
        st.session_state.colls.append({"id":coll_id,"clientId":cid,"date":str(date.today()),"moyen":moyen,"montant":solde_actuel})
        client["solde"] = 0.0
        mid = f"m{len(st.session_state.moves)+1}"
        st.session_state.moves.append({"id":mid,"clientId":cid,"date":str(date.today()),"libelle":"Encaissement (mock)","montant":-solde_actuel})
        st.success(L["encaisser_ok"])
    dfc = pd.DataFrame(st.session_state.colls)
    st.dataframe(dfc.sort_values("date", ascending=False), use_container_width=True)
    if not dfc.empty:
        csv = dfc.to_csv(index=False).encode('utf-8')
        st.download_button(L["export_csv"], data=csv, file_name="encaissements.csv", mime="text/csv")

# REPORTS
elif menu == L["reports"]:
    st.subheader(L["reports"])
    encours = sum([float(c["solde"]) for c in st.session_state.clients])
    mois = datetime.today().strftime('%Y-%m')
    encaisse_mois = sum([float(r["montant"]) for r in st.session_state.colls if r["date"].startswith(mois)])
    col1, col2 = st.columns(2)
    col1.metric(L["total_outstanding"], f"{encours:.2f}")
    col2.metric(L["payments_month"], f"{encaisse_mois:.2f}")
    top_df = pd.DataFrame(sorted(st.session_state.clients, key=lambda x: x["solde"], reverse=True)[:10])
    st.caption(L["top_clients"])
    st.dataframe(top_df[["nom","tel","solde","plafond","kycLevel"]], use_container_width=True)

# INDIA REFERENCES
elif menu == L["india"]:
    st.subheader(L["india"])
    st.markdown(I18N[st.session_state.lang]["india_md"])

# SETTINGS
elif menu == L["settings"]:
    st.subheader(L["settings"])
    st.write("POC sans backend. Paramètres indicatifs uniquement.")
    st.selectbox(L["kyc"], [L["n1"], L["n2"]])
    st.number_input("Frais TPE (affichage)", min_value=0.0, value=0.3, step=0.1, help="% indicatif pour la démo")
    st.checkbox("Activer reçus PDF (prochaine itération)", value=False)
