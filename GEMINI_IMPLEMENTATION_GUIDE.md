# AI Implementation with Gemini API - Complete Guide

## ✅ Why Gemini API is Perfect for This Project

- **No ML expertise needed** - Just API calls
- **No model training** - Pre-trained and ready
- **Natural language understanding** - Better than traditional ML
- **Cost-effective** - Pay only for what you use
- **Always improving** - Google updates the model
- **JSON mode** - Structured responses guaranteed

---

## 🚀 Quick Start Guide

### Step 1: Get API Key
1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### Step 2: Install SDK
```bash
pip install google-generativeai python-dotenv
```

### Step 3: Configure
```python
# .env file
GEMINI_API_KEY=your_key_here

# settings.py
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

---

## 📝 Gemini Client Implementation

```python
# ml_models/gemini_client.py
import google.generativeai as genai
from django.conf import settings
import json
import time

genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiClient:
    def __init__(self, model_name='gemini-1.5-flash'):
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"response_mime_type": "application/json"}
        )
    
    def predict_risk(self, student_data):
        prompt = f"""
        Analyze this student and predict their academic risk level.
        
        Student Data:
        - GPA: {student_data['gpa']} (previous: {student_data['previous_gpa']})
        - Attendance: {student_data['attendance_rate']}%
        - Missing Assignments: {student_data['missing_assignments']}
        - Stress Level: {student_data['stress_level']}/5
        - Motivation: {student_data['motivation']}/5
        
        Return JSON:
        {{
          "risk_probability": 0.0-1.0,
          "confidence": 0.0-1.0,
          "risk_level": "low|medium|high",
          "risk_factors": ["factor1", "factor2"],
          "recommendations": ["action1", "action2"]
        }}
        """
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)
    
    def recommend_intervention(self, student_profile, past_interventions):
        prompt = f"""
        Recommend interventions for this at-risk student.
        
        Student: {student_profile}
        Past Success: {past_interventions}
        
        Return JSON with top 3 recommendations:
        {{
          "recommendations": [
            {{
              "type": "intervention name",
              "success_probability": 0.0-1.0,
              "reasoning": "why this works"
            }}
          ]
        }}
        """
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)
    
    def analyze_sentiment(self, text):
        prompt = f"""
        Analyze this student's wellness response for emotional distress.
        
        Text: "{text}"
        
        Return JSON:
        {{
          "sentiment": "positive|neutral|negative",
          "confidence": 0.0-1.0,
          "emotions": {{"sadness": 0.0-1.0, "anxiety": 0.0-1.0}},
          "alert_level": "none|low|medium|high|critical",
          "concerning_phrases": ["phrase1"]
        }}
        """
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)
    
    def prioritize_students(self, students_data):
        prompt = f"""
        Rank these students by urgency (who needs help first).
        
        Students: {json.dumps(students_data)}
        
        Return JSON:
        {{
          "prioritized": [
            {{
              "student_id": 123,
              "urgency_score": 0-10,
              "reasoning": "why urgent"
            }}
          ]
        }}
        """
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)
```

---

## 🎯 Feature Implementation

### 1. Predictive Risk Analysis

```python
# ml_models/predictors/risk_predictor.py
from ml_models.gemini_client import GeminiClient
from ml_models.models import PredictionLog
from django.core.cache import cache

def predict_student_risk(student_id):
    # Check cache first
    cache_key = f'risk_{student_id}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Get student data
    student = User.objects.get(id=student_id)
    data = {
        'gpa': student.gpa or 0,
        'previous_gpa': get_previous_gpa(student),
        'attendance_rate': calculate_attendance_rate(student),
        'missing_assignments': count_missing_assignments(student),
        'stress_level': get_avg_stress(student),
        'motivation': get_avg_motivation(student)
    }
    
    # Call Gemini
    client = GeminiClient()
    result = client.predict_risk(data)
    
    # Save prediction
    PredictionLog.objects.create(
        student=student,
        prediction_type='risk',
        prediction_value=result,
        confidence=result['confidence']
    )
    
    # Cache for 24 hours
    cache.set(cache_key, result, 86400)
    
    return result
```

### 2. Intervention Recommendations

```python
# ml_models/predictors/intervention_recommender.py
def recommend_interventions(student_id):
    student = User.objects.get(id=student_id)
    
    # Get student profile
    profile = {
        'risk_factors': get_risk_factors(student),
        'year_level': student.year_level,
        'issues': identify_issues(student)
    }
    
    # Get past intervention success rates
    past = get_intervention_stats()
    
    # Call Gemini
    client = GeminiClient()
    result = client.recommend_intervention(profile, past)
    
    # Save recommendations
    for rec in result['recommendations']:
        InterventionRecommendation.objects.create(
            student=student,
            intervention_type=rec['type'],
            success_probability=rec['success_probability'],
            reasoning=rec['reasoning']
        )
    
    return result
```

### 3. Sentiment Analysis

```python
# ml_models/predictors/sentiment_analyzer.py
def analyze_wellness_sentiment(checkin_id):
    checkin = WellnessCheckIn.objects.get(id=checkin_id)
    
    if not checkin.text_response:
        return None
    
    # Call Gemini
    client = GeminiClient()
    result = client.analyze_sentiment(checkin.text_response)
    
    # Save analysis
    SentimentAnalysis.objects.create(
        wellness_checkin=checkin,
        sentiment=result['sentiment'],
        confidence=result['confidence'],
        emotion_scores=result['emotions'],
        concerning_phrases=result['concerning_phrases'],
        alert_level=result['alert_level']
    )
    
    # Create alert if needed
    if result['alert_level'] in ['high', 'critical']:
        Alert.objects.create(
            student=checkin.student,
            alert_type='emotional_distress',
            severity='high',
            description=f"Negative sentiment detected: {result['concerning_phrases']}"
        )
    
    return result
```

### 4. Student Prioritization

```python
# ml_models/predictors/priority_ranker.py
def update_daily_priorities():
    # Get all at-risk students
    students = User.objects.filter(role='student', risk_level__in=['medium', 'high'])
    
    # Prepare data
    students_data = []
    for s in students:
        students_data.append({
            'id': s.id,
            'name': s.get_full_name(),
            'risk_level': s.risk_level,
            'gpa': s.gpa,
            'attendance': calculate_attendance_rate(s),
            'alerts': s.alerts.filter(resolved=False).count(),
            'days_since_intervention': days_since_last_intervention(s)
        })
    
    # Call Gemini
    client = GeminiClient()
    result = client.prioritize_students(students_data)
    
    # Save priorities
    for i, priority in enumerate(result['prioritized']):
        StudentPriority.objects.create(
            student_id=priority['student_id'],
            urgency_score=priority['urgency_score'],
            rank=i+1,
            reasoning=priority['reasoning']
        )
    
    return result
```

---

## 🎨 UI Integration Examples

### Student Profile - AI Insights Section

```html
<!-- Add to accounts/student_profile.html -->
{% if ai_prediction %}
<div class="bg-gradient-to-r from-purple-100 to-blue-100 p-6 rounded-lg mt-6">
    <h3 class="text-xl font-bold mb-4 flex items-center">
        <span class="text-2xl mr-2">🤖</span> AI Insights
    </h3>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Risk Prediction -->
        <div class="bg-white p-4 rounded-lg">
            <h4 class="font-semibold mb-2">Predicted Risk</h4>
            <div class="flex items-center justify-between mb-2">
                <span class="text-3xl font-bold 
                    {% if ai_prediction.risk_level == 'high' %}text-red-600
                    {% elif ai_prediction.risk_level == 'medium' %}text-yellow-600
                    {% else %}text-green-600{% endif %}">
                    {{ ai_prediction.risk_probability|floatformat:0 }}%
                </span>
                <span class="px-3 py-1 rounded-full text-sm
                    {% if ai_prediction.risk_level == 'high' %}bg-red-100 text-red-800
                    {% elif ai_prediction.risk_level == 'medium' %}bg-yellow-100 text-yellow-800
                    {% else %}bg-green-100 text-green-800{% endif %}">
                    {{ ai_prediction.risk_level|upper }}
                </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="h-2 rounded-full 
                    {% if ai_prediction.risk_level == 'high' %}bg-red-600
                    {% elif ai_prediction.risk_level == 'medium' %}bg-yellow-600
                    {% else %}bg-green-600{% endif %}"
                    style="width: {{ ai_prediction.risk_probability }}%"></div>
            </div>
            <p class="text-xs text-gray-500 mt-2">
                Confidence: {{ ai_prediction.confidence|floatformat:0 }}%
            </p>
        </div>
        
        <!-- Risk Factors -->
        <div class="bg-white p-4 rounded-lg">
            <h4 class="font-semibold mb-2">Key Risk Factors</h4>
            <ul class="space-y-1 text-sm">
                {% for factor in ai_prediction.risk_factors %}
                <li class="flex items-start">
                    <span class="text-red-500 mr-2">⚠️</span>
                    {{ factor }}
                </li>
                {% endfor %}
            </ul>
        </div>
    </div>
    
    <!-- AI Recommendations -->
    {% if ai_recommendations %}
    <div class="mt-4 bg-white p-4 rounded-lg">
        <h4 class="font-semibold mb-3">💡 AI Recommended Interventions</h4>
        <div class="space-y-2">
            {% for rec in ai_recommendations %}
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                    <span class="font-medium">{{ rec.intervention_type }}</span>
                    <p class="text-xs text-gray-600">{{ rec.reasoning }}</p>
                </div>
                <span class="text-green-600 font-bold">
                    {{ rec.success_probability|floatformat:0 }}% success
                </span>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
</div>
{% endif %}
```

### Counselor Dashboard - Priority Students

```html
<!-- Add to dashboard/counselor_dashboard.html -->
<div class="bg-white rounded-lg shadow p-6 mb-6">
    <h3 class="text-xl font-bold mb-4 flex items-center">
        <span class="text-2xl mr-2">🎯</span> Today's Priority Students
        <span class="ml-auto text-sm text-gray-500">AI-Ranked by Urgency</span>
    </h3>
    
    {% for priority in priority_students %}
    <div class="border-l-4 
        {% if priority.urgency_score >= 8 %}border-red-500 bg-red-50
        {% elif priority.urgency_score >= 5 %}border-yellow-500 bg-yellow-50
        {% else %}border-blue-500 bg-blue-50{% endif %}
        p-4 rounded mb-3">
        
        <div class="flex items-start justify-between">
            <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-bold">{{ priority.student.get_full_name }}</h4>
                    <span class="text-xs px-2 py-1 bg-gray-200 rounded">
                        Grade {{ priority.student.year_level }}
                    </span>
                </div>
                <p class="text-sm text-gray-700 mb-2">{{ priority.reasoning }}</p>
                <p class="text-xs text-gray-500">
                    Recommended: {{ priority.recommended_action }}
                </p>
            </div>
            
            <div class="text-right ml-4">
                <div class="text-3xl font-bold 
                    {% if priority.urgency_score >= 8 %}text-red-600
                    {% elif priority.urgency_score >= 5 %}text-yellow-600
                    {% else %}text-blue-600{% endif %}">
                    {{ priority.urgency_score|floatformat:1 }}
                </div>
                <span class="text-xs text-gray-500">Urgency</span>
            </div>
        </div>
        
        <div class="mt-3 flex gap-2">
            <a href="{% url 'create_intervention' priority.student.id %}" 
               class="bg-red-600 text-white px-4 py-2 rounded text-sm hover:bg-red-700">
                Create Intervention
            </a>
            <a href="{% url 'student_profile' priority.student.id %}" 
               class="bg-gray-200 text-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-300">
                View Profile
            </a>
        </div>
    </div>
    {% endfor %}
</div>
```

---

## 🔧 Django Management Commands

```python
# ml_models/management/commands/predict_risks.py
from django.core.management.base import BaseCommand
from accounts.models import User
from ml_models.predictors.risk_predictor import predict_student_risk

class Command(BaseCommand):
    help = 'Run AI risk predictions for all students'
    
    def handle(self, *args, **options):
        students = User.objects.filter(role='student')
        
        for student in students:
            try:
                result = predict_student_risk(student.id)
                self.stdout.write(
                    f"✅ {student.get_full_name()}: {result['risk_level']} "
                    f"({result['risk_probability']:.0%})"
                )
            except Exception as e:
                self.stdout.write(f"❌ Error for {student.id}: {e}")
```

```python
# ml_models/management/commands/update_priorities.py
from django.core.management.base import BaseCommand
from ml_models.predictors.priority_ranker import update_daily_priorities

class Command(BaseCommand):
    help = 'Update daily student priority rankings'
    
    def handle(self, *args, **options):
        result = update_daily_priorities()
        self.stdout.write(f"✅ Prioritized {len(result['prioritized'])} students")
```

---

## 💰 Cost Estimation

### Gemini 1.5 Flash Pricing (as of 2024)
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

### Example Costs:
- **Risk prediction per student**: ~500 tokens = $0.0004
- **100 students daily**: $0.04/day = $1.20/month
- **Sentiment analysis**: ~300 tokens = $0.0002
- **50 check-ins daily**: $0.01/day = $0.30/month

**Total estimated cost: ~$2-5/month for 100 students**

---

## ✅ Implementation Checklist

- [ ] Get Gemini API key
- [ ] Install google-generativeai
- [ ] Create ml_models app
- [ ] Implement GeminiClient
- [ ] Add database models
- [ ] Create risk predictor
- [ ] Create intervention recommender
- [ ] Create sentiment analyzer
- [ ] Create priority ranker
- [ ] Add UI components
- [ ] Create management commands
- [ ] Set up caching
- [ ] Test all features
- [ ] Deploy to production

---

**Ready to implement!** 🚀
