from google import genai
from django.conf import settings
from django.core.cache import cache
import json
import hashlib

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
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
        
        # Call API with JSON mode
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        result = json.loads(response.text)
        
        # Cache result
        cache.set(cache_key, result, cache_hours * 3600)
        
        return result
    
    def predict_risk(self, student_data):
        """Predict student risk level"""
        prompt = f"""Analyze this student's academic risk level.

Student Data:
- GPA: {student_data.get('gpa', 0)}
- Attendance Rate: {student_data.get('attendance', 0)}%
- Missing Assignments: {student_data.get('missing', 0)}
- Stress Level: {student_data.get('stress', 0)}/5
- Motivation Level: {student_data.get('motivation', 0)}/5

Return JSON only:
{{
  "risk_probability": 0.0-1.0,
  "risk_level": "low|medium|high",
  "risk_factors": ["factor1", "factor2"],
  "recommendations": ["action1", "action2"]
}}"""
        
        return self._call_with_cache(prompt, cache_hours=24)
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of wellness check-in text"""
        prompt = f"""Analyze this student's wellness response for emotional distress.

Text: "{text}"

Return JSON only:
{{
  "sentiment": "positive|neutral|negative",
  "confidence": 0.0-1.0,
  "alert_level": "none|low|medium|high|critical",
  "concerning_phrases": ["phrase1"]
}}"""
        
        return self._call_with_cache(prompt, cache_hours=168)  # 7 days
    
    def recommend_intervention(self, student_profile):
        """Recommend interventions for at-risk student"""
        prompt = f"""Recommend top 2 interventions for this at-risk student.

Student Profile:
{json.dumps(student_profile, indent=2)}

Available interventions: One-on-One Counseling, Group Counseling, Academic Tutoring, Peer Mentoring, Parent Meeting, Study Skills Workshop

Return JSON only:
{{
  "recommendations": [
    {{
      "type": "intervention name",
      "success_probability": 0.0-1.0,
      "reasoning": "why this will work"
    }}
  ]
}}"""
        
        return self._call_with_cache(prompt, cache_hours=24)
    
    def analyze_academic_pattern(self, student_data):
        """Analyze academic performance patterns"""
        prompt = f"""Analyze this student's academic performance patterns.

Student Data:
- Attendance Records: {student_data.get('attendance_records', [])}
- Assignment Scores: {student_data.get('assignment_scores', [])}
- Grade Trend: {student_data.get('grade_trend', 'stable')}
- Recent Performance: {student_data.get('recent_performance', {})}

Return JSON only:
{{
  "pattern_type": "improving|declining|stable|inconsistent",
  "confidence": 0.0-1.0,
  "key_observations": ["observation1", "observation2"],
  "attendance_pattern": "regular|irregular|declining",
  "performance_pattern": "consistent|improving|declining|erratic",
  "risk_indicators": ["indicator1"],
  "recommendations": ["action1", "action2"]
}}"""
        
        return self._call_with_cache(prompt, cache_hours=24)
