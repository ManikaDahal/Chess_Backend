import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

def record_migration(app, name):
    with connection.cursor() as cursor:
        # Check if already exists
        cursor.execute("SELECT id FROM django_migrations WHERE app = %s AND name = %s", [app, name])
        if cursor.fetchone():
            print(f"Migration {app}.{name} already recorded.")
            return

        print(f"Recording migration {app}.{name}...")
        from django.utils import timezone
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
            [app, name, timezone.now()]
        )
        print("Success.")

if __name__ == "__main__":
    record_migration('users', '0001_initial')
    record_migration('authentication', '0001_initial')
    record_migration('authentication', '0002_initial')
    record_migration('notifications', '0001_initial')
    record_migration('notifications', '0002_initial')
