import torch
import models.ia_supervisee_trainer as trainer


class DummyModel:
    def __call__(self, **kwargs):
        class Out:
            logits = torch.tensor([[0.1, -0.2]])
        return Out()


class DummyTokenizer:
    def __call__(self, text, return_tensors=None):
        return {"input_ids": torch.tensor([[1, 2]]), "attention_mask": torch.tensor([[1, 1]])}


def test_mistral_prediction(monkeypatch):
    monkeypatch.setattr(trainer, "charger_tokenizer_mistral", lambda: DummyTokenizer())
    monkeypatch.setattr(trainer, "charger_modele_mistral", lambda: DummyModel())
    logits = trainer.predire_mistral("Signal achat fort")
    assert isinstance(logits, torch.Tensor)
