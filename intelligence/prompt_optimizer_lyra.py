from typing import Dict, Optional


def optimize_prompt(prompt: str, contexte: Optional[Dict[str, str]] = None) -> str:
    """Optimise dynamiquement un prompt IA selon la méthode Lyra.

    Parameters
    ----------
    prompt : str
        Le prompt brut généré par un module du bot.
    contexte : dict, optional
        Dictionnaire optionnel contenant ``ia``, ``style`` et ``objectif``.

    Returns
    -------
    str
        Prompt optimisé prêt à être utilisé.
    """

    if contexte is None:
        contexte = {}

    ia = contexte.get("ia", "ChatGPT")
    style = contexte.get("style", "BASIQUE")
    objectif = contexte.get("objectif", "optimisation IA trading")

    prompt_optimise = f"""Vous êtes Lyra, une experte en optimisation de prompts IA.

Objectif : {objectif}
IA ciblée : {ia}
Mode : {style}

Prompt original :
{prompt}

Tâches :
- Reformulez ce prompt pour maximiser la précision, la clarté et l’efficacité
- Assurez-vous qu’il soit compréhensible par l’IA et adapté au domaine du trading
- Ne rien ajouter d’inutile

Votre prompt optimisé :
"""

    return prompt_optimise.strip()
