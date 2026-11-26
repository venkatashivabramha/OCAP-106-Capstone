
# Conversational ISL Recognition API Wrapper
# Adds semantic layer on top of base model

import json
from pathlib import Path

class ConversationalISLRecognizer:
    """Wraps base model with conversational vocabulary"""
    
    def __init__(self):
        # Load conversational vocabulary
        vocab_path = Path(__file__).parent / "models" / "conversational_vocabulary_extended.json"
        with open(vocab_path) as f:
            self.vocab = json.load(f)
        
        # Create reverse mapping (sign ? concepts)
        self.sign_to_concepts = {}
        for category, concepts in self.vocab.items():
            for concept, data in concepts.items():
                sign = data['sign']
                if sign not in self.sign_to_concepts:
                    self.sign_to_concepts[sign] = []
                self.sign_to_concepts[sign].append({
                    'concept': concept,
                    'category': data['category'],
                    'tier': data.get('tier', 1)
                })
        
        print(f"? Loaded conversational vocabulary: {len(self.sign_to_concepts)} base signs")
    
    def recognize_conversational(self, base_prediction, confidence=0.0):
        """
        Convert base model prediction to conversational concepts
        
        Args:
            base_prediction: Base sign (e.g., 'H', 'T', '1')
            confidence: Model confidence score
            
        Returns:
            List of possible conversational meanings
        """
        if base_prediction not in self.sign_to_concepts:
            return [{
                'text': base_prediction,
                'category': 'finger_spell',
                'tier': 1,
                'confidence': confidence
            }]
        
        # Get all possible meanings
        concepts = self.sign_to_concepts[base_prediction]
        
        # Sort by tier (Tier 1 = highest priority)
        concepts_sorted = sorted(concepts, key=lambda x: x['tier'])
        
        # Format results
        results = []
        for concept in concepts_sorted[:5]:  # Top 5 meanings
            results.append({
                'text': concept['concept'].replace('_', ' ').title(),
                'category': concept['category'],
                'tier': concept['tier'],
                'base_sign': base_prediction,
                'confidence': confidence
            })
        
        return results
    
    def get_suggestions(self, context_signs=[]):
        """Get suggestions based on conversation context"""
        # Simple context-aware suggestions
        if not context_signs:
            # Default: common greetings
            return ['Hello', 'Hi', 'Thank You', 'Please', 'Yes', 'No']
        
        last_sign = context_signs[-1] if context_signs else None
        
        # Context-based suggestions
        suggestions_map = {
            'H': ['How are you?', 'Happy', 'Help', 'Home'],
            'W': ['What', 'Where', 'When', 'Water', 'Want'],
            'T': ['Thank you', 'Today', 'Tomorrow', 'Tired'],
            'Y': ['Yes', 'You', 'Your'],
            'N': ['No', 'Now', 'Need', 'Night'],
        }
        
        return suggestions_map.get(last_sign, ['OK', 'Yes', 'No'])

# Example usage
if __name__ == "__main__":
    recognizer = ConversationalISLRecognizer()
    
    # Test base sign ? conversational meanings
    test_signs = ['H', 'T', 'W', 'Y', 'N', 'S', 'M']
    
    for sign in test_signs:
        results = recognizer.recognize_conversational(sign, confidence=0.95)
        print(f"\nSign '{sign}' can mean:")
        for r in results:
            print(f"  - {r['text']} ({r['category']}, tier {r['tier']})")
