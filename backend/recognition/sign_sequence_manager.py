"""
Task 2.1 — ISL Sign Sequence Manager
Tracks sign sequence per user, detects sentence boundaries, forms text.
"""
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

PAUSE_SECONDS = 2.5   # treat silence > this as sentence end


class SignSequence:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.signs: List[Dict] = []
        self.last_time: Optional[datetime] = None
        self.sentences_formed = 0
        self.total_signs = 0

    # ── public ──────────────────────────────────────────────────────────────

    def add_sign(self, label: str, confidence: float = 1.0) -> Dict:
        now = datetime.now()
        # Detect pause → finalise current sentence first
        completed_sentence = None
        if self.signs and self._paused(now):
            completed_sentence = self._form_sentence()
            self.sentences_formed += 1
            self.signs = []

        self.signs.append({'sign': label, 'confidence': confidence, 'ts': now})
        self.last_time = now
        self.total_signs += 1

        return {
            'sign_added': label,
            'current_sequence': self.sign_labels(),
            'sequence_length': len(self.signs),
            'sentence_complete': completed_sentence is not None,
            'sentence_text': completed_sentence,
        }

    def flush(self) -> Optional[str]:
        """Force-complete current sequence (called when user presses Send)."""
        if not self.signs:
            return None
        text = self._form_sentence()
        self.sentences_formed += 1
        self.signs = []
        return text

    def sign_labels(self) -> List[str]:
        return [s['sign'] for s in self.signs]

    def clear(self):
        self.signs = []
        self.last_time = None

    def stats(self) -> Dict:
        return {
            'user_id': self.user_id,
            'total_signs': self.total_signs,
            'current_length': len(self.signs),
            'sentences_formed': self.sentences_formed,
            'is_paused': self._paused(datetime.now()) if self.last_time else False,
        }

    # ── private ─────────────────────────────────────────────────────────────

    def _paused(self, now: datetime) -> bool:
        if not self.last_time:
            return False
        return (now - self.last_time).total_seconds() >= PAUSE_SECONDS

    def _form_sentence(self) -> str:
        words = [s['sign'].replace('_', ' ').lower() for s in self.signs]
        sentence = ' '.join(words)
        return sentence[0].upper() + sentence[1:] + ('.' if sentence[-1] not in '.!?' else '')


class SignSequenceManager:
    def __init__(self):
        self._store: Dict[str, SignSequence] = {}

    def _seq(self, user_id: str) -> SignSequence:
        if user_id not in self._store:
            self._store[user_id] = SignSequence(user_id)
        return self._store[user_id]

    def add_sign(self, user_id: str, label: str, confidence: float = 1.0) -> Dict:
        return self._seq(user_id).add_sign(label, confidence)

    def flush(self, user_id: str) -> Optional[str]:
        return self._seq(user_id).flush()

    def get_signs(self, user_id: str) -> List[str]:
        return self._seq(user_id).sign_labels()

    def clear(self, user_id: str):
        self._seq(user_id).clear()

    def stats(self, user_id: str) -> Dict:
        return self._seq(user_id).stats()


_mgr = None

def get_sequence_manager() -> SignSequenceManager:
    global _mgr
    if _mgr is None:
        _mgr = SignSequenceManager()
    return _mgr
