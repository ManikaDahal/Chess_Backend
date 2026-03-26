import os

settings_path = r'c:\Users\User\Desktop\Chess_Backend\django_project\settings.py'
stripe_config = """
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_key_here')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_key_here')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_your_key_here')
"""

with open(settings_path, 'a') as f:
    f.write(stripe_config)

print("Successfully appended Stripe configuration to settings.py")
