# Gemini Free Tier Implementation Guide

## 🆓 Free Tier Limits (Gemini 1.5 Flash)

- **15 requests per minute (RPM)**
- **1 million tokens per day**
- **1,500 requests per day**

**Perfect for BrightTrack!** With smart caching and batching, this is more than enough.

---

## 💡 Optimization Strategy

### 1. Cache Everything (24 hours)
- Risk predictions: Update once daily
- Intervention recommendations: Cache per student
- Sentiment analysis: Cache after first analysis

### 2. Batch Processing
- Run predictions overnight (not real-time)
- Process all students in scheduled tasks
- Avoid API calls during user interactions

### 3. Smart Triggers
- Only analyze new wellness check-ins
- Only re-predict when data changes significantly
- Skip predictions for inactive students

---

## 📊 Usage Estimate (100 Students)

| Feature | Frequency | Daily Requests | Tokens/Request | Daily Tokens |
|---------|-----------|----------------|----------------|--------------|
| Risk Prediction | Daily | 100 | 500 | 50,000 |
| Sentiment Analysis | Per check-in | 20 | 300 | 6,000 |
| Intervention Rec | On-demand | 5 | 600 | 3,000 |
| Priority Ranking | Daily | 1 | 2,000 | 2,000 |
| **TOTAL** | | **126** | | **61,000** |

**Result**: Well within free tier limits! ✅

---

## 🚀 Implementation Plan (Free Tier Optimized)

### Phase 1: Setup (Day 1)

```bash
# Install only what we need
pip install google-generativeai python-dotenv

# Get free API key
# Visit: https://aistudio.google.com/app/apikey
```

### Phase 2: Gemini Client with Caching (Day 1)

```python
# ml_models/gemini_client.py
import google.generativeai as genai
from django.conf import settings
from django.core.cache import cache
import json
import hashlib

genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiClient:
    def __init__(self):
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
    
    def _get_cache_key(self, prompt):
        """Generate cache key from prompt"""
        return f"gemini_{hashlib.md5(prompt.encode()).hexdigest()}"
    
    def _call_with_cache(self, prompt, cache_hours=24):
        """Call Gemini with caching"""
        cache_key = self._get_cache_key(prompt)
        
        # Check cache first
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Call API
        response = self.model.generate_content(prompt)
        result = json.loads(response.text)
        
        # Cache result
        cache.set(cache_key, result, cache_hours * 3600)
        
        return result
    
    def predict_risk(self, student_data):
        prompt = f"""Analyze student risk level.
        
Data: GPA={student_data['gpa']}, Attendance={student_data['attendance']}%, 
Missing={student_data['missing']}, Stress={student_data['stress']}/5

Return JSON:
{{"risk_probability": 0.0-1.0, "risk_level": "low|medium|high", 
"risk_factors": ["factor1"], "recommendations": ["action1"]}}"""
        
        return self._call_with_cache(prompt, cache_hours=24)
    
    def analyze_sentiment(self, text):
        prompt = f"""Analyze emotional distress in: "{text}"

Return JSON:
{{"sentiment": "positive|neutral|negative", "confidence": 0.0-1.0,
"alert_level": "none|low|medium|high", "concerning_phrases": []}}"""
        
        return self._call_with_cache(prompt, cache_hours=168)  # 7 days
    
    def recommend_intervention(self, student_profile):
        prompt = f"""Recommend top 2 interventions for: {student_profile}

Return JSON:
{{"recommendations": [{{"type": "name", "success_probability": 0.0-1.0, 
"reasoning": "why"}}]}}"""
        
        return self._call_with_cache(prompt, cache_hours=24)
```

### Phase 3: Scheduled Daily Predictions (Day 2)

```python
# ml_models/management/commands/daily_ai_tasks.py
from django.core.management.base import BaseCommand
from accounts.models import User
from ml_models.gemini_client import GeminiClient
from ml_models.models import PredictionLog
import time

class Command(BaseCommand):
    help = 'Run daily AI predictions (free tier optimized)'
    
    def handle(self, *args, **options):
        client = GeminiClient()
        students = User.objects.filter(role='student', is_active=True)
        
        self.stdout.write(f"Processing {students.count()} students...")
        
        for i, student in enumerate(students):
            # Rate limiting: 15 RPM = 1 request per 4 seconds
            if i > 0 and i % 15 == 0:
                time.sleep(60)  # Wait 1 minute after 15 requests
            
            try:
                # Get student data
                data = {
                    'gpa': student.gpa or 0,
                    'attendance': self.calc_attendance(student),
                    'missing': self.count_missing(student),
                    'stress': self.avg_stress(student)
                }
                
                # Predict risk (cached for 24h)
                result = client.predict_risk(data)
                
                # Save prediction
                PredictionLog.objects.create(
                    student=student,
                    prediction_type='risk',
                    prediction_value=result,
                    confidence=result.get('confidence', 0.8)
                )
                
                self.stdout.write(f"✅ {student.username}: {result['risk_level']}")
                
            except Exception as e:
                self.stdout.write(f"❌ {student.username}: {e}")
        
        self.stdout.write("✅ Daily predictions complete!")
    
    def calc_attendance(self, student):
        # Your attendance calculation
        return 85
    
    def count_missing(self, student):
        # Your missing assignments count
        return 2
    
    def avg_stress(self, student):
        # Your stress calculation
        return 3
```

### Phase 4: Real-time Sentiment (Day 2)

```python
# wellness/views.py (add to wellness check-in submission)
from ml_models.gemini_client import GeminiClient
from ml_models.models import SentimentAnalysis

def submit_wellness_checkin(request):
    if request.method == 'POST':
        # ... existing code ...
        
        # Analyze sentiment if text provided
        if checkin.text_response:
            client = GeminiClient()
            result = client.analyze_sentiment(checkin.text_response)
            
            # Save analysis
            SentimentAnalysis.objects.create(
                wellness_checkin=checkin,
                sentiment=result['sentiment'],
                confidence=result['confidence'],
                alert_level=result['alert_level'],
                concerning_phrases=result.get('concerning_phrases', [])
            )
            
            # Create alert if high risk
            if result['alert_level'] in ['high', 'critical']:
                Alert.objects.create(
                    student=request.user,
                    alert_type='emotional_distress',
                    severity='high',
                    description=f"Negative sentiment detected"
                )
        
        # ... rest of code ...
```

### Phase 5: On-Demand Recommendations (Day 3)

```python
# wellness/views.py (add to create intervention page)
from ml_models.gemini_client import GeminiClient

def create_intervention(request, student_id):
    student = User.objects.get(id=student_id)
    
    # Get AI recommendations
    client = GeminiClient()
    profile = {
        'risk_level': student.risk_level,
        'issues': 'academic decline, low attendance',
        'year_level': student.year_level
    }
    
    ai_recommendations = client.recommend_intervention(profile)
    
    context = {
        'student': student,
        'ai_recommendations': ai_recommendations['recommendations']
    }
    
    return render(request, 'wellness/create_intervention.html', context)
```

---

## 🗓️ Cron Schedule (Run Daily at 2 AM)

```bash
# Add to crontab or use Django-cron
0 2 * * * cd /path/to/project && python manage.py daily_ai_tasks
```

Or use Django management command manually:
```bash
python manage.py daily_ai_tasks
```

---

## 📊 Minimal Database Models

```python
# ml_models/models.py
from django.db import models
from accounts.models import User

class PredictionLog(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    prediction_type = models.CharField(max_length=50)
    prediction_value = models.JSONField()
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class SentimentAnalysis(models.Model):
    wellness_checkin = models.OneToOneField('wellness.WellnessCheckIn', on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=20)
    confidence = models.FloatField()
    alert_level = models.CharField(max_length=20)
    concerning_phrases = models.JSONField(default=list)
    analyzed_at = models.DateTimeField(auto_now_add=True)
```

---

## 🎨 Simple UI Integration

```python
# accounts/views.py (student profile)
from ml_models.models import PredictionLog

def student_profile(request, student_id):
    student = User.objects.get(id=student_id)
    
    # Get latest AI prediction
    latest_prediction = PredictionLog.objects.filter(
        student=student,
        prediction_type='risk'
    ).first()
    
    context = {
        'student': student,
        'ai_prediction': latest_prediction.prediction_value if latest_prediction else None
    }
    
    return render(request, 'accounts/student_profile.html', context)
```

```html
<!-- accounts/student_profile.html -->
{% if ai_prediction %}
<div class="bg-purple-50 p-4 rounded-lg mt-4">
    <h4 class="font-bold mb-2">🤖 AI Risk Prediction</h4>
    <div class="flex items-center gap-4">
        <span class="text-3xl font-bold 
            {% if ai_prediction.risk_level == 'high' %}text-red-600
            {% elif ai_prediction.risk_level == 'medium' %}text-yellow-600
            {% else %}text-green-600{% endif %}">
            {{ ai_prediction.risk_level|upper }}
        </span>
        <div class="flex-1">
            <p class="text-sm text-gray-600 mb-1">Risk Factors:</p>
            <ul class="text-xs">
                {% for factor in ai_prediction.risk_factors %}
                <li>• {{ factor }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
</div>
{% endif %}
```

---

## ✅ Quick Start Checklist

- [ ] Get free Gemini API key
- [ ] Install `google-generativeai`
- [ ] Create `ml_models` app
- [ ] Add `GeminiClient` with caching
- [ ] Create `PredictionLog` model
- [ ] Create `daily_ai_tasks` command
- [ ] Add sentiment analysis to wellness
- [ ] Update student profile template
- [ ] Schedule daily cron job
- [ ] Test with sample data

---

## 🎯 Free Tier Best Practices

1. **Cache aggressively** - 24 hours for predictions
2. **Batch process** - Run overnight, not real-time
3. **Rate limit** - 15 requests/minute max
4. **Skip inactive** - Only process active students
5. **Reuse results** - Don't re-predict unchanged data

---

**Total Setup Time: 3 days** ⚡
**Cost: $0/month** 💰
**Perfect for your project!** ✅
