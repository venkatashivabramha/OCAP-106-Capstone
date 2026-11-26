# Conversational ISL Model - Requirements Specification

## 1. Project Overview

### 1.1 Context
**Current State:**
- Model: 35 signs (A-Z, 0-9 finger-spelling only)
- Accuracy: 97.7% test accuracy
- Limitation: Cannot support basic conversations, only spelling

**Objective:**
Expand to **conversational ISL vocabulary** supporting basic everyday communication beyond finger-spelling.

### 1.2 Goal
Create an ISL recognition model that understands common conversational signs for:
- Greetings and farewells
- Common questions and answers
- Basic needs and requests
- Emotions and feelings
- Daily activities
- Family and relationships

**Target**: 100-150 conversational signs for practical communication

---

## 2. Vocabulary Requirements

### 2.1 Priority Categories

#### **Tier 1: Essential Communication** (30 signs) - MUST HAVE
Core signs needed for basic interaction:

**Greetings & Politeness (8 signs)**
1. Hello / Hi
2. Goodbye / Bye
3. Thank you
4. Please
5. Sorry / Excuse me
6. Welcome
7. Good morning
8. Good night

**Question Words (6 signs)**
9. What
10. Where
11. When
12. Who
13. Why
14. How

**Basic Responses (6 signs)**
15. Yes
16. No
17. Maybe
18. I don't know
19. I understand
20. I don't understand

**Common Verbs (10 signs)**
21. Want / Need
22. Like / Love
23. Help
24. Go
25. Come
26. Eat
27. Drink
28. Sleep
29. Work
30. Study

#### **Tier 2: Personal & Social** (40 signs) - SHOULD HAVE
Building social connections:

**Personal Pronouns & Identity (10 signs)**
31. I / Me
32. You
33. He / Him
34. She / Her
35. We / Us
36. They / Them
37. My / Mine
38. Your / Yours
39. Name
40. Age

**Family & Relationships (10 signs)**
41. Mother
42. Father
43. Brother
44. Sister
45. Friend
46. Family
47. Child / Baby
48. Husband / Wife
49. Grandmother
50. Grandfather

**Emotions & Feelings (10 signs)**
51. Happy
52. Sad
53. Angry
54. Tired
55. Sick / Ill
56. Hurt / Pain
57. Hungry
58. Thirsty
59. Good
60. Bad

**Common Adjectives (10 signs)**
61. Big
62. Small
63. Hot
64. Cold
65. Fast
66. Slow
67. Easy
68. Difficult / Hard
69. Important
70. Beautiful

#### **Tier 3: Daily Life** (40 signs) - COULD HAVE
Everyday activities and needs:

**Places (10 signs)**
71. Home
72. School
73. Hospital
74. Shop / Store
75. Office
76. Restaurant
77. Bathroom / Toilet
78. Kitchen
79. Bedroom
80. Outside

**Time & Days (10 signs)**
81. Today
82. Tomorrow
83. Yesterday
84. Now
85. Later
86. Morning
87. Afternoon
88. Evening
89. Night
90. Week

**Common Nouns (10 signs)**
91. Food
92. Water
93. Money
94. Phone
95. Book
96. Car
97. House
98. Medicine
99. Clothes
100. Bag

**Actions & States (10 signs)**
101. Sit
102. Stand
103. Walk
104. Run
105. Stop
106. Wait
107. Talk / Speak
108. Listen
109. See / Look
110. Read

#### **Tier 4: Extended Conversation** (30 signs) - NICE TO HAVE
For richer communication:

**Numbers Beyond 0-9 (10 signs)**
111. Ten (10)
112. Twenty (20)
113. Hundred (100)
114. Thousand (1000)
115. Many / Much
116. Few / Little
117. First
118. Second
119. Last
120. All

**Additional Useful Signs (20 signs)**
121. Same / Similar
122. Different
123. More
124. Less
125. Enough
126. Again / Repeat
127. Finish / Done
128. Start / Begin
129. Can / Able
130. Cannot / Unable
131. Have
132. Don't have
133. Give
134. Take
135. Buy
136. Sell
137. Open
138. Close
139. Right (correct)
140. Wrong

**Total Target: 140 conversational signs**

### 2.2 Vocabulary Principles
1. **Practical Focus**: Signs used in daily conversation
2. **Cultural Authenticity**: Standard ISL signs (Indian Sign Language)
3. **Frequency-Based**: Common signs prioritized
4. **Progressive Learning**: Tier structure for phased rollout
5. **Semantic Grouping**: Related signs learned together

---

## 3. Data Requirements

### 3.1 Data Sources

#### **Primary Source: Kaggle/AI4Bharat Dataset**
- **Dataset**: Indian Sign Language MediaPipe Landmarks
- **Coverage**: 263 ISL signs with real video data
- **Format**: Parquet files with MediaPipe Holistic landmarks
- **Status**: Available for download via kagglehub

**Download Strategy:**
\\\python
import kagglehub
path = kagglehub.dataset_download("drblack00/isl-csltr-indian-sign-language-dataset")
\\\

#### **Secondary Source: Existing Image Dataset**
- **Current**: 42,745 images (A-Z, 0-9) already processed
- **Usage**: Keep for finger-spelling augmentation
- **Integration**: Combine with new conversational signs

#### **Tertiary Source: Synthetic Augmentation**
- **Purpose**: Fill gaps for missing signs
- **Method**: Data augmentation (rotation, scaling, temporal variation)
- **Ratio**: Real data 80%, augmented 20%

### 3.2 Data Processing Requirements

#### **Input Format**
- **Raw**: MediaPipe Parquet files OR images
- **Landmarks**: Holistic (pose + hands + face)
- **Frame Rate**: Variable (normalize to 32 frames)

#### **Output Format**
- **Shape**: (n_samples, 32, 468)
- **Features**: 468 MediaPipe landmark features
- **Labels**: Integer class IDs (0-139 for 140 signs)
- **Splits**: 70% train, 15% val, 15% test

#### **Quality Requirements**
- **Minimum samples per sign**: 20 (preferably 50+)
- **Multiple signers**: 3+ different people per sign
- **Varied conditions**: Different lighting, backgrounds, speeds
- **Validation**: Manual review of random samples

---

## 4. Model Requirements

### 4.1 Architecture Specifications

#### **Input Layer**
- Shape: (32, 468) - 32 frames × 468 landmark features
- Normalization: [0, 1] range
- Augmentation: Temporal jitter, landmark dropout

#### **Network Architecture**
\\\
Input(32, 468)
  ↓
Bidirectional LSTM(128, return_sequences=True)
  ↓
Spatial Attention Layer (optional)
  ↓
Dropout(0.3)
  ↓
Bidirectional LSTM(64)
  ↓
Dropout(0.3)
  ↓
Dense(128, activation='relu')
  ↓
Dropout(0.2)
  ↓
Dense(140, activation='softmax')  # 140 conversational signs
\\\

#### **Training Configuration**
- **Optimizer**: Adam (lr=0.001 → 0.0001 scheduled)
- **Loss**: Categorical Crossentropy with label smoothing
- **Batch Size**: 32 (adaptive based on GPU memory)
- **Epochs**: 100 (early stopping patience=20)
- **Class Weights**: Balanced to handle imbalanced data

### 4.2 Performance Requirements

#### **Accuracy Targets**
- **Overall Test Accuracy**: ≥ 90%
- **Tier 1 Signs (Essential)**: ≥ 95%
- **Tier 2-3 Signs**: ≥ 90%
- **Tier 4 Signs**: ≥ 85%
- **Confusion Threshold**: <5% between similar signs

#### **Inference Requirements**
- **Latency**: <200ms per prediction
- **Throughput**: ≥5 FPS for real-time recognition
- **Memory**: <2GB model size
- **Hardware**: CPU-compatible (GPU optional)

#### **Robustness Requirements**
- **Lighting**: Works in various lighting conditions
- **Background**: Tolerant to different backgrounds
- **Speed**: Handles normal to fast signing speeds
- **Hand Size**: Works for different hand sizes
- **Occlusion**: Basic tolerance for partial occlusion

---

## 5. User Experience Requirements

### 5.1 Recognition Interface

#### **Real-time Feedback**
- Display recognized sign within 200ms
- Show confidence score (%)
- Highlight when confidence < 70%
- Provide alternative suggestions (top-3)

#### **Sign Guidance**
- Visual guide for each sign
- Reference video/image per sign
- Common mistakes highlighted
- Practice mode with feedback

### 5.2 Vocabulary Browser

#### **Organization**
- Browse by category (greetings, questions, etc.)
- Search by sign name
- Filter by tier/difficulty
- View sign details (video, description)

#### **Learning Features**
- Mark signs as "learned"
- Practice mode with random signs
- Progress tracking per category
- Suggested learning path

---

## 6. Data Privacy & Ethics

### 6.1 Privacy Requirements
- No personal identifiable information in training data
- Anonymized signer identities
- MediaPipe landmarks (not raw video pixels)
- Local inference (no data sent to cloud)

### 6.2 Cultural Sensitivity
- Authentic ISL signs (Indian Sign Language)
- Respect for Deaf community standards
- Avoid gestures that may be offensive
- Include regional variations where appropriate

### 6.3 Accessibility
- Interface usable by Deaf/HoH users
- Visual feedback (no audio-only)
- Clear visual instructions
- Support for screen readers (text alternatives)

---

## 7. Success Criteria

### 7.1 Functional Requirements ✅
- [ ] Model recognizes 140 conversational signs
- [ ] All Tier 1 signs (30 essential) working
- [ ] ≥90% overall test accuracy
- [ ] <200ms inference latency
- [ ] Real-time camera recognition working

### 7.2 Quality Requirements ✅
- [ ] Confusion matrix shows <5% error between similar signs
- [ ] Works with 3+ different signers
- [ ] Robust to lighting/background variations
- [ ] Handles normal to fast signing speeds

### 7.3 Usability Requirements ✅
- [ ] Sign vocabulary browser implemented
- [ ] Reference videos/images for each sign
- [ ] Practice mode with feedback
- [ ] User can achieve >80% accuracy in practice mode

### 7.4 Documentation Requirements ✅
- [ ] Sign vocabulary documented
- [ ] Training process documented
- [ ] API usage examples provided
- [ ] User guide created

---

## 8. Implementation Phases

### **Phase 1: Data Acquisition** (1-2 hours)
1. Download MediaPipe Parquet dataset (263 signs)
2. Extract and validate data structure
3. Map 140 conversational signs to dataset
4. Verify sufficient samples per sign

### **Phase 2: Data Processing** (1-2 hours)
1. Convert Parquet to NumPy format (32×468)
2. Handle variable sequence lengths
3. Create train/val/test splits
4. Apply data augmentation
5. Generate class weights

### **Phase 3: Model Training** (2-3 hours)
1. Expand model to 140 output classes
2. Train on conversational vocabulary
3. Monitor training curves
4. Optimize hyperparameters
5. Validate on test set

### **Phase 4: Integration** (1 hour)
1. Deploy model to backend
2. Update sign vocabulary JSON
3. Test API endpoints
4. Verify camera integration

### **Phase 5: Testing** (1 hour)
1. Real camera testing (20+ signs)
2. Performance profiling
3. Error analysis
4. User acceptance testing

**Total Estimated Time: 6-9 hours**

---

## 9. Risk Assessment

### 9.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Insufficient data for some signs** | High | Use data augmentation, start with Tier 1 only |
| **Model overfitting** | Medium | Dropout, early stopping, validation monitoring |
| **Sign similarity confusion** | High | Attention mechanism, more training data |
| **Dataset download fails** | Medium | Fallback to image dataset + manual labeling |
| **Training time too long** | Low | Use subset first, full training overnight |

### 9.2 Data Quality Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Mislabeled data** | High | Manual validation of samples |
| **Regional ISL variations** | Medium | Document variations, focus on standard ISL |
| **Insufficient signer diversity** | Medium | Augmentation, test with multiple users |
| **Imbalanced classes** | High | Class weighting, balanced sampling |

---

## 10. Constraints

### 10.1 Technical Constraints
- Python 3.12, TensorFlow 2.x
- Windows environment
- 16GB RAM limit
- CPU training acceptable (GPU optional)
- Must maintain <2GB model size

### 10.2 Time Constraints
- Complete implementation: 1-2 days
- Initial working prototype: 6-9 hours
- Testing and validation: 2-3 hours

### 10.3 Data Constraints
- Primary dataset: Kaggle/AI4Bharat (263 signs available)
- Secondary: Existing 42,745 images (A-Z, 0-9)
- Cannot collect new video data (time constraint)
- Must work with available datasets

---

## 11. Acceptance Criteria

### 11.1 Minimum Viable Product (MVP)
✅ **Must Have:**
- 30 Tier 1 essential signs working (greetings, questions, responses)
- ≥90% accuracy on test set
- Real-time camera recognition (<200ms)
- API integration working
- Basic sign vocabulary browser

### 11.2 Full Product
✅ **Should Have:**
- 100+ conversational signs (Tiers 1-3)
- ≥90% overall accuracy
- Sign reference guide
- Practice mode
- Comprehensive testing

### 11.3 Stretch Goals
✅ **Nice to Have:**
- Full 140 signs (all tiers)
- Sentence formation from signs
- Sign-to-text translation
- Learning progress tracking

---

## 12. Deliverables

### 12.1 Code Deliverables
1. download_conversational_dataset.py - Dataset acquisition
2. process_conversational_data.py - Data preprocessing
3. 	rain_conversational_model.py - Training pipeline
4. deploy_conversational_model.py - Deployment script
5. 	est_conversational_model.py - Testing suite

### 12.2 Model Deliverables
1. isl_model_conversational_140.h5 - Trained model
2. sign_vocabulary_conversational.json - 140 sign labels
3. 	raining_history_conversational.json - Training metrics
4. confusion_matrix_conversational.png - Error analysis

### 12.3 Documentation Deliverables
1. CONVERSATIONAL_ISL_REQUIREMENTS.md - This document
2. CONVERSATIONAL_ISL_DESIGN.md - Technical design
3. SIGN_VOCABULARY_GUIDE.md - User-facing sign guide
4. TRAINING_REPORT.md - Training results and analysis

---

## 13. Next Steps

After requirements approval:
1. Create technical design document
2. Download and validate dataset
3. Implement data processing pipeline
4. Begin phased training (Tier 1 → Tier 2 → Tier 3 → Tier 4)
5. Iterative testing and refinement

---

**Status**: ✅ Requirements Complete - Ready for Design Phase
**Priority**: HIGH - Enables actual conversation vs finger-spelling
**Complexity**: Medium - Data processing + model training
**Impact**: HIGH - Transforms app from spelling tool to conversation tool

---

*Requirements v1.0 - Created for Conversational ISL Expansion*
*Focus: Practical everyday communication in Indian Sign Language*
