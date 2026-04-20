from __future__ import annotations
import re
from functools import lru_cache
from datetime import datetime

def normalize(text):
    return re.sub(r"\s+", " ", text.strip().lower())

def classify_problem(problem):
    p = normalize(problem)
    categories = {
        "renda": ["dinheiro", "renda", "vender", "ganhar", "cliente", "pix"],
        "direcao": ["vida", "rumo", "objetivo", "futuro", "sentido"],
        "trabalho": ["trabalho", "emprego", "chefe", "empresa"],
        "projeto": ["projeto", "app", "codigo", "sistema", "ia"],
        "energia": ["cansado", "preguica", "ansiedade", "trava"],
        "relacao": ["relacionamento", "amizade", "familia", "sozinho"],
    }
    for cat, words in categories.items():
        if any(w in p for w in words):
            return cat
    return "geral"

def score_actions(records, category):
    now = datetime.utcnow()
    buckets = {}
    for r in records:
        if r.get("category") != category:
            continue
        a = r.get("chosen_action")
        s = int(r.get("result_score", 0))
        rep = 1 if r.get("would_repeat") else 0
        ts = r.get("timestamp")
        try:
            age_days = (now - datetime.fromisoformat(ts)).days
        except:
            age_days = 999
        recency = max(0, 30 - age_days) / 30
        buckets.setdefault(a, []).append((s, rep, recency))

    ranked = []
    for a, vals in buckets.items():
        avg = sum(v[0] for v in vals) / len(vals)
        rep = sum(v[1] for v in vals) / len(vals)
        rec = sum(v[2] for v in vals) / len(vals)
        strength = avg * 0.6 + (rep * 10) * 0.3 + (rec * 10) * 0.1
        ranked.append((strength, a))

    ranked.sort(reverse=True)
    return ranked[0][1] if ranked and ranked[0][0] >= 6 else None

@lru_cache(maxsize=1000)
def predict(problem, goal, pain, today, records_tuple):
    records = list(records_tuple)
    category = classify_problem(problem)

    actions_map = {
        "renda": [
            f"Criar oferta mínima: {goal}",
            "Falar com 1 cliente real hoje",
            "Testar venda imediata"
        ],
        "direcao": [
            f"Executar 30 min: {goal}",
            f"Fazer menor passo: {today}",
            "Testar ao invés de pensar"
        ],
        "trabalho": [
            "Criar renda paralela hoje",
            "Reduzir dependência do emprego",
            "Testar nova fonte de renda"
        ],
        "projeto": [
            f"Criar versão mínima: {goal}",
            "Definir entrada/saída",
            "Testar com 1 pessoa"
        ],
        "energia": [
            f"Executar micro passo: {today}",
            f"Atacar o ponto travado: {pain}",
            "Ignorar o todo e agir"
        ],
        "relacao": [
            f"Falar direto sobre: {pain}",
            "Escrever em 3 linhas",
            "Perguntar ao invés de assumir"
        ],
        "geral": [
            f"Quebrar problema: {problem}",
            f"Executar versão mínima: {goal}",
            "Testar com alguém"
        ],
    }

    actions = actions_map.get(category, actions_map["geral"]).copy()
    learned = score_actions(records, category)
    if learned:
        actions[0] = learned

    return {
        "category": category,
        "actions": actions[:3],
        "confidence": 0.75
    }
