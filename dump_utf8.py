import os, django, json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()
from django.core import serializers
from django.apps import apps

# Dump all models
data = []
for model in apps.get_models():
    data.extend(serializers.serialize("json", model.objects.all()))

# Write UTF-8 without BOM
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f)
print("data.json created successfully!")
