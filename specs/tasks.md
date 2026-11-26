# Real ISL Dataset Integration - Tasks

## Project Overview
Integrate real ISL dataset (263 signs, 4,284 videos) to replace synthetic training data and improve model accuracy from poor recognition to >85% real-world accuracy.

---

## Task 1: Extract and Validate Kaggle Dataset
**Priority**: HIGH | **Estimated Time**: 15 min

### Description
Extract the 294 MB archive.zip and validate the dataset structure, ensuring all Parquet files and label mappings are present.

### Acceptance Criteria
- [ ] archive.zip extracted to d:\Cap\data\kaggle_isl\
- [ ] 4,284 Parquet files verified
- [ ] label_map.json loaded and validated (263 signs)
- [ ] Directory structure matches expected format
- [ ] Sample Parquet file successfully read with pandas

### Dependencies
None

### Files to Create/Modify
- d:\Cap\scripts\extract_kaggle_data.py

---

## Task 2: Create Parquet to NumPy Converter
**Priority**: HIGH | **Estimated Time**: 30 min

### Description
Build converter to transform Parquet MediaPipe landmarks into NumPy arrays (32 frames × 468 features) matching current model input format.

### Acceptance Criteria
- [ ] Converter handles variable-length sequences (pad/truncate to 32 frames)
- [ ] Extracts pose (33) + left_hand (21) + right_hand (21) + face subset = 468 features
- [ ] Normalizes coordinates to [0, 1] range
- [ ] Handles missing landmarks gracefully
- [ ] Processes all 4,284 videos successfully
- [ ] Output shape verified: (4284, 32, 468)

### Dependencies
Task 1 (data extraction)

### Files to Create/Modify
- d:\Cap\scripts\convert_parquet_to_numpy.py
- d:\Cap\data\kaggle_isl\processed\X_train.npy
- d:\Cap\data\kaggle_isl\processed\y_train.npy

### Technical Notes
`python
# Landmark mapping:
# - pose: 33 points (MediaPipe Pose)
# - left_hand: 21 points
# - right_hand: 21 points  
# - face: subset to fit 468 total (393 remaining)
# Total: 33 + 21 + 21 + 393 = 468 features × 3 coords (x,y,z) = 1404 → flatten to 468
`

---

## Task 3: Create Train/Val/Test Splits
**Priority**: HIGH | **Estimated Time**: 10 min

### Description
Split converted dataset into training (80%), validation (10%), and test (10%) sets with stratification to maintain class balance.

### Acceptance Criteria
- [ ] 80/10/10 split implemented
- [ ] Stratified by sign class (balanced distribution)
- [ ] No data leakage between sets
- [ ] Splits saved to separate files
- [ ] Sign distribution verified per split

### Dependencies
Task 2 (data conversion)

### Files to Create/Modify
- d:\Cap\scripts\create_dataset_splits.py
- d:\Cap\data\kaggle_isl\processed\train\
- d:\Cap\data\kaggle_isl\processed\val\
- d:\Cap\data\kaggle_isl\processed\test\

---

## Task 4: Merge with Synthetic Data (Optional Augmentation)
**Priority**: MEDIUM | **Estimated Time**: 15 min

### Description
Optionally combine Kaggle real data with existing synthetic data for data augmentation, using real data as primary and synthetic as supplement.

### Acceptance Criteria
- [ ] Can toggle synthetic data inclusion via config
- [ ] Real data weighted 80%, synthetic 20% (if used)
- [ ] Label mapping unified between datasets
- [ ] Combined dataset maintains proper splits
- [ ] No duplicate samples between real and synthetic

### Dependencies
Task 3 (dataset splits)

### Files to Create/Modify
- d:\Cap\scripts\merge_datasets.py
- d:\Cap\config\training_config.json

---

## Task 5: Create 263-Class Model Architecture
**Priority**: HIGH | **Estimated Time**: 20 min

### Description
Modify existing BiLSTM model to output 263 classes instead of 136, maintaining the same input format and architecture design.

### Acceptance Criteria
- [ ] Input shape: (32, 468) unchanged
- [ ] Output layer: 263 classes (softmax)
- [ ] BiLSTM layers maintained
- [ ] Dropout and regularization configured
- [ ] Model summary shows correct architecture
- [ ] Compatible with TensorFlow 2.x

### Dependencies
None (architecture only)

### Files to Create/Modify
- d:\Cap\scripts\create_263_model.py

### Model Architecture
`python
Input(32, 468)
  ↓
BiLSTM(128, return_sequences=True)
  ↓
Dropout(0.3)
  ↓
BiLSTM(64)
  ↓
Dropout(0.3)
  ↓
Dense(128, activation='relu')
  ↓
Dense(263, activation='softmax')  # Updated
`

---

## Task 6: Implement Training Pipeline
**Priority**: HIGH | **Estimated Time**: 30 min

### Description
Create comprehensive training script with data generators, callbacks, learning rate scheduling, and performance monitoring.

### Acceptance Criteria
- [ ] Data generator for memory-efficient loading
- [ ] Class weighting for imbalanced data
- [ ] Learning rate schedule (reduce on plateau)
- [ ] Early stopping (patience=15)
- [ ] Model checkpointing (save best)
- [ ] TensorBoard logging
- [ ] Training history saved to JSON
- [ ] GPU utilization >80%

### Dependencies
Task 2 (data ready), Task 5 (model architecture)

### Files to Create/Modify
- d:\Cap\scripts\train_real_isl_model.py
- d:\Cap\models\isl_model_263_real.h5 (output)
- d:\Cap\models\training_history_263.json (output)

### Training Configuration
`python
{
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001,
    "optimizer": "adam",
    "early_stopping_patience": 15,
    "reduce_lr_patience": 7,
    "class_weights": "auto"
}
`

---

## Task 7: Run Training and Monitor Performance
**Priority**: HIGH | **Estimated Time**: 90 min (mostly automated)

### Description
Execute training pipeline on full Kaggle dataset and monitor accuracy, loss, and performance metrics.

### Acceptance Criteria
- [ ] Training completes successfully
- [ ] Validation accuracy >85%
- [ ] No overfitting (val loss close to train loss)
- [ ] Training curves saved and visualized
- [ ] Best model checkpoint saved
- [ ] Final model exported as .h5

### Dependencies
Task 6 (training pipeline)

### Files Generated
- d:\Cap\models\isl_model_263_real.h5
- d:\Cap\models\checkpoints\epoch_*.h5
- d:\Cap\logs\tensorboard\

---

## Task 8: Create Updated Sign Vocabulary
**Priority**: HIGH | **Estimated Time**: 10 min

### Description
Generate sign_labels_263.json with all 263 ISL signs from Kaggle label_map.json, maintaining ID-to-name mapping.

### Acceptance Criteria
- [ ] JSON file with 263 sign entries
- [ ] Format: {"sign_name": id, ...}
- [ ] IDs match Kaggle label_map
- [ ] All signs from categories included
- [ ] File saved to backend models directory

### Dependencies
Task 1 (label_map.json extracted)

### Files to Create/Modify
- d:\Cap\scripts\create_vocabulary.py
- d:\Cap\backend\models\sign_labels_263.json

---

## Task 9: Validate Model Accuracy on Test Set
**Priority**: HIGH | **Estimated Time**: 15 min

### Description
Run comprehensive validation on held-out test set to measure real-world accuracy, per-class metrics, and confusion matrix.

### Acceptance Criteria
- [ ] Test accuracy >85%
- [ ] Per-class precision/recall/F1 calculated
- [ ] Confusion matrix generated
- [ ] Top-5 accuracy measured
- [ ] Inference time <200ms per sample
- [ ] Validation report saved

### Dependencies
Task 7 (trained model)

### Files to Create/Modify
- d:\Cap\scripts\validate_model_263.py
- d:\Cap\reports\model_263_validation.json
- d:\Cap\reports\confusion_matrix_263.png

---

## Task 10: Deploy Model to Backend
**Priority**: HIGH | **Estimated Time**: 20 min

### Description
Integrate new 263-class model into Django backend, update model loading, and ensure API compatibility.

### Acceptance Criteria
- [ ] Model file copied to backend directory
- [ ] sign_labels_263.json loaded correctly
- [ ] Recognition API updated to use new model
- [ ] Backward compatibility maintained (API unchanged)
- [ ] Model loads successfully on server start
- [ ] Inference endpoint tested and working

### Dependencies
Task 7 (trained model), Task 8 (vocabulary)

### Files to Modify
- d:\Cap\backend\ml_model\model_loader.py
- d:\Cap\backend\ml_model\inference.py
- d:\Cap\backend\isl_recognition_model.h5 (replace)
- d:\Cap\backend\models\sign_labels.json (update)

---

## Task 11: Update Frontend Sign List
**Priority**: MEDIUM | **Estimated Time**: 15 min

### Description
Update React frontend to display all 263 signs in vocabulary, organized by categories.

### Acceptance Criteria
- [ ] Frontend loads 263 signs from API
- [ ] Signs grouped by 15 categories
- [ ] Search/filter functionality works
- [ ] Sign display is responsive
- [ ] No breaking changes to existing UI

### Dependencies
Task 10 (backend deployed)

### Files to Modify
- d:\Cap\frontend\isl-chat-ui\src\components\SignVocabulary.tsx
- d:\Cap\frontend\isl-chat-ui\src\services\signService.ts

---

## Task 12: Real Camera Testing
**Priority**: HIGH | **Estimated Time**: 20 min

### Description
Test model with actual camera input using data_collector.html to verify real-world accuracy improvements.

### Acceptance Criteria
- [ ] Camera interface loads and captures frames
- [ ] Model identifies signs correctly (>80% accuracy)
- [ ] Inference time <200ms
- [ ] No console errors
- [ ] Confidence scores displayed
- [ ] Test with 20+ different signs

### Dependencies
Task 10 (backend deployed)

### Files to Test
- d:\Cap\data_collector.html
- Backend recognition API

---

## Task 13: Performance Profiling
**Priority**: MEDIUM | **Estimated Time**: 15 min

### Description
Profile model inference performance, memory usage, and identify any bottlenecks.

### Acceptance Criteria
- [ ] Inference time measured (<200ms target)
- [ ] Memory usage profiled (<2GB target)
- [ ] CPU/GPU utilization measured
- [ ] Bottlenecks identified (if any)
- [ ] Performance report generated

### Dependencies
Task 10 (deployed model)

### Files to Create
- d:\Cap\scripts\profile_model.py
- d:\Cap\reports\performance_profile.json

---

## Task 14: Create Model Comparison Report
**Priority**: LOW | **Estimated Time**: 15 min

### Description
Compare old 136-sign synthetic model vs new 263-sign real data model across multiple metrics.

### Acceptance Criteria
- [ ] Side-by-side accuracy comparison
- [ ] Inference time comparison
- [ ] Model size comparison
- [ ] Real-world test results
- [ ] Recommendation for production use

### Dependencies
Task 9 (validation complete)

### Files to Create
- d:\Cap\reports\MODEL_COMPARISON.md

### Comparison Metrics
- Accuracy: synthetic vs real
- Signs supported: 136 vs 263
- Real-world performance
- Inference speed
- Model size

---

## Task 15: Documentation and Handoff
**Priority**: MEDIUM | **Estimated Time**: 20 min

### Description
Create comprehensive documentation for training process, deployment, and future retraining.

### Acceptance Criteria
- [ ] Training process documented
- [ ] Deployment steps documented
- [ ] Model architecture explained
- [ ] Retraining instructions provided
- [ ] Troubleshooting guide included

### Dependencies
All previous tasks

### Files to Create
- d:\Cap\docs\REAL_DATA_TRAINING.md
- d:\Cap\docs\MODEL_263_DEPLOYMENT.md
- d:\Cap\docs\RETRAINING_GUIDE.md

---

## Summary

**Total Tasks**: 15
**Estimated Time**: 2.5-3 hours
**High Priority**: 10 tasks
**Medium Priority**: 4 tasks
**Low Priority**: 1 task

### Critical Path
1. Extract data → Convert format → Train model → Deploy → Test
2. Tasks 1 → 2 → 3 → 5 → 6 → 7 → 10 → 12

### Success Metrics
- ✅ 263 signs supported (up from 136)
- ✅ >85% real-world accuracy (up from poor accuracy)
- ✅ <200ms inference time (maintained)
- ✅ Working camera recognition (fixed)

---

**Ready to execute**: All tasks sequenced and dependencies mapped
**Next Step**: Begin Task 1 (Extract Kaggle Dataset)
