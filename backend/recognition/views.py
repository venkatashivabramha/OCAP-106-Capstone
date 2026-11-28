from rest_framework.permissions import AllowAny
"""
Sign recognition views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import numpy as np

from .mediapipe_processor import MediaPipeProcessor
from .model_inference import get_model


class RecognizeSignView(APIView):
    permission_classes = [AllowAny]
    """
    Recognize ISL sign from video frame(s)
    Expects base64-encoded image frames
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Don't instantiate processor and model during init
        # They will be lazy-loaded on first request
        self._processor = None
        self._model = None
    
    @property
    def processor(self):
        """Lazy load MediaPipe processor"""
        if self._processor is None:
            self._processor = MediaPipeProcessor()
        return self._processor
    
    @property
    def model(self):
        """Lazy load ML model"""
        if self._model is None:
            self._model = get_model()
        return self._model
    
    def post(self, request):
        """
        POST /api/recognition/recognize/
        Body: {
            "frame": "<base64_image>",  # Single frame
            OR
            "frames": ["<base64_1>", "<base64_2>", ...],  # Multiple frames (up to 32)
        }
        """
        
        # Get frames from request
        single_frame = request.data.get('frame')
        multiple_frames = request.data.get('frames')
        
        if not single_frame and not multiple_frames:
            return Response(
                {'error': 'Either "frame" or "frames" required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Process frames
            if single_frame:
                # Single frame - duplicate to make 32 frames
                frames = [single_frame] * 32
            else:
                # Multiple frames
                frames = multiple_frames
            
            # Extract features using MediaPipe
            features = self.processor.process_video_sequence(frames, sequence_length=32)
            
            # Predict using ML model
            result = self.model.predict(features)
            
            # Check for errors
            if 'error' in result:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'success': True,
                'sign_label': result['sign_label'],
                'confidence_score': result['confidence_score'],
                'all_predictions': result.get('all_predictions', {}),
                'message': result.get('message', f'Recognized: {result["sign_label"]}')
            })
            
        except Exception as e:
            return Response(
                {
                    'error': 'Recognition failed',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
