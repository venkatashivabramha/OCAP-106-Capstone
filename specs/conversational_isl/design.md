# Conversational ISL Model - Design Specification

## 1. System Architecture

### 1.1 Overall Design
\\\
Data Pipeline:
  Kaggle Dataset (263 signs) → Parquet Reader → Landmark Extractor
                                                        ↓
                                            NumPy Arrays (32×468)
                                                        ↓
                                                Sign Filter (140)
                                                        ↓
                                            Train/Val/Test Split
                                                        ↓
  Training Pipeline → BiLSTM Model (140 classes) → Validation
                                                        ↓
                                            Checkpoint Best Model
                                                        ↓
                                                Deploy to Backend
                                                        ↓
                                            Camera Recognition API
\\\

### 1.2 Component Breakdown

#### **Component 1: Data Acquisition**
- **Input**: Kaggle dataset ID
- **Process**: kagglehub download
- **Output**: Local Parquet files
- **Fallback**: Use existing image dataset if download fails

#### **Component 2: Data Processing**
- **Input**: Parquet files OR images
- **Process**: Extract MediaPipe landmarks, normalize, sequence
- **Output**: NumPy arrays (n_samples, 32, 468)
- **Augmentation**: Temporal jitter, landmark dropout

#### **Component 3: Vocabulary Mapping**
- **Input**: 263 available signs
- **Process**: Select 140 conversational signs
- **Output**: Label mapping JSON
- **Priority**: Tier 1 → 2 → 3 → 4

#### **Component 4: Model Training**
- **Input**: Processed arrays + labels
- **Architecture**: BiLSTM with attention
- **Output**: Trained .h5 model + history
- **Strategy**: Phased training by tier

#### **Component 5: Deployment**
- **Input**: Trained model
- **Process**: Replace backend model
- **Output**: Active API endpoint
- **Testing**: Camera integration test

---

## 2. Detailed Design

### 2.1 Vocabulary Selection Strategy

**Automatic Mapping:**
\\\python
# Priority mapping from 263 signs to 140 conversational signs
PRIORITY_SIGNS = {
    'tier1': [
        'hello', 'goodbye', 'thank_you', 'please', 'sorry',
        'yes', 'no', 'help', 'what', 'where', 'when', 'who',
        # ... 30 total
    ],
    'tier2': [
        'i', 'you', 'mother', 'father', 'happy', 'sad',
        # ... 40 total
    ],
    'tier3': [
        'home', 'school', 'food', 'water', 'today', 'tomorrow',
        # ... 40 total
    ],
    'tier4': [
        'more', 'less', 'same', 'different', 'again',
        # ... 30 total
    ]
}
\\\

**Fallback Strategy:**
- If sign not in dataset: Use similar sign or skip
- If <20 samples: Apply 3x augmentation
- If multiple variations: Use most common variant

### 2.2 Data Processing Pipeline

\\\python
def process_parquet_to_numpy(parquet_path, target_frames=32):
    # 1. Read Parquet file
    df = pd.read_parquet(parquet_path)
    
    # 2. Extract landmarks by type
    landmarks = {
        'pose': extract_pose(df),      # 33 points × 3 coords = 99
        'left_hand': extract_hand(df, 'left'),   # 21 × 3 = 63
        'right_hand': extract_hand(df, 'right'), # 21 × 3 = 63
        'face': extract_face_subset(df)  # Subset for 468 total
    }
    
    # 3. Concatenate features
    features = np.concatenate([
        landmarks['pose'],
        landmarks['left_hand'],
        landmarks['right_hand'],
        landmarks['face']
    ], axis=-1)  # Shape: (n_frames, 468)
    
    # 4. Normalize to target frames
    if len(features) > target_frames:
        features = temporal_subsample(features, target_frames)
    elif len(features) < target_frames:
        features = temporal_pad(features, target_frames)
    
    # 5. Normalize coordinates
    features = normalize_landmarks(features)  # [0, 1] range
    
    return features  # Shape: (32, 468)
\\\

### 2.3 Model Architecture

\\\python
def create_conversational_model(num_classes=140):
    inputs = Input(shape=(32, 468), name='landmark_sequence')
    
    # Bidirectional LSTM layers
    x = Bidirectional(LSTM(128, return_sequences=True))(inputs)
    x = Dropout(0.3)(x)
    
    # Attention mechanism (optional)
    attention = Dense(1, activation='tanh')(x)
    attention = Flatten()(attention)
    attention = Activation('softmax')(attention)
    attention = RepeatVector(256)(attention)
    attention = Permute([2, 1])(attention)
    
    x = Bidirectional(LSTM(64, return_sequences=True))(x)
    x = multiply([x, attention])  # Apply attention
    x = Lambda(lambda xin: K.sum(xin, axis=1))(x)
    
    x = Dropout(0.3)(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.2)(x)
    
    outputs = Dense(num_classes, activation='softmax', name='sign_prediction')(x)
    
    model = Model(inputs=inputs, outputs=outputs)
    return model
\\\

### 2.4 Training Strategy

**Phase 1: Tier 1 Only (30 signs)**
- Epochs: 50
- Purpose: Validate pipeline, baseline accuracy
- Expected: 95%+ accuracy

**Phase 2: Tiers 1+2 (70 signs)**
- Epochs: 50
- Purpose: Expand to personal/social signs
- Expected: 92%+ accuracy

**Phase 3: Full Model (140 signs)**
- Epochs: 100
- Purpose: Complete conversational vocabulary
- Expected: 90%+ accuracy

**Training Configuration:**
\\\python
config = {
    'optimizer': Adam(learning_rate=0.001),
    'loss': 'sparse_categorical_crossentropy',
    'metrics': ['accuracy', 'top_k_categorical_accuracy'],
    'batch_size': 32,
    'epochs': 100,
    'callbacks': [
        EarlyStopping(patience=20, restore_best_weights=True),
        ReduceLROnPlateau(factor=0.5, patience=10),
        ModelCheckpoint('best_model.h5', save_best_only=True)
    ],
    'class_weight': 'balanced'
}
\\\

---

## 3. Implementation Plan

### Phase 1: Data Acquisition (1-2 hours)
\\\python
# 1. Download dataset
import kagglehub
path = kagglehub.dataset_download("drblack00/isl-csltr-indian-sign-language-dataset")

# 2. Validate structure
validate_dataset(path)

# 3. Load label mapping
labels = load_label_map(path)

# 4. Select 140 conversational signs
selected_signs = select_conversational_vocabulary(labels)
\\\

### Phase 2: Data Processing (1-2 hours)
\\\python
# 1. Process Parquet files
X_data, y_data, metadata = process_all_parquet_files(
    dataset_path=path,
    selected_signs=selected_signs,
    target_frames=32
)

# 2. Split dataset
X_train, X_temp, y_train, y_temp = train_test_split(
    X_data, y_data, test_size=0.3, stratify=y_data
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp
)

# 3. Save processed data
save_processed_dataset(X_train, y_train, X_val, y_val, X_test, y_test)
\\\

### Phase 3: Model Training (2-3 hours)
\\\python
# 1. Create model
model = create_conversational_model(num_classes=140)

# 2. Compile
model.compile(optimizer=Adam(0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 3. Train
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=100,
    batch_size=32,
    callbacks=callbacks
)

# 4. Evaluate
test_acc = model.evaluate(X_test, y_test)
\\\

### Phase 4: Deployment (30 min)
\\\python
# 1. Save model
model.save('isl_model_conversational_140.h5')

# 2. Create vocabulary JSON
save_vocabulary(selected_signs, 'sign_vocabulary_140.json')

# 3. Deploy to backend
deploy_model('isl_model_conversational_140.h5', 'd:/Cap/backend/')

# 4. Test API
test_recognition_api()
\\\

---

## 4. File Structure

\\\
d:/Cap/
├── data/
│   ├── kaggle_conversational/      # Downloaded dataset
│   │   ├── keypoints/              # Parquet files
│   │   └── label_map.json          # 263 signs
│   └── processed_conversational/   # Processed arrays
│       ├── X_train.npy
│       ├── y_train.npy
│       ├── X_val.npy
│       └── X_test.npy
├── scripts/
│   ├── download_conversational_data.py
│   ├── process_conversational_data.py
│   ├── train_conversational_model.py
│   └── deploy_conversational_model.py
├── models/
│   ├── isl_model_conversational_140.h5
│   ├── training_history_conversational.json
│   └── vocabulary_conversational_140.json
└── backend/
    ├── isl_recognition_model.h5         # Deployed model
    └── models/
        └── sign_labels.json              # 140 signs
\\\

---

## 5. Success Metrics

### Training Metrics
- **Train Accuracy**: >95%
- **Validation Accuracy**: >90%
- **Test Accuracy**: >90%
- **Top-3 Accuracy**: >98%

### Performance Metrics
- **Inference Time**: <200ms
- **Model Size**: <100MB
- **Memory Usage**: <2GB
- **FPS**: >5 for real-time

### Quality Metrics
- **Tier 1 Accuracy**: >95%
- **Tier 2 Accuracy**: >92%
- **Tier 3 Accuracy**: >90%
- **Tier 4 Accuracy**: >85%

---

**Status**: Design Complete - Ready for Implementation
**Next**: Execute all phases
