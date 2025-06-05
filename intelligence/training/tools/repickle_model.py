import joblib

# Charger l'ancien modèle
model = joblib.load('modele_ia.pkl')
# Re-sauvegarder pour assurer compatibilité de pickle
joblib.dump(model, 'modele_ia_refreshed.pkl')
print("✔ Modèle repicklé et sauvegardé sous 'modele_ia_refreshed.pkl'")
