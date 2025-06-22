import json
from pathlib import Path
from typing import List

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from stable_baselines3 import PPO

# Default paths for pretrained models
MISTRAL_MODEL_PATH = Path("models/mistral")
FINRL_AGENT_PATH = Path("models/finrl/trained_agent.zip")


def charger_modele_mistral() -> AutoModelForSequenceClassification:
    """Load the local Mistral model if available."""
    model = AutoModelForSequenceClassification.from_pretrained(MISTRAL_MODEL_PATH)
    return model


def charger_tokenizer_mistral() -> AutoTokenizer:
    """Load Mistral tokenizer from HuggingFace."""
    return AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")


def predire_mistral(texte: str) -> torch.Tensor:
    """Generate logits for the given text using Mistral."""
    tokenizer = charger_tokenizer_mistral()
    model = charger_modele_mistral()
    inputs = tokenizer(texte, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.logits


def charger_agent_finrl(env) -> PPO:
    """Load a FinRL-trained agent for evaluation."""
    return PPO.load(FINRL_AGENT_PATH, env=env)


def entrainer_modele_supervise(dataset_path: str, output_dir: str) -> None:
    """Placeholder supervised training pipeline for Mistral.

    Args:
        dataset_path: Path to a JSONL file with ``text`` and ``label`` fields.
        output_dir: Directory to save the trained model.
    """
    tokenizer = charger_tokenizer_mistral()
    model = charger_modele_mistral()

    # Simple example training loop; expects small dataset
    texts: List[str] = []
    labels: List[int] = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            texts.append(record["text"])
            labels.append(int(record["label"]))

    encodings = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    dataset = torch.utils.data.TensorDataset(encodings.input_ids, encodings.attention_mask, torch.tensor(labels))
    loader = torch.utils.data.DataLoader(dataset, batch_size=2, shuffle=True)

    optimiser = torch.optim.AdamW(model.parameters(), lr=5e-5)
    model.train()
    for epoch in range(1):
        for input_ids, attention_mask, batch_labels in loader:
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=batch_labels)
            loss = outputs.loss
            loss.backward()
            optimiser.step()
            optimiser.zero_grad()

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)


def evaluer_modele_ia(env) -> float:
    """Evaluate the FinRL agent in the given environment and return the mean reward."""
    agent = charger_agent_finrl(env)
    obs = env.reset()
    total_reward = 0.0
    done = False
    while not done:
        action, _ = agent.predict(obs, deterministic=True)
        obs, reward, done, _info = env.step(action)
        total_reward += reward
    return float(total_reward)
