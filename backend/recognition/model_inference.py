"""
ML Model for ISL Recognition
Conv1D + BiLSTM + Multi-Head Attention
"""
import os
import pickle
from django.conf import settings


class ISLRecognitionModel:
    """ISL Recognition Model Inference"""
    
    def __init__(self):
        self.model = None
        self.sign_labels = []
        # Don't load model during Django startup - lazy load on first prediction
    
    def load_model(self):
        """Load trained model and metadata"""
        if self.model is not None:
            return  # Already loaded
            
        try:
            import tensorflow as tf
            import numpy as np
            
            model_path = settings.MODEL_PATH
            metadata_path = os.path.join(settings.BASE_DIR, 'metadata.pkl')
            
            # Load metadata with sign labels
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    self.sign_labels = metadata.get('sign_list', [])
                    print(f"✅ Loaded {len(self.sign_labels)} sign labels from metadata")
            else:
                print(f"⚠️ Metadata file not found at {metadata_path}")
                # Fallback to old labels if metadata missing
                self.sign_labels = [
                    'Beautiful', 'Blind', 'Deaf', 'Happy', 
                    'Quiet', 'Sad', 'Ugly', 'Loud'
                ]
            
            # Load model
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                print(f"✅ Model loaded from {model_path}")
                print(f"   Input shape: {self.model.input_shape}")
                print(f"   Output shape: {self.model.output_shape}")
                print(f"   Expected {len(self.sign_labels)} classes")
            else:
                print(f"⚠️ Model file not found at {model_path}")
                print("📝 Creating dummy model for testing...")
                self.model = self._create_dummy_model()
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
    
    def _create_dummy_model(self):
        """Create a dummy model for testing (when real model not available)"""
        import tensorflow as tf
        from tensorflow.keras import layers, Model
        
        num_classes = len(self.sign_labels) if self.sign_labels else 136
        
        # Same architecture as research paper
        inputs = layers.Input(shape=(32, 468))
        
        # Conv1D layers
        x = layers.Conv1D(128, kernel_size=3, activation='relu', padding='same')(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Conv1D(128, kernel_size=5, activation='relu', padding='same')(x)
        x = layers.BatchNormalization()(x)
        
        # BiLSTM
        x = layers.Bidirectional(layers.LSTM(128, return_sequences=True))(x)
        
        # Multi-Head Self-Attention
        x = layers.MultiHeadAttention(num_heads=4, key_dim=64)(x, x)
        
        # Global pooling
        x = layers.GlobalAveragePooling1D()(x)
        
        # Dense layers
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(num_classes, activation='softmax')(x)
        
        model = Model(inputs, outputs)
        print(f"📝 Dummy model created with {num_classes} output classes (untrained)")
        
        return model
    
    def predict(self, features):
        """
        Predict ISL sign from features
        Args:
            features: numpy array of shape (32, 468)
        Returns:
            dict with sign_label and confidence_score
        """
        import numpy as np
        
        # Lazy load model on first prediction
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            return {
                'sign_label': 'Error',
                'confidence_score': 0.0,
                'error': 'Model not loaded'
            }
        
        try:
            # Add batch dimension
            features_batch = np.expand_dims(features, axis=0)
            
            # Predict
            predictions = self.model.predict(features_batch, verbose=0)
            
            # Get top prediction
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            
            # Get top 5 predictions for debugging
            top_5_indices = np.argsort(predictions[0])[-5:][::-1]
            all_predictions = {
                self.sign_labels[i]: float(predictions[0][i]) 
                for i in top_5_indices
            }
            
            # Check confidence threshold
            if confidence < settings.CONFIDENCE_THRESHOLD:
                return {
                    'sign_label': 'Uncertain',
                    'confidence_score': confidence,
                    'all_predictions': all_predictions,
                    'message': f'Low confidence ({confidence:.2%}). Please try again.'
                }
            
            return {
                'sign_label': self.sign_labels[predicted_class],
                'confidence_score': confidence,
                'all_predictions': all_predictions
            }
            
        except Exception as e:
            return {
                'sign_label': 'Error',
                'confidence_score': 0.0,
                'error': str(e)
            }


# Global model instance (loaded once)
_model_instance = None


def get_model():
    """Get or create model instance (singleton)"""
    global _model_instance
    if _model_instance is None:
        _model_instance = ISLRecognitionModel()
    return _model_instance
