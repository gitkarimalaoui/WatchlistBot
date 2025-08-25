from intelligence.prompt_optimizer_lyra import optimize_prompt


def main() -> None:
    test_data = {
        "symbol": "AVXL",
        "prix": 3.45,
        "float_shares": 12_000_000,
        "volume": 1_500_000,
        "variation": "+67%",
        "news": "FDA approval",
        "pattern": "cassure haussière sur gros volume",
    }

    prompt_brut = f"Score ce ticker selon les données : {test_data}"
    contexte = {
        "ia": "ChatGPT",
        "style": "DÉTAILLÉ",
        "objectif": "évaluation IA de trading pour penny stock biotech",
    }

    prompt_ameliore = optimize_prompt(prompt_brut, contexte)

    print("=== PROMPT OPTIMISÉ ===\n")
    print(prompt_ameliore)


if __name__ == "__main__":
    main()
