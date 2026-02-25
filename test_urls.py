from django.urls import reverse

try:
    counselor_url = reverse('ai_assistant:counselor_chat_view')
    print(f"✓ Counselor chat URL: {counselor_url}")
except Exception as e:
    print(f"✗ Counselor chat URL error: {e}")

try:
    admin_url = reverse('ai_assistant:admin_chat_view')
    print(f"✓ Admin chat URL: {admin_url}")
except Exception as e:
    print(f"✗ Admin chat URL error: {e}")

print("\nAll ai_assistant URLs:")
from django.urls import get_resolver
resolver = get_resolver()
for pattern in resolver.url_patterns:
    if 'ai' in str(pattern.pattern):
        print(f"  {pattern.pattern}")
