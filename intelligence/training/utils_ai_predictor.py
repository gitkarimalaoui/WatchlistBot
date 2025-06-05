import joblib
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_absolute_error

def entrainer_modele_classification(df):
    if "resultat" not in df.columns:
        raise ValueError("Colonne 'resultat' manquante dans le DataFrame")
    X = df.drop(columns=["resultat"])
    y = df["resultat"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modele = LogisticRegression(max_iter=1000)
    modele.fit(X_train, y_train)
    y_pred = modele.predict(X_test)
    rapport = classification_report(y_test, y_pred, output_dict=True)
    return modele, rapport

def entrainer_modele_regression(df):
    if "gain_net" not in df.columns:
        raise ValueError("Colonne 'gain_net' manquante dans le DataFrame")
    X = df.drop(columns=["gain_net"])
    y = df["gain_net"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modele = LinearRegression()
    modele.fit(X_train, y_train)
    y_pred = modele.predict(X_test)
    erreur = mean_absolute_error(y_test, y_pred)
    return modele, erreur

def sauvegarder_modele(model, filepath):
    joblib.dump(model, filepath)

def charger_modele(filepath):
    return joblib.load(filepath)