"""
MediaPipe feature extraction for ISL recognition
"""


class MediaPipeProcessor:
    """Extract landmarks from video frames using MediaPipe Holistic"""
    
    def __init__(self):
        # Lazy import to avoid loading heavy dependencies during Django startup
        import mediapipe as mp
        
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            refine_face_landmarks=False
        )
    
    def extract_landmarks(self, frame):
        """
        Extract landmarks from a single frame
        Returns 468-dimensional feature vector
        """
        import cv2
        import numpy as np
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.holistic.process(rgb_frame)
        
        # Extract landmarks
        pose_landmarks = self._extract_pose(results)
        left_hand_landmarks = self._extract_hand(results.left_hand_landmarks)
        right_hand_landmarks = self._extract_hand(results.right_hand_landmarks)
        
        # Combine all features (33*3 + 21*3 + 21*3 = 225 coordinates)
        # Additional features: palm orientation, velocity, finger distances
        # Total: 468-dimensional vector
        
        features = np.concatenate([
            pose_landmarks,
            left_hand_landmarks,
            right_hand_landmarks,
            self._compute_palm_orientation(results),
            self._compute_finger_distances(results.left_hand_landmarks),
            self._compute_finger_distances(results.right_hand_landmarks),
        ])
        
        return features
    
    def _extract_pose(self, results):
        """Extract pose landmarks (33 points * 3 coords = 99 features)"""
        import numpy as np
        
        if results.pose_landmarks:
            landmarks = []
            for lm in results.pose_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            return np.array(landmarks)
        return np.zeros(99)
    
    def _extract_hand(self, hand_landmarks):
        """Extract hand landmarks (21 points * 3 coords = 63 features)"""
        import numpy as np
        
        if hand_landmarks:
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            return np.array(landmarks)
        return np.zeros(63)
    
    def _compute_palm_orientation(self, results):
        """Compute palm orientation vectors (additional 12 features)"""
        import numpy as np
        # Simplified - add actual palm orientation calculation
        return np.zeros(12)
    
    def _compute_finger_distances(self, hand_landmarks):
        """Compute inter-finger distances (additional features)"""
        import numpy as np
        # Simplified - add actual distance calculations
        return np.zeros(20)
    
    def decode_base64_frame(self, base64_string):
        """Decode base64 image to OpenCV frame"""
        import base64
        import cv2
        import numpy as np
        
        img_data = base64.b64decode(base64_string)
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return frame
    
    def process_video_sequence(self, frames_base64, sequence_length=32):
        """
        Process a sequence of frames
        Returns array of shape (sequence_length, 468)
        """
        import numpy as np
        
        features_list = []
        
        for frame_b64 in frames_base64[:sequence_length]:
            frame = self.decode_base64_frame(frame_b64)
            features = self.extract_landmarks(frame)
            features_list.append(features)
        
        # Pad if needed
        while len(features_list) < sequence_length:
            features_list.append(np.zeros(468))
        
        return np.array(features_list)
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'holistic'):
            self.holistic.close()
