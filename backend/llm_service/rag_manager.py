"""
Task 2.3 — RAG Manager
Keyword-based context retrieval from ISL knowledge base.
In production, swap search() for ChromaDB + sentence-transformers embeddings.
"""
from typing import List, Dict
from pathlib import Path
import json, logging

logger = logging.getLogger(__name__)

KB_PATH = Path(__file__).parent / 'isl_knowledge_base.json'

DEFAULT_KB = {
    "signs": [
        {"sign":"HELLO",     "meaning":"greeting",    "usage":"Start conversation"},
        {"sign":"THANK_YOU", "meaning":"gratitude",   "usage":"Express thanks"},
        {"sign":"HELP",      "meaning":"assistance",  "usage":"Request help"},
        {"sign":"YES",       "meaning":"affirmation", "usage":"Agree / confirm"},
        {"sign":"NO",        "meaning":"negation",    "usage":"Disagree / refuse"},
        {"sign":"SORRY",     "meaning":"apology",     "usage":"Apologise"},
        {"sign":"PLEASE",    "meaning":"politeness",  "usage":"Polite request"},
        {"sign":"GOOD",      "meaning":"positive",    "usage":"Express satisfaction"},
        {"sign":"BAD",       "meaning":"negative",    "usage":"Express dissatisfaction"},
        {"sign":"HAPPY",     "meaning":"emotion",     "usage":"Express happiness"},
        {"sign":"SAD",       "meaning":"emotion",     "usage":"Express sadness"},
        {"sign":"LOVE",      "meaning":"emotion",     "usage":"Express affection"},
        {"sign":"EAT",       "meaning":"action",      "usage":"Eating food"},
        {"sign":"DRINK",     "meaning":"action",      "usage":"Drinking"},
        {"sign":"GO",        "meaning":"movement",    "usage":"Going somewhere"},
        {"sign":"COME",      "meaning":"movement",    "usage":"Coming here"},
        {"sign":"WAIT",      "meaning":"action",      "usage":"Please wait"},
        {"sign":"STOP",      "meaning":"action",      "usage":"Stop something"},
        {"sign":"NAME",      "meaning":"identity",    "usage":"Asking/giving name"},
        {"sign":"FINISH",    "meaning":"completion",  "usage":"Completed something"},
    ],
    "phrases": [
        {"phrase":"How are you?",         "signs":["HOW","YOU"],       "ctx":"greeting"},
        {"phrase":"Thank you very much",  "signs":["THANK_YOU","VERY"],"ctx":"gratitude"},
        {"phrase":"I need help",          "signs":["I","NEED","HELP"], "ctx":"assistance"},
        {"phrase":"What is your name?",   "signs":["WHAT","YOUR","NAME"],"ctx":"intro"},
        {"phrase":"Nice to meet you",     "signs":["NICE","MEET","YOU"],"ctx":"greeting"},
    ],
}


class RAGManager:
    def __init__(self):
        self.kb: Dict = {}
        self._load()

    def _load(self):
        if KB_PATH.exists():
            try:
                with open(KB_PATH, encoding='utf-8') as f:
                    self.kb = json.load(f)
                logger.info(f"RAG: loaded {len(self.kb.get('signs',[]))} signs from {KB_PATH}")
                return
            except Exception as e:
                logger.warning(f"RAG load failed: {e}")
        self.kb = DEFAULT_KB
        try:
            KB_PATH.write_text(json.dumps(self.kb, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception:
            pass

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        q = set(query.upper().split())
        results = []

        for s in self.kb.get('signs', []):
            score = 10 if s['sign'] in q else 0
            score += len(q & set(s['sign'].split('_'))) * 2
            if s['meaning'].upper() in query.upper():
                score += 3
            if score:
                results.append(('sign', s, score))

        for p in self.kb.get('phrases', []):
            phrase_signs = set(p['signs'])
            score = len(q & phrase_signs) * 3
            if score:
                results.append(('phrase', p, score))

        results.sort(key=lambda x: x[2], reverse=True)
        return [{'type': t, 'content': c} for t, c, _ in results[:top_k]]

    def context_string(self, query: str) -> str:
        hits = self.search(query, top_k=3)
        if not hits:
            return ''
        lines = ['Relevant ISL context:']
        for h in hits:
            if h['type'] == 'sign':
                s = h['content']
                lines.append(f"  - {s['sign']}: {s['meaning']} ({s['usage']})")
            else:
                p = h['content']
                lines.append(f"  - Phrase \"{p['phrase']}\" → signs: {', '.join(p['signs'])}")
        return '\n'.join(lines)

    def stats(self) -> Dict:
        return {
            'total_signs':   len(self.kb.get('signs', [])),
            'total_phrases': len(self.kb.get('phrases', [])),
        }


_mgr = None

def get_rag_manager() -> RAGManager:
    global _mgr
    if _mgr is None:
        _mgr = RAGManager()
    return _mgr
