# AI-Powered Predictive Analytics Implementation Plan

## 🎯 Overview
Transform BrightTrack from reactive to proactive student support using AI/ML for early intervention and data-driven decision making.

---

## 📊 Features to Implement

### 1. **Predictive Risk Analysis** (High Priority)
- **Goal**: Predict at-risk students before traditional metrics show problems
- **Impact**: Proactive intervention instead of reactive

### 2. **Intervention Recommendation Engine**
- **Goal**: Suggest personalized interventions based on past success
- **Impact**: Data-driven intervention planning

### 3. **Sentiment Analysis on Wellness Check-ins**
- **Goal**: Detect emotional distress from text responses
- **Impact**: Catch hidden emotional issues

### 4. **Smart Student Prioritization**
- **Goal**: Rank students by urgency, not just risk level
- **Impact**: Optimize counselor time allocation

---

## 🛠️ Technical Stack

### Core AI Service
- **Google Gemini API** - Primary AI engine for all predictions and analysis
  - Gemini 1.5 Flash (fast, cost-effective for real-time predictions)
  - Gemini 1.5 Pro (advanced reasoning for complex analysis)
- **google-generativeai** - Python SDK for Gemini

### Data Processing
- **pandas** - Data manipulation and feature engineering
- **numpy** - Numerical computations (optional)

### Background Processing
- **celery** - Background task processing for predictions
- **redis** - Caching API responses and prediction results

### Why Gemini API?
✅ **No model training needed** - Use pre-trained AI out of the box
✅ **Natural language understanding** - Better context interpretation
✅ **Multimodal capabilities** - Can analyze text, patterns, and trends
✅ **Easy integration** - Simple API calls, no ML expertise required
✅ **Cost-effective** - Pay per use, no infrastructure costs
✅ **Always up-to-date** - Google maintains and improves the model
✅ **Structured output** - JSON mode for consistent responses

---

## 📁 Project Structure

```
campus-care-project/
├── ml_models/                          # New Django app for AI
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                       # Store predictions, logs
│   ├── views.py                        # API endpoints for predictions
│   ├── urls.py
│   ├── admin.py
│   ├── gemini_client.py                # Gemini API wrapper
│   ├── prompt_templates.py             # Prompt templates for each feature
│   ├── predictors/                     # AI logic
│   │   ├── __init__.py
│   │   ├── risk_predictor.py          # Predictive risk analysis
│   │   ├── intervention_recommender.py # Intervention suggestions
│   │   ├── sentiment_analyzer.py       # Wellness sentiment analysis
│   │   ├── priority_ranker.py          # Student prioritization
│   │   └── feature_engineering.py      # Data preprocessing
│   ├── management/                     # Django commands
│   │   └── commands/
│   │       ├── predict_risks.py        # python manage.py predict_risks
│   │       └── update_priorities.py    # python manage.py update_priorities
│   └── templates/
│       └── ml_models/
│           ├── predictions_dashboard.html
│           └── ai_insights.html
├── .env                                # Environment variables (API keys)
├── requirements.txt                    # Updated with Gemini SDK
└── README.md
```

---

## 📋 Implementation Phases

### **Phase 1: Setup & Data Preparation** (Week 1)
**Goal**: Prepare infrastructure and data pipeline

#### Tasks:
1. **Install Dependencies**
   ```bash
   pip install google-generativeai pandas celery redis
   ```

2. **Get Gemini API Key**
   - Go to https://makersuite.google.com/app/apikey
   - Create new API key
   - Add to `.env` file:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

3. **Create ml_models Django App**
   ```bash
   python manage.py startapp ml_models
   ```

4. **Database Models**
   - `PredictionLog` - Store all predictions with timestamps
   - `ModelMetadata` - Track model versions, accuracy, last trained
   - `StudentPriority` - Daily prioritized student list
   - `InterventionRecommendation` - AI-suggested interventions

5. **Feature Engineering Module**
   - Extract features from existing data:
     - Grade trends (slope, variance)
     - Attendance patterns (rate, consecutive absences)
     - Assignment submission timing (early/late patterns)
     - Wellness check-in history (stress trends, motivation trends)
     - Alert frequency (count, types)
     - Intervention history (count, outcomes)

6. **Gemini Integration Module**
   - Create `ml_models/gemini_client.py` - Wrapper for Gemini API
   - Implement prompt templates for each prediction type
   - Add error handling and retry logic
   - Implement response caching (Redis)

---

### **Phase 2: Predictive Risk Analysis** (Week 2)
**Goal**: Build ML model to predict future at-risk students

#### Tasks:
1. **Feature Selection**
   - GPA trend (last 4 weeks)
   - Attendance rate (last 4 weeks)
   - Missing assignments count
   - Wellness stress level (average last 3 check-ins)
   - Wellness motivation level (average last 3 check-ins)
   - Days since last intervention
   - Alert count (last 2 weeks)

2. **Gemini Prompt Engineering**
   - Design prompt template for risk prediction
   - Include student data context (grades, attendance, wellness)
   - Request structured JSON output
   - Example prompt:
     ```
     Analyze this student's data and predict their risk level:
     - Current GPA: 2.5 (was 3.2 last month)
     - Attendance: 70% (5 absences last 2 weeks)
     - Wellness: Stress=4/5, Motivation=2/5
     - Missing assignments: 3
     
     Provide JSON response with:
     - risk_probability (0-1)
     - confidence (0-1)
     - risk_factors (list)
     - recommendations (list)
     ```

3. **Prediction Pipeline**
   - `predict_student_risk(student_id)` function
   - Call Gemini API with student context
   - Parse JSON response
   - Returns: `{risk_probability: 0.75, confidence: 0.85, factors: [...]}`
   - Store predictions in `PredictionLog`
   - Cache results for 24 hours

4. **Integration**
   - Add "AI Risk Score" to student profile
   - Show confidence level (High/Medium/Low)
   - Display contributing factors
   - Create alerts for high-probability predictions

5. **UI Components**
   - Badge on student cards: "AI: 75% Risk"
   - Prediction explanation tooltip
   - Trend graph showing risk over time

---

### **Phase 3: Intervention Recommendation Engine** (Week 3)
**Goal**: Suggest personalized interventions based on similar cases

#### Tasks:
1. **Feature Engineering**
   - Student profile: risk factors, demographics, year level
   - Past interventions: type, outcome, duration
   - Similar student matching (clustering)

2. **Gemini-Powered Recommendations**
   - Send student profile + past intervention data to Gemini
   - Gemini analyzes patterns and suggests interventions
   - Prompt includes:
     - Student's risk factors
     - Past intervention outcomes (anonymized)
     - Available intervention types
   - Gemini returns ranked recommendations with reasoning

3. **Recommendation Output**
   ```python
   {
       "recommendations": [
           {
               "intervention_type": "One-on-One Counseling",
               "success_probability": 0.82,
               "reasoning": "Worked for 8/10 similar students",
               "similar_cases": 10
           },
           {
               "intervention_type": "Peer Tutoring",
               "success_probability": 0.65,
               "reasoning": "Effective for academic concerns",
               "similar_cases": 5
           }
       ]
   }
   ```

4. **Integration**
   - Add "AI Recommendations" section to Create Intervention page
   - Show ranked list with success probabilities
   - One-click to select recommended intervention
   - Track if counselor followed recommendation

5. **UI Components**
   - Recommendation cards with success rates
   - "Why this works" explanation
   - Similar case studies (anonymized)

---

### **Phase 4: Sentiment Analysis** (Week 4)
**Goal**: Analyze wellness check-in text for emotional distress

#### Tasks:
1. **Text Data Collection**
   - Add open-ended question to wellness check-in:
     - "How are you feeling today? (Optional)"
     - "Is there anything you'd like to share?"
   - Store in `WellnessCheckIn.text_response` field

2. **Gemini Sentiment Analysis**
   - Send wellness text responses to Gemini
   - Gemini analyzes sentiment and emotional tone
   - Detects concerning language patterns
   - Identifies specific emotions (sadness, anxiety, anger)
   - No need for keyword lists - Gemini understands context
   - Prompt example:
     ```
     Analyze this student's wellness response for emotional distress:
     "I'm feeling really overwhelmed. I can't keep up with everything."
     
     Provide JSON with:
     - sentiment (positive/neutral/negative)
     - confidence (0-1)
     - emotions (sadness, anxiety, anger scores)
     - concerning_phrases (list)
     - alert_level (none/low/medium/high)
     ```

3. **Sentiment Scoring**
   ```python
   {
       "sentiment": "negative",
       "confidence": 0.89,
       "emotion_scores": {
           "sadness": 0.75,
           "anxiety": 0.60,
           "anger": 0.20
       },
       "concerning_phrases": ["feeling hopeless", "can't do this"],
       "alert_level": "high"
   }
   ```

4. **Alert Generation**
   - Auto-create alert if:
     - Sentiment is negative with high confidence (>0.8)
     - Concerning keywords detected
     - Consecutive negative check-ins (3+)
   - Alert type: "Emotional Distress Detected"

5. **Integration**
   - Show sentiment badge on wellness history
   - Highlight concerning responses in red
   - Counselor dashboard: "Students with negative sentiment"
   - Email notification for high-alert cases

6. **UI Components**
   - Sentiment emoji indicators (😊😐😢)
   - Confidence bars
   - Flagged phrases highlighted
   - Trend graph: sentiment over time

---

### **Phase 5: Smart Student Prioritization** (Week 5)
**Goal**: Rank students by urgency for counselor attention

#### Tasks:
1. **Prioritization Algorithm**
   - Use Gemini to analyze and rank students
   - Send all at-risk student data to Gemini
   - Gemini considers:
     - Current risk score (40% weight)
     - Predicted risk trend
     - Days since last intervention
     - Alert frequency and severity
     - Recent behavioral changes
   - Gemini returns prioritized list with reasoning

2. **Daily Priority Calculation**
   - Run daily via Django command: `python manage.py update_priorities`
   - Or: Celery scheduled task (every morning at 8 AM)
   - Call Gemini API with batch of students
   - Store in `StudentPriority` model
   - Cache results for 24 hours Django command: `python manage.py update_priorities`
   - Or: Celery scheduled task (every morning at 8 AM)
   - Store in `StudentPriority` model

3. **Priority Output**
   ```python
   {
       "student_id": 123,
       "urgency_score": 8.5,
       "rank": 1,
       "reasoning": "High risk + declining trend + no intervention in 14 days",
       "recommended_action": "Schedule intervention within 24 hours",
       "factors": {
           "risk_score": 9.0,
           "predicted_risk": 0.85,
           "trend": "declining",
           "days_since_intervention": 14,
           "recent_alerts": 3
       }
   }
   ```

4. **Integration**
   - Counselor dashboard: "Today's Priority Students" widget
   - Sort students by urgency score (not just risk level)
   - Show reasoning for each ranking
   - Track if counselor acted on priority

5. **UI Components**
   - Priority badge: "Urgent", "High Priority", "Monitor"
   - Urgency score visualization (1-10 scale)
   - Reasoning tooltip
   - Action recommendations
   - "Mark as Addressed" button

---

### **Phase 6: Dashboard & Visualization** (Week 6)
**Goal**: Create AI insights dashboard for counselors and admins

#### Tasks:
1. **AI Predictions Dashboard**
   - Page: `/ml/predictions/`
   - Sections:
     - Predicted at-risk students (next 2 weeks)
     - Confidence distribution chart
     - Model accuracy metrics
     - Recent predictions log

2. **Model Performance Page**
   - Page: `/ml/model-insights/`
   - Sections:
     - Model accuracy over time
     - Feature importance chart
     - Prediction vs actual outcomes
     - Model version history
     - Last trained date

3. **Intervention Success Analytics**
   - Page: `/ml/intervention-analytics/`
   - Sections:
     - Success rate by intervention type
     - AI recommendation accuracy
     - Counselor follow-through rate
     - Best practices insights

4. **Sentiment Trends**
   - Page: `/ml/sentiment-trends/`
   - Sections:
     - School-wide sentiment over time
     - Students with declining sentiment
     - Concerning phrase frequency
     - Sentiment by grade level

5. **Charts & Visualizations**
   - Chart.js for interactive graphs
   - Heatmaps for risk distribution
   - Line graphs for trends
   - Bar charts for comparisons

---

## 🔄 Automation & Scheduling

### Daily Tasks (Celery Beat)
```python
# Run every day at 8:00 AM
@periodic_task(run_every=crontab(hour=8, minute=0))
def daily_predictions():
    # 1. Predict risk for all students
    # 2. Update priority rankings
    # 3. Generate alerts for high-risk predictions
    # 4. Send email digest to counselors
```

### Weekly Tasks
```python
# Run every Sunday at midnight
@periodic_task(run_every=crontab(day_of_week=0, hour=0, minute=0))
def weekly_model_evaluation():
    # 1. Evaluate model accuracy
    # 2. Compare predictions vs actual outcomes
    # 3. Log performance metrics
```

### Monthly Tasks
```python
# Run on 1st of every month
@periodic_task(run_every=crontab(day_of_month=1, hour=2, minute=0))
def monthly_model_retraining():
    # 1. Retrain models with new data
    # 2. Evaluate new model vs old model
    # 3. Deploy if accuracy improved
    # 4. Archive old model
```

---

## 📊 Database Schema

### New Models

```python
# ml_models/models.py

class ModelMetadata(models.Model):
    """Track ML model versions and performance"""
    model_name = models.CharField(max_length=100)  # 'risk_predictor', 'intervention_recommender'
    version = models.CharField(max_length=20)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    trained_date = models.DateTimeField(auto_now_add=True)
    training_data_size = models.IntegerField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

class PredictionLog(models.Model):
    """Store all AI predictions"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    prediction_type = models.CharField(max_length=50)  # 'risk', 'intervention', 'sentiment'
    prediction_value = models.JSONField()  # Store full prediction output
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=20)
    actual_outcome = models.CharField(max_length=50, null=True, blank=True)  # For evaluation
    was_accurate = models.BooleanField(null=True, blank=True)

class StudentPriority(models.Model):
    """Daily prioritized student list"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    urgency_score = models.FloatField()  # 0-10 scale
    rank = models.IntegerField()
    reasoning = models.TextField()
    factors = models.JSONField()  # Store all contributing factors
    recommended_action = models.CharField(max_length=200)
    was_addressed = models.BooleanField(default=False)
    addressed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='addressed_priorities')
    addressed_at = models.DateTimeField(null=True, blank=True)

class InterventionRecommendation(models.Model):
    """AI-suggested interventions"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    intervention_type = models.CharField(max_length=100)
    success_probability = models.FloatField()
    reasoning = models.TextField()
    similar_cases_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    was_selected = models.BooleanField(default=False)
    actual_intervention = models.ForeignKey('wellness.Intervention', on_delete=models.SET_NULL, null=True, blank=True)
    outcome_match = models.BooleanField(null=True, blank=True)  # Did it work as predicted?

class SentimentAnalysis(models.Model):
    """Sentiment analysis results for wellness check-ins"""
    wellness_checkin = models.OneToOneField('wellness.WellnessCheckIn', on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=20)  # 'positive', 'neutral', 'negative'
    confidence = models.FloatField()
    emotion_scores = models.JSONField()  # {'sadness': 0.75, 'anxiety': 0.60, ...}
    concerning_phrases = models.JSONField(default=list)
    alert_level = models.CharField(max_length=20)  # 'none', 'low', 'medium', 'high'
    alert_created = models.BooleanField(default=False)
    analyzed_at = models.DateTimeField(auto_now_add=True)
```

### Updated Models

```python
# wellness/models.py - Add to WellnessCheckIn
class WellnessCheckIn(models.Model):
    # ... existing fields ...
    text_response = models.TextField(blank=True, null=True)  # NEW: Open-ended response
    ai_sentiment = models.CharField(max_length=20, blank=True, null=True)  # NEW: AI sentiment
    ai_risk_score = models.FloatField(null=True, blank=True)  # NEW: AI predicted risk
```

---

## 🎨 UI/UX Enhancements

### Student Profile Page
```html
<!-- Add AI Insights Section -->
<div class="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg">
    <h3 class="text-lg font-bold mb-4">🤖 AI Insights</h3>
    
    <!-- Predicted Risk -->
    <div class="mb-4">
        <div class="flex items-center justify-between">
            <span>Predicted Risk (Next 2 Weeks)</span>
            <span class="text-2xl font-bold text-red-600">75%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div class="bg-red-600 h-2 rounded-full" style="width: 75%"></div>
        </div>
        <p class="text-sm text-gray-600 mt-2">Confidence: High (85%)</p>
    </div>
    
    <!-- Contributing Factors -->
    <div class="mb-4">
        <h4 class="font-semibold mb-2">Key Risk Factors:</h4>
        <ul class="space-y-1 text-sm">
            <li>📉 Declining grade trend (-15% last month)</li>
            <li>📅 3 consecutive absences</li>
            <li>😟 Negative wellness sentiment</li>
            <li>⏰ Late assignment submissions</li>
        </ul>
    </div>
    
    <!-- Recommended Actions -->
    <div class="bg-white p-4 rounded-lg">
        <h4 class="font-semibold mb-2">💡 AI Recommendations:</h4>
        <div class="space-y-2">
            <div class="flex items-center justify-between">
                <span class="text-sm">One-on-One Counseling</span>
                <span class="text-green-600 font-semibold">82% success</span>
            </div>
            <div class="flex items-center justify-between">
                <span class="text-sm">Academic Tutoring</span>
                <span class="text-green-600 font-semibold">75% success</span>
            </div>
        </div>
    </div>
</div>
```

### Counselor Dashboard
```html
<!-- Priority Students Widget -->
<div class="bg-white rounded-lg shadow p-6">
    <h3 class="text-xl font-bold mb-4">🎯 Today's Priority Students</h3>
    <div class="space-y-3">
        {% for priority in priority_students %}
        <div class="border-l-4 border-red-500 bg-red-50 p-4 rounded">
            <div class="flex items-center justify-between">
                <div>
                    <h4 class="font-bold">{{ priority.student.get_full_name }}</h4>
                    <p class="text-sm text-gray-600">{{ priority.reasoning }}</p>
                </div>
                <div class="text-right">
                    <div class="text-2xl font-bold text-red-600">{{ priority.urgency_score }}/10</div>
                    <span class="text-xs text-gray-500">Urgency Score</span>
                </div>
            </div>
            <div class="mt-3 flex gap-2">
                <button class="bg-red-600 text-white px-4 py-2 rounded text-sm">
                    Create Intervention
                </button>
                <button class="bg-gray-200 text-gray-700 px-4 py-2 rounded text-sm">
                    View Profile
                </button>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
```

---

## 🧪 Testing Strategy

### Unit Tests
- Test feature engineering functions
- Test prediction accuracy on sample data
- Test sentiment analysis on known texts
- Test prioritization algorithm

### Integration Tests
- Test end-to-end prediction pipeline
- Test alert generation from predictions
- Test recommendation selection workflow
- Test daily automation tasks

### Model Evaluation
- Cross-validation during training
- Confusion matrix analysis
- ROC curve and AUC score
- Precision-recall curves
- A/B testing (AI recommendations vs manual)

---

## 📈 Success Metrics

### Model Performance
- **Risk Prediction Accuracy**: Target >80%
- **Intervention Recommendation Success**: Target >70%
- **Sentiment Analysis Accuracy**: Target >85%
- **False Positive Rate**: Target <15%

### Business Impact
- **Early Detection Rate**: % of at-risk students caught early
- **Intervention Success Rate**: % of interventions that worked
- **Counselor Efficiency**: Time saved per week
- **Student Outcomes**: Improvement in GPA, attendance

### User Adoption
- **Counselor Usage**: % of recommendations followed
- **Alert Response Time**: Average time to address AI alerts
- **Dashboard Engagement**: Daily active users

---

## ⚠️ Risks & Mitigation

### Risk 1: Insufficient Training Data
- **Mitigation**: Start with simpler models, collect more data over time
- **Fallback**: Use rule-based system initially

### Risk 2: Model Bias
- **Mitigation**: Regular bias audits, diverse training data
- **Monitoring**: Track predictions by demographics

### Risk 3: Over-reliance on AI
- **Mitigation**: Always show confidence scores, require human review
- **Training**: Educate counselors on AI limitations

### Risk 4: Privacy Concerns
- **Mitigation**: Anonymize data, secure model storage
- **Compliance**: Follow data protection regulations

### Risk 5: Model Drift
- **Mitigation**: Monthly retraining, performance monitoring
- **Alerts**: Notify if accuracy drops below threshold

---

## 🚀 Deployment Plan

### Development Environment
1. Train models on development database
2. Test predictions on sample students
3. Validate UI components

### Staging Environment
1. Deploy models to staging
2. Run predictions on staging data
3. User acceptance testing with counselors

### Production Deployment
1. Deploy ml_models app
2. Upload trained models to server
3. Set up Celery for automation
4. Enable AI features with feature flag
5. Monitor performance for 1 week
6. Full rollout

### Rollback Plan
- Keep old system running in parallel
- Feature flag to disable AI features
- Revert to manual risk assessment if needed

---

## 📚 Documentation Needed

1. **User Guide**: How counselors use AI features
2. **Technical Docs**: Model architecture, API endpoints
3. **Training Guide**: How to retrain models
4. **Troubleshooting**: Common issues and fixes
5. **Ethics Policy**: AI usage guidelines

---

## 💰 Resource Requirements

### Development Time
- **Phase 1**: 5 days
- **Phase 2**: 7 days
- **Phase 3**: 7 days
- **Phase 4**: 7 days
- **Phase 5**: 5 days
- **Phase 6**: 7 days
- **Total**: ~6 weeks (1 developer)

### Infrastructure
- **Storage**: +500MB for models
- **Memory**: +1GB RAM for predictions
- **CPU**: Moderate (predictions are fast)
- **Optional**: GPU for sentiment analysis (faster)

### Third-Party Services
- **Hugging Face**: Free (for pre-trained models)
- **Redis**: Optional (for caching)
- **Celery**: Free (for scheduling)

---

## 🎓 Learning Resources

### For Developers
- Scikit-learn documentation
- Hugging Face Transformers guide
- Django + ML integration tutorials

### For Counselors
- AI predictions interpretation guide
- When to trust AI vs human judgment
- Best practices for using recommendations

---

## ✅ Next Steps

1. **Review this plan** with stakeholders
2. **Approve budget** and timeline
3. **Set up development environment**
4. **Start Phase 1**: Data preparation
5. **Weekly progress reviews**

---

## 📞 Support & Maintenance

### Ongoing Tasks
- Monthly model retraining
- Weekly performance monitoring
- Quarterly bias audits
- Annual model architecture review

### Support Channels
- Technical issues: Dev team
- Model questions: ML engineer
- User training: Product team

---

**Status**: Ready to implement  
**Priority**: High  
**Estimated Completion**: 6 weeks  
**Last Updated**: February 22, 2026
