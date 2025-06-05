
import qlib
from qlib.config import REG_US
from qlib.data import D

# Initialiser Qlib avec les données US stock
qlib.init(provider_uri="qlib_data", region=REG_US)

print("✅ Qlib a été initialisé avec succès.")

# Test : accéder aux données pour un ticker
try:
    df = D.features(["AAPL"], ["$close", "$volume"], freq="day")
    print("✅ Exemple de données disponibles :")
    print(df)
except Exception as e:
    print(f"❌ Erreur d'accès aux données : {e}")
