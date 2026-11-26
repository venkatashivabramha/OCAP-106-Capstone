# Real ISL Dataset Integration - Requirements

## 1. Project Context

### Current State
- **Model**: 136 ISL signs, trained on synthetic data (27,200 samples)
- **Architecture**: BiLSTM (32 frames × 468 features)
- **Problem**: Poor real-world accuracy due to synthetic training data
- **Status**: Deployed but not identifying signs correctly from camera

### Available Data Sources
1. **Kaggle Dataset** (archive.zip - 294 MB)
   - 263 ISL signs from AI4Bharat INCLUDE
   - 4,284 real video files in Parquet format
   - MediaPipe Holistic landmarks
   - Structure: (frame, row_id, type, landmark_index, x, y, z)

2. **Local Notebook** 
   - Path: C:\Users\venka\Downloads\indian-sign-language-mediapipe-landmark-eda.ipynb
   - Contains: Dataset exploration and analysis code
   - Label mapping: label_map.json with 263 signs

3. **Current Synthetic Dataset**
   - 27,200 synthetic samples (200 per sign × 136 signs)
   - Augmented 5x from base synthetic data
   - Location: d:\Cap\models\isl_enhanced\

## 2. Objectives

### Primary Goals
1. **Fix Accuracy**: Train model on REAL ISL data to match real-world camera input
2. **Use ALL Data**: Combine Kaggle dataset + current synthetic data
3. **Expand Vocabulary**: Support all 263 signs from Kaggle dataset
4. **Maintain Compatibility**: Keep 32 frames × 468 features input format
5. **Production Ready**: Deploy working model that identifies signs correctly

### Success Criteria
- Real-world accuracy: >85% on test set
- Inference time: <200ms per prediction
- Support: 263 ISL signs (up from 136)
- Robustness: Works with varied lighting, speed, hand positions
- Deployment: Seamless integration with existing backend

## 3. Technical Requirements

### Data Processing
1. **Extract Archive**: Unzip 294 MB archive.zip
2. **Parse Parquet Files**: Read MediaPipe landmarks from 4,284 files
3. **Convert Format**: Transform to 32 frames × 468 features
   - Handle variable-length sequences (pad/truncate)
   - Normalize coordinates to [0, 1]
   - Maintain landmark order: pose + left_hand + right_hand + face
4. **Create Label Mapping**: Map 263 signs to numeric IDs
5. **Split Dataset**: 80% train, 10% validation, 10% test

### Model Architecture
1. **Expand Output Layer**: 136 → 263 classes
2. **Keep Input Format**: 32 frames × 468 features
3. **Architecture**: Maintain BiLSTM structure
4. **Regularization**: Dropout, L2, batch normalization
5. **Loss Function**: Categorical crossentropy

### Training Strategy
1. **Phase 1**: Train on Kaggle real data only
2. **Phase 2**: Fine-tune with synthetic data augmentation
3. **Phase 3**: Optimize hyperparameters
4. **Validation**: Use real data test set for metrics

### Integration Requirements
1. **Model Export**: Save as .h5 format
2. **Vocabulary Update**: Create new sign_labels.json (263 signs)
3. **Backend Integration**: Update Django model loading
4. **Frontend Update**: Add new signs to vocabulary
5. **API Compatibility**: Maintain existing endpoints

## 4. Implementation Scope

### In Scope
✅ Extract and process ALL Kaggle dataset (4,284 videos)
✅ Convert Parquet → NumPy training format
✅ Expand model to 263 signs
✅ Train on real data with synthetic augmentation
✅ Bias-variance analysis and optimization
✅ Deploy to backend with new vocabulary
✅ Update frontend sign list
✅ Comprehensive testing and validation

### Out of Scope
❌ Video recording/collection (using existing Kaggle data)
❌ Manual data annotation (labels provided)
❌ Model architecture redesign (keeping BiLSTM)
❌ Mobile app deployment (web only)

## 5. Deliverables

### Scripts
1. extract_kaggle_data.py - Extract and validate archive
2. convert_parquet_to_numpy.py - Convert landmarks to training format
3. create_combined_dataset.py - Merge Kaggle + synthetic data
4. 	rain_real_isl_model.py - Training pipeline with all data
5. alidate_model.py - Testing and metrics

### Models
1. isl_model_263_real.h5 - Trained model (263 signs)
2. sign_labels_263.json - Sign vocabulary mapping
3. 	raining_history.json - Training metrics and plots

### Documentation
1. REAL_DATA_TRAINING.md - Training process and results
2. MODEL_COMPARISON.md - Before/after metrics
3. DEPLOYMENT_GUIDE.md - Integration steps

## 6. Data Structure Specification

### Kaggle Parquet Format
"'python
{
    'frame': int,           # Frame number (0-indexed)
    'row_id': str,         # Unique row identifier
    'type': str,           # 'face', 'pose', 'left_hand', 'right_hand'
    'landmark_index': int, # Landmark ID within type
    'x': float,            # X coordinate [0, 1]
    'y': float,            # Y coordinate [0, 1]
    'z': float             # Z depth (relative)
}
"'

### Target NumPy Format
"'python
shape: (n_samples, 32, 468)
# 468 features = 33 pose + 21 left + 21 right + 468 holistic
# 32 frames = temporal sequence
"'

### Label Mapping
"'json
{
    "hello": 0,
    "thank_you": 1,
    ...
    "sign_262": 262
}
"'

## 7. Performance Requirements

### Training
- GPU utilization: >80%
- Training time: <3 hours for full dataset
- Memory usage: <16GB RAM
- Batch size: Adaptive based on GPU memory

### Inference
- Latency: <200ms per prediction
- Throughput: >5 FPS
- CPU usage: <70% during inference
- Memory: <2GB for model

## 8. Risk Assessment

### Technical Risks
1. **Variable Sequence Length**: Parquet files have different frame counts
   - Mitigation: Pad/truncate to 32 frames with temporal interpolation

2. **Memory Constraints**: 4,284 videos may exceed RAM
   - Mitigation: Use data generators, process in batches

3. **Class Imbalance**: Some signs may have more samples
   - Mitigation: Class weighting, balanced sampling

4. **Overfitting**: Real data much larger than synthetic
   - Mitigation: Dropout, early stopping, validation monitoring

### Operational Risks
1. **Deployment Compatibility**: New model may break existing code
   - Mitigation: Maintain API compatibility, version models

2. **Performance Degradation**: Larger model may be slower
   - Mitigation: Profile inference, optimize if needed

## 9. Timeline Estimate

### Phase 1: Data Preparation (45 min)
- Extract archive.zip
- Parse Parquet files
- Convert to NumPy format
- Create train/val/test splits

### Phase 2: Model Training (90 min)
- Configure architecture (263 outputs)
- Train on real data
- Fine-tune with synthetic data
- Validate and optimize

### Phase 3: Integration (30 min)
- Deploy model to backend
- Update vocabulary files
- Test API endpoints
- Verify camera integration

### Phase 4: Validation (15 min)
- Accuracy testing
- Performance profiling
- Real camera testing

**Total: 2-3 hours**

## 10. Acceptance Criteria

### Functional
✅ Model supports all 263 ISL signs
✅ Real-world accuracy >85% on test set
✅ Inference time <200ms
✅ Camera integration works correctly
✅ Existing API endpoints unchanged

### Non-Functional
✅ Code is documented and maintainable
✅ Training process is reproducible
✅ Model files are version controlled
✅ Performance metrics are logged

---

**Status**: Ready for Implementation
**Priority**: HIGH - Fixes critical accuracy issue
**Complexity**: Medium - Data processing + retraining
**Impact**: HIGH - Transforms model from synthetic to production-ready
