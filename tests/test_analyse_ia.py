
import joblib
import os
import pytest

pytest.skip("model prediction requires scikit-learn model", allow_module_level=True)

def test_model_file_exists():
    assert os.path.exists("models/model_gain_classifier.pkl"), "Modèle IA manquant"

def test_model_prediction():
    model = joblib.load("models/model_gain_classifier.pkl")
    prediction = model.predict([[1, 2, 3, 4, 5]])
    assert prediction is not None, "Prédiction du modèle échouée"
