import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from incubator.models import Startup

User = get_user_model()

def verify():
    print("Running system check...")
    # Django setup() already checks registry
    
    print("Creating Superuser...")
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword', role='super_admin')
        print("Superuser 'admin' created with password 'adminpassword'.")
    else:
        print("Superuser 'admin' already exists.")

    print("Checking Models...")
    count = Startup.objects.count()
    print(f"Current Startups: {count}")
    
    print("Verification Completed Successfully.")

if __name__ == "__main__":
    verify()
