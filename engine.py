from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer, util
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict

_NLP = spacy.load("en_core_web_sm", disable=["parser", "tagger", "lemmatizer"])
_NLP.add_pipe("sentencizer")
_SENT_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def _compute_semantic_similarity(text: str, query: str) -> float:
    return util.pytorch_cos_sim(
        _SENT_MODEL.encode(query, convert_to_tensor=True),
        _SENT_MODEL.encode(text, convert_to_tensor=True)
    ).item()

def _compute_entity_density(text: str) -> float:
    doc = _NLP(text[:1000])
    return len(list(doc.ents)) / max(1, len(doc)) if doc else 0

def _compute_lexical_overlap(texts: List[str], query: str) -> List[float]:
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        tfidf = vectorizer.fit_transform(texts + [query])
        sims = (tfidf[:-1] * tfidf[-1].T).toarray().flatten()
        max_sim = max(sims) if max(sims) > 0 else 1
        return [s / max_sim for s in sims]
    except:
        return [0.0] * len(texts)

def _compute_text_quality_score(text: str) -> float:
    if not text.strip():
        return 0
    length_score = min(len(text) / 500, 1)
    sents = text.split('.')
    avg_len = np.mean([len(s.split()) for s in sents if s.strip()]) if sents else 0
    struct_score = min(avg_len / 15, 1) if avg_len else 0
    words = text.split()
    diversity = len(set(words)) / len(words) if words else 0
    return (length_score + struct_score + diversity) / 3

def _refine_text(text: str, max_len=800) -> str:
    doc = _NLP(text)
    sents = list(doc.sents)
    scored = []
    for i, sent in enumerate(sents):
        txt = sent.text.strip()
        pos_score = 1 - (i / len(sents)) * 0.3
        ent_score = _compute_entity_density(txt)
        len_score = 1 - abs(len(txt) - 100) / 200
        scored.append((pos_score + ent_score + len_score, txt))
    scored.sort(reverse=True)
    result = ""
    for _, s in scored:
        if len(result + s) <= max_len:
            result += s + " "
        else:
            break
    return result.strip()

def rank_and_refine_sections(
    sections: List[dict], persona: str, job: str, top_k: int = 5
) -> Tuple[List[dict], List[dict]]:
    query = f"Persona: {persona}. Task: {job}"
    texts = [s["text"] for s in sections]

    sem = [_compute_semantic_similarity(t, query) for t in texts]
    lex = _compute_lexical_overlap(texts, query)
    ent = [_compute_entity_density(t) for t in texts]
    qual = [_compute_text_quality_score(t) for t in texts]

    def norm(x): return (np.array(x) - min(x)) / (max(x) - min(x) + 1e-6)

    score = (
        0.5 * norm(sem) +
        0.25 * norm(lex) +
        0.15 * norm(ent) +
        0.10 * norm(qual)
    )

    picks = []
    used_docs = set()
    all_by_score = sorted(range(len(sections)), key=lambda i: score[i], reverse=True)
    for idx in all_by_score:
        doc = sections[idx]["document"]
        if doc not in used_docs or len(picks) >= top_k:
            picks.append(idx)
            used_docs.add(doc)
        if len(picks) == top_k:
            break

    extracted = []
    refined = []
    for rank, idx in enumerate(picks, 1):
        sec = sections[idx]
        extracted.append({
            "document": sec["document"],
            "section_title": sec["title"],
            "importance_rank": rank,
            "page_number": sec["page"]
        })
        refined.append({
            "document": sec["document"],
            "refined_text": _refine_text(sec["text"]),
            "page_number": sec["page"]
        })

    return extracted, refined
