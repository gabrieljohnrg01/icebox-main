import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from incubator.models import Startup, StartupMember

User = get_user_model()

def run_flow():
    c = Client()
    
    # 1. Login as Admin
    print("1. Logging in as Admin...")
    login_successful = c.login(username='admin', password='adminpassword')
    if not login_successful:
        print("FAIL: Could not login as admin.")
        return
    print("PASS: Admin logged in.")

    # 2. Add Startup
    print("\n2. Creating Startup 'Test Startup'...")
    try:
        response = c.post(reverse('add_startup'), {
            'name': 'Test Startup',
            'description': 'A test startup',
            'email': 'test@startup.com',
            'contact_number': '1234567890'
        }, follow=True)
        
        if response.status_code == 200:
            startup = Startup.objects.filter(name='Test Startup').last()
            print(f"PASS: Startup created (ID: {startup.id})")
        else:
            print(f"FAIL: Startup creation failed. Status: {response.status_code}")
            return
    except Exception as e:
        print(f"FAIL: Exception during startup creation: {e}")
        return

    # 3. Add Member
    print("\n3. Adding Member 'John Doe'...")
    try:
        response = c.post(reverse('add_member', args=[startup.id]), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'position': 'CTO',
            'contact_number': '555-0199'
        }, follow=True)

        if "Member John added!" in str(response.content) or User.objects.filter(email='john@example.com').exists():
            new_user = User.objects.filter(email='john@example.com').last()
            print(f"PASS: Member created. Username: {new_user.username}")
        else:
            # Check if user exists anyway
            if User.objects.filter(email='john@example.com').exists():
                 print("PASS: Member created (found in DB).")
            else:
                print("FAIL: Member creation might have failed.")
    except Exception as e:
         print(f"FAIL: Exception adding member: {e}")

    # 4. Login as New Member
    print("\n4. Logging in as New Member...")
    c.logout()
    member_usernames = [u.username for u in User.objects.filter(email='john@example.com')]
    if not member_usernames:
        print("FAIL: No member user found.")
        return
    
    username = member_usernames[0]
    password = 'password123' # Hardcoded in views.py
    
    if c.login(username=username, password=password):
         print(f"PASS: Logged in as {username}")
    else:
         print(f"FAIL: Could not login as {username} with default password.")
         return

    # 5. Submit Progress Report
    print("\n5. Submitting Progress Report...")
    try:
        response = c.post(reverse('submit_progress', args=[startup.id]), {
            'title': 'Week 1 Update',
            'description': 'Working on MVP',
            'achievements': 'Setup Django',
            'challenges': 'None',
            'next_steps': 'Build frontend'
        }, follow=True)
        
        if response.status_code == 200 and "Report submitted" in str(response.content):
             print("PASS: Report submitted.")
        elif response.status_code == 200:
             # Might verify by checking DB
             if startup.progress_reports.filter(title='Week 1 Update').exists():
                  print("PASS: Report found in DB.")
             else:
                  print("FAIL: Report not found in DB.")
        else:
             print(f"FAIL: Report submission failed. Status: {response.status_code}")

    except Exception as e:
        print(f"FAIL: Exception submitting report: {e}")

if __name__ == "__main__":
    run_flow()
