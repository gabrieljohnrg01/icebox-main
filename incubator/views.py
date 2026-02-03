from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Startup, StartupMember, ProgressReport, Milestone
from .forms import LoginForm, StartupForm, AdminCreationForm, ProgressReportForm, StartupMemberForm
from django.db.models import Count

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is None:
                # Try finding user by email
                try:
                    user_obj = User.objects.filter(email=username).first()
                    if user_obj:
                        user = authenticate(request, username=user_obj.username, password=password)
                except:
                    pass
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username/email or password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'super_admin':
        return super_admin_dashboard(request)
    elif user.role == 'admin':
        return admin_dashboard(request)
    else:
        return incubatee_dashboard(request)

def super_admin_dashboard(request):
    admins = User.objects.filter(role='admin')
    incubatees = User.objects.filter(role='incubatee')
    startups = Startup.objects.all()
    context = {
        'admins': admins, 
        'incubatees': incubatees, 
        'startups': startups,
        'total_startups': startups.count(),
        'total_users': User.objects.count()
    }
    return render(request, 'dashboard/super_admin.html', context)

def admin_dashboard(request):
    startups = Startup.objects.all()
    recent_reports = ProgressReport.objects.order_by('-submitted_at')[:10]
    context = {'startups': startups, 'recent_reports': recent_reports}
    return render(request, 'dashboard/admin.html', context)

def incubatee_dashboard(request):
    # Memberships
    startups = request.user.startups.all()
    context = {'startups': startups}
    return render(request, 'dashboard/incubatee.html', context)

@login_required
def add_admin(request):
    if request.user.role != 'super_admin':
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            admin_user = form.save(commit=False)
            admin_user.created_by = request.user
            admin_user.save()
            messages.success(request, f'Admin {admin_user.username} created!')
            return redirect('dashboard')
    else:
        form = AdminCreationForm()
    return render(request, 'super_admin/add_admin.html', {'form': form})

@login_required
def delete_user(request, user_id):
    # Allow Super Admin and Admin to access
    if request.user.role not in ['super_admin', 'admin']:
        return redirect('dashboard')
        
    target_user = get_object_or_404(User, id=user_id)
    
    # Protections
    if target_user.role == 'super_admin':
        messages.error(request, 'Cannot delete Super Admin.')
        return redirect('dashboard')
        
    if request.user.role == 'admin':
        # Admin can ONLY delete Incubatees
        if target_user.role != 'incubatee':
            messages.error(request, 'Admins can only delete Incubatees.')
            return redirect('dashboard')
            
    target_user.delete()
    messages.success(request, f'User {target_user.username} deleted.')
    return redirect('dashboard')

@login_required
def delete_startup(request, startup_id):
    # Allow Super Admin and Admin
    if request.user.role not in ['super_admin', 'admin']:
        return redirect('dashboard')
        
    startup = get_object_or_404(Startup, id=startup_id)
    startup.delete()
    messages.success(request, f'Startup {startup.name} deleted.')
    return redirect('dashboard')

@login_required
def add_startup(request):
    # Allow admins and super admins
    if request.user.role not in ['admin', 'super_admin']:
        return redirect('dashboard')

    if request.method == 'POST':
        form = StartupForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            startup = form.save(commit=False)
            startup.owner = request.user
            startup.save()
            
            # Auto-create default milestones
            for i in range(1, 5):
                Milestone.objects.create(
                    startup=startup,
                    milestone_progress=i,
                    title=f"Milestone {i}",
                    description=f"Default milestone {i} for {startup.name}",
                    status='pending'
                )

            messages.success(request, 'Startup created! Now add members.')
            return redirect('add_member', startup_id=startup.id)
    else:
        form = StartupForm(user=request.user)
    return render(request, 'startups/add_startup.html', {'form': form})

# ... view_startup ...
@login_required
def view_startup(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    # Check permission?
    milestones = startup.milestones.all()
    reports = startup.progress_reports.order_by('-submitted_at')
    
    context = {
        'startup': startup,
        'milestones': milestones,
        'reports': reports
    }
    return render(request, 'startups/view.html', context)

@login_required
def edit_startup(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    
    # Allow admins OR the owner (incubatee)
    is_owner = (request.user == startup.owner)
    is_admin = (request.user.role in ['admin', 'super_admin'])
    
    if not (is_admin or is_owner):
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = StartupForm(request.POST, request.FILES, instance=startup, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Startup updated.')
            return redirect('view_startup', startup_id=startup.id)
    else:
        form = StartupForm(instance=startup, user=request.user)
    return render(request, 'startups/edit.html', {'form': form, 'startup': startup})

@login_required
def add_member(request, startup_id):
    if request.user.role not in ['admin', 'super_admin']:
        return redirect('dashboard')
    
    startup = get_object_or_404(Startup, id=startup_id)
    
    if request.method == 'POST':
        form = StartupMemberForm(request.POST)
        if form.is_valid():
            # Extract data
            first_name = form.cleaned_data['first_name']
            middle_name = form.cleaned_data['middle_name']
            last_name = form.cleaned_data['last_name']
            position = form.cleaned_data['position']
            email = form.cleaned_data['email']
            contact = form.cleaned_data['contact_number']
            
            # Generate Username: lastname.firstname
            base_username = f"{last_name.lower()}.{first_name.lower()}".replace(" ", "")
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create User (Default password)
            password = "password123" 
            try:
                user = User.objects.create_user(
                    username=username, 
                    email=email, 
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    middle_name=middle_name,
                    contact_number=contact,
                    role='incubatee' 
                )
                
                # Link to Startup
                StartupMember.objects.create(
                    startup=startup,
                    user=user,
                    role=position
                )
                
                messages.success(request, f'Member {first_name} added! Username: {username}')
                return redirect('add_member', startup_id=startup.id)
            except Exception as e:
                messages.error(request, f"Error creating user: {e}")
    else:
        form = StartupMemberForm()

    return render(request, 'startups/add_member.html', {'form': form, 'startup': startup})

@login_required
def add_milestone(request, startup_id):
    if request.user.role not in ['admin', 'super_admin']:
        return redirect('dashboard')
    
    startup = get_object_or_404(Startup, id=startup_id)
    if request.method == 'POST':
        # Calculate next milestone number
        last_milestone = startup.milestones.order_by('-milestone_progress').first()
        next_num = (last_milestone.milestone_progress + 1) if last_milestone else 1
        
        Milestone.objects.create(
            startup=startup,
            milestone_progress=next_num,
            title=f"Milestone {next_num}",
            description="New added milestone",
            status='pending'
        )
        messages.success(request, f'Milestone {next_num} added!')
    
    return redirect('view_startup', startup_id=startup.id)

@login_required
def submit_progress(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)
    if request.method == 'POST':
        form = ProgressReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.startup = startup
            report.submitted_by = request.user
            report.save()
            messages.success(request, 'Report submitted.')
            return redirect('view_startup', startup_id=startup.id)
    else:
        form = ProgressReportForm()
    return render(request, 'startups/submit_report.html', {'form': form, 'startup': startup})

@login_required
def update_milestone_status(request, startup_id, milestone_id):
    # Helper to update status via AJAX or post
    pass
