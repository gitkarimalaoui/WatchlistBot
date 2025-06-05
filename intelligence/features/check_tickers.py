def analyser_ticker(ticker, return_features=False):
    # Simulation d'analyse avec des features factices pour IA
    # Remplace ceci par tes vraies métriques à extraire
    features = {
        "volume": 1_000_000,
        "variation_pct": 12.5,
        "float_ratio": 0.3,
        "news_score": 0.8,
        "volatilite": 1.2
    }
    if return_features:
        return list(features.values())  # Retourne sous forme de vecteur pour sklearn
    return features