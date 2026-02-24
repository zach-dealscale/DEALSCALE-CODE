# Phase 2: Company Management Frontend - Architecture & Planning

## Overview

We need to build a complete company management interface accessible to all users initially, with access control via mixins/decorators in Phase 3.

**Current Status:** Django Admin ✅ | Views ❌ | Templates ❌

---

## 1. URL Structure & Page Map

### Main Dashboard
```
/dashboard/
  └─ Company Overview (Stats, Quick Actions)
```

### Company Management (`/company/`)
```
/company/
├── settings/
│   ├── overview/          # Company info, edit name, logo, website
│   ├── roles/             # Role CRUD
│   └── billing/           # (Future)
├── people/
│   ├── users/             # User management (list, create, edit, deactivate)
│   ├── teams/             # Team CRUD
│   └── team-members/      # Team membership management
└── activity/              # (Future - audit logs)
```

### Detailed Pages

| URL | Page | Action | Component |
|-----|------|--------|-----------|
| `/company/` | Company Dashboard | View | Overview stats |
| `/company/settings/` | Company Settings | View/Edit | Edit info |
| `/company/settings/roles/` | Roles Management | View | List all roles |
| `/company/settings/roles/create/` | Create Role | Create | Form |
| `/company/settings/roles/<id>/edit/` | Edit Role | Update | Form |
| `/company/settings/roles/<id>/delete/` | Delete Role | Delete | Confirm |
| `/company/people/users/` | Users Management | View | List all users |
| `/company/people/users/create/` | Invite User | Create | Form (email) |
| `/company/people/users/<id>/edit/` | Edit User | Update | Form |
| `/company/people/users/<id>/deactivate/` | Deactivate User | Update | Confirm |
| `/company/people/users/<id>/reactivate/` | Reactivate User | Update | Confirm |
| `/company/people/teams/` | Teams Management | View | List all teams |
| `/company/people/teams/create/` | Create Team | Create | Form |
| `/company/people/teams/<id>/edit/` | Edit Team | Update | Form |
| `/company/people/teams/<id>/delete/` | Delete Team | Delete | Confirm |
| `/company/people/teams/<id>/members/` | Team Members | View | List members |
| `/company/people/teams/<id>/members/add/` | Add Team Member | Create | Form (user select) |
| `/company/people/teams/<id>/members/<user_id>/remove/` | Remove Team Member | Delete | Confirm |

---

## 2. Directory Structure

```
apps/
└── core/  (or create apps/company_management/)
    ├── views/
    │   ├── __init__.py
    │   ├── dashboard.py         # Dashboard view
    │   ├── company.py           # Company CRUD
    │   ├── roles.py             # Role CRUD
    │   ├── users.py             # User management
    │   └── teams.py             # Team CRUD + membership
    │
    ├── forms/
    │   ├── __init__.py
    │   ├── company_forms.py      # Company edit form
    │   ├── role_forms.py         # Role create/edit form
    │   ├── user_forms.py         # User invite/edit form
    │   └── team_forms.py         # Team forms
    │
    ├── templates/
    │   └── company/
    │       ├── base.html         # Company section base
    │       ├── dashboard.html    # Dashboard
    │       ├── settings/
    │       │   ├── index.html    # Settings overview
    │       │   ├── company/
    │       │   │   ├── overview.html
    │       │   │   └── edit.html
    │       │   └── roles/
    │       │       ├── list.html
    │       │       ├── create.html
    │       │       └── edit.html
    │       └── people/
    │           ├── users/
    │           │   ├── list.html
    │           │   ├── create.html
    │           │   └── edit.html
    │           └── teams/
    │               ├── list.html
    │               ├── create.html
    │               ├── edit.html
    │               └── members.html
    │
    ├── urls.py                  # All company URLs
    └── mixins.py                # Access control mixins (Phase 3)
```

---

## 3. View Classes & Methods

### Dashboard Views

**DashboardView**
```python
class CompanyDashboardView(LoginRequiredMixin, View):
    """
    Overview of company with stats:
    - Total users
    - Active users
    - Total teams
    - Total roles
    - Quick actions
    """
    def get(self, request):
        company = request.user.company
        context = {
            'company': company,
            'total_users': company.users.count(),
            'active_users': company.users.filter(is_active_in_company=True).count(),
            'total_teams': company.teams.count(),
            'total_roles': company.roles.count(),
        }
        return render(request, 'company/dashboard.html', context)
```

### Company Settings

**CompanySettingsView** (GET)
```python
class CompanySettingsView(LoginRequiredMixin, View):
    """View company settings overview"""
    def get(self, request):
        company = request.user.company
        return render(request, 'company/settings/index.html', {'company': company})
```

**CompanyEditView** (GET/POST)
```python
class CompanyEditView(LoginRequiredMixin, View):
    """Edit company name, website, logo"""
    def get(self, request):
        company = request.user.company
        form = CompanyForm(instance=company)
        return render(request, 'company/settings/company/edit.html', {'form': form})

    def post(self, request):
        company = request.user.company
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company updated successfully')
            return redirect('company:settings')
        return render(request, 'company/settings/company/edit.html', {'form': form})
```

### Role Management

**RoleListView**
```python
class RoleListView(LoginRequiredMixin, View):
    """List all roles for company"""
    def get(self, request):
        company = request.user.company
        roles = company.roles.all().annotate(
            user_count=Count('users', filter=Q(users__is_active_in_company=True))
        )
        return render(request, 'company/settings/roles/list.html', {'roles': roles})
```

**RoleCreateView**
```python
class RoleCreateView(LoginRequiredMixin, View):
    """Create new role"""
    def get(self, request):
        form = RoleForm()
        return render(request, 'company/settings/roles/create.html', {'form': form})

    def post(self, request):
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.company = request.user.company
            role.save()
            messages.success(request, f'Role "{role.name}" created')
            return redirect('company:roles-list')
        return render(request, 'company/settings/roles/create.html', {'form': form})
```

**RoleEditView**
```python
class RoleEditView(LoginRequiredMixin, View):
    """Edit role"""
    def get(self, request, role_id):
        role = get_object_or_404(Role, id=role_id, company=request.user.company)
        form = RoleForm(instance=role)
        return render(request, 'company/settings/roles/edit.html', {'form': form, 'role': role})

    def post(self, request, role_id):
        role = get_object_or_404(Role, id=role_id, company=request.user.company)
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, f'Role "{role.name}" updated')
            return redirect('company:roles-list')
        return render(request, 'company/settings/roles/edit.html', {'form': form, 'role': role})
```

**RoleDeleteView**
```python
class RoleDeleteView(LoginRequiredMixin, View):
    """Delete role (with confirmation)"""
    def post(self, request, role_id):
        role = get_object_or_404(Role, id=role_id, company=request.user.company)
        if role.users.exists():
            messages.error(request, 'Cannot delete role with assigned users')
            return redirect('company:roles-list')

        role.delete()
        messages.success(request, f'Role deleted')
        return redirect('company:roles-list')
```

### User Management

**UserListView**
```python
class UserListView(LoginRequiredMixin, View):
    """List all users in company"""
    def get(self, request):
        company = request.user.company
        users = company.users.all().select_related('role', 'manager')

        # Filter by active/inactive
        status = request.GET.get('status', 'active')
        if status == 'active':
            users = users.filter(is_active_in_company=True)
        elif status == 'inactive':
            users = users.filter(is_active_in_company=False)

        context = {
            'users': users,
            'status': status,
        }
        return render(request, 'company/people/users/list.html', context)
```

**UserCreateView** (Invite)
```python
class UserCreateView(LoginRequiredMixin, View):
    """Invite new user to company"""
    def get(self, request):
        form = UserInviteForm()
        form.fields['role'].queryset = request.user.company.roles.all()
        return render(request, 'company/people/users/create.html', {'form': form})

    def post(self, request):
        form = UserInviteForm(request.POST)
        form.fields['role'].queryset = request.user.company.roles.all()

        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']

            # Check if user exists
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                # Create new user (with temporary password)
                user = CustomUser.objects.create_user(
                    email=email,
                    first_name=form.cleaned_data.get('first_name', ''),
                    last_name=form.cleaned_data.get('last_name', ''),
                )

            # Assign to company
            user.company = request.user.company
            user.role = role
            user.is_active_in_company = True
            user.joined_company_at = timezone.now()
            user.save()

            # Send invitation email (future)
            messages.success(request, f'User {email} invited to company')
            return redirect('company:users-list')

        return render(request, 'company/people/users/create.html', {'form': form})
```

**UserEditView**
```python
class UserEditView(LoginRequiredMixin, View):
    """Edit user details"""
    def get(self, request, user_id):
        user = get_object_or_404(
            CustomUser,
            id=user_id,
            company=request.user.company
        )
        form = UserEditForm(instance=user)
        form.fields['role'].queryset = request.user.company.roles.all()
        form.fields['manager'].queryset = request.user.company.users.exclude(id=user_id)

        return render(request, 'company/people/users/edit.html', {
            'form': form,
            'user_obj': user
        })

    def post(self, request, user_id):
        user = get_object_or_404(
            CustomUser,
            id=user_id,
            company=request.user.company
        )
        form = UserEditForm(request.POST, instance=user)
        form.fields['role'].queryset = request.user.company.roles.all()
        form.fields['manager'].queryset = request.user.company.users.exclude(id=user_id)

        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.email} updated')
            return redirect('company:users-list')

        return render(request, 'company/people/users/edit.html', {
            'form': form,
            'user_obj': user
        })
```

**UserDeactivateView**
```python
class UserDeactivateView(LoginRequiredMixin, View):
    """Deactivate user"""
    def post(self, request, user_id):
        user = get_object_or_404(
            CustomUser,
            id=user_id,
            company=request.user.company
        )
        user.is_active_in_company = False
        user.save()

        messages.success(request, f'User {user.email} deactivated')
        return redirect('company:users-list')
```

**UserReactivateView**
```python
class UserReactivateView(LoginRequiredMixin, View):
    """Reactivate user"""
    def post(self, request, user_id):
        user = get_object_or_404(
            CustomUser,
            id=user_id,
            company=request.user.company
        )
        user.is_active_in_company = True
        user.joined_company_at = timezone.now()
        user.save()

        messages.success(request, f'User {user.email} reactivated')
        return redirect('company:users-list')
```

### Team Management

**TeamListView**
```python
class TeamListView(LoginRequiredMixin, View):
    """List all teams"""
    def get(self, request):
        company = request.user.company
        teams = company.teams.all().annotate(
            member_count=Count('memberships', filter=Q(memberships__is_active=True))
        )
        return render(request, 'company/people/teams/list.html', {'teams': teams})
```

**TeamCreateView**
```python
class TeamCreateView(LoginRequiredMixin, View):
    """Create new team"""
    def get(self, request):
        form = TeamForm()
        form.fields['lead'].queryset = request.user.company.users.filter(is_active_in_company=True)
        return render(request, 'company/people/teams/create.html', {'form': form})

    def post(self, request):
        form = TeamForm(request.POST)
        form.fields['lead'].queryset = request.user.company.users.filter(is_active_in_company=True)

        if form.is_valid():
            team = form.save(commit=False)
            team.company = request.user.company
            team.created_by = request.user
            team.save()
            messages.success(request, f'Team "{team.name}" created')
            return redirect('company:teams-list')

        return render(request, 'company/people/teams/create.html', {'form': form})
```

**TeamEditView**
```python
class TeamEditView(LoginRequiredMixin, View):
    """Edit team"""
    def get(self, request, team_id):
        team = get_object_or_404(Team, id=team_id, company=request.user.company)
        form = TeamForm(instance=team)
        form.fields['lead'].queryset = request.user.company.users.filter(is_active_in_company=True)
        return render(request, 'company/people/teams/edit.html', {'form': form, 'team': team})

    def post(self, request, team_id):
        team = get_object_or_404(Team, id=team_id, company=request.user.company)
        form = TeamForm(request.POST, instance=team)
        form.fields['lead'].queryset = request.user.company.users.filter(is_active_in_company=True)

        if form.is_valid():
            form.save()
            messages.success(request, f'Team "{team.name}" updated')
            return redirect('company:teams-list')

        return render(request, 'company/people/teams/edit.html', {'form': form, 'team': team})
```

**TeamDeleteView**
```python
class TeamDeleteView(LoginRequiredMixin, View):
    """Delete team"""
    def post(self, request, team_id):
        team = get_object_or_404(Team, id=team_id, company=request.user.company)
        team.delete()
        messages.success(request, f'Team deleted')
        return redirect('company:teams-list')
```

**TeamMembersView**
```python
class TeamMembersView(LoginRequiredMixin, View):
    """Manage team members"""
    def get(self, request, team_id):
        team = get_object_or_404(Team, id=team_id, company=request.user.company)
        memberships = team.memberships.filter(is_active=True).select_related('user')

        return render(request, 'company/people/teams/members.html', {
            'team': team,
            'memberships': memberships
        })
```

**AddTeamMemberView**
```python
class AddTeamMemberView(LoginRequiredMixin, View):
    """Add member to team"""
    def get(self, request, team_id):
        team = get_object_or_404(Team, id=team_id, company=request.user.company)
        form = TeamMemberForm()
        # Only show users not already in team
        form.fields['user'].queryset = request.user.company.users.exclude(
            team_memberships__team=team,
            team_memberships__is_active=True
        )
        return render(request, 'company/people/teams/add_member.html', {
            'form': form,
            'team': team
        })

    def post(self, request, team_id):
        team = get_object_or_404(Team, id=team_id, company=request.user.company)
        form = TeamMemberForm(request.POST)
        form.fields['user'].queryset = request.user.company.users.exclude(
            team_memberships__team=team,
            team_memberships__is_active=True
        )

        if form.is_valid():
            user = form.cleaned_data['user']
            user.add_to_team(team, role_in_team=form.cleaned_data.get('role_in_team'))
            messages.success(request, f'{user.email} added to team')
            return redirect('company:team-members', team_id=team_id)

        return render(request, 'company/people/teams/add_member.html', {
            'form': form,
            'team': team
        })
```

**RemoveTeamMemberView**
```python
class RemoveTeamMemberView(LoginRequiredMixin, View):
    """Remove member from team"""
    def post(self, request, team_id, user_id):
        team = get_object_or_404(Team, id=team_id, company=request.user.company)
        user = get_object_or_404(CustomUser, id=user_id, company=request.user.company)

        user.remove_from_team(team)
        messages.success(request, f'{user.email} removed from team')
        return redirect('company:team-members', team_id=team_id)
```

---

## 4. Forms

**CompanyForm**
```python
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'website', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
```

**RoleForm**
```python
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'level', 'description', 'can_view_all_data', 'can_manage_team',
                  'can_view_hierarchy_data', 'can_manage_roles', 'can_manage_clients',
                  'can_upload_transcripts', 'can_generate_reports']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'can_view_all_data': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # ... etc for other checkboxes
        }
```

**UserInviteForm**
```python
class UserInviteForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.none())

    widgets = {
        'email': forms.EmailInput(attrs={'class': 'form-control'}),
        'first_name': forms.TextInput(attrs={'class': 'form-control'}),
        'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        'role': forms.Select(attrs={'class': 'form-control'}),
    }
```

**UserEditForm**
```python
class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'role', 'manager']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }
```

**TeamForm**
```python
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description', 'lead']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lead': forms.Select(attrs={'class': 'form-control'}),
        }
```

**TeamMemberForm**
```python
class TeamMemberForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    role_in_team = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Team Lead'})
    )
```

---

## 5. Template Structure

### Base Template (`company/base.html`)
```html
{% extends "base.html" %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <!-- Sidebar Navigation -->
        <div class="col-md-3 sidebar">
            <ul class="nav nav-pills flex-column">
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'company:dashboard' %}">Dashboard</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'company:settings' %}">Settings</a>
                    <ul class="nav nav-pills flex-column ms-3">
                        <li><a class="nav-link" href="{% url 'company:company-overview' %}">Company</a></li>
                        <li><a class="nav-link" href="{% url 'company:roles-list' %}">Roles</a></li>
                    </ul>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'company:users-list' %}">People</a>
                    <ul class="nav nav-pills flex-column ms-3">
                        <li><a class="nav-link" href="{% url 'company:users-list' %}">Users</a></li>
                        <li><a class="nav-link" href="{% url 'company:teams-list' %}">Teams</a></li>
                    </ul>
                </li>
            </ul>
        </div>

        <!-- Main Content -->
        <div class="col-md-9 main-content">
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}">{{ message }}</div>
                {% endfor %}
            {% endif %}

            {% block company_content %}{% endblock %}
        </div>
    </div>
</div>
{% endblock %}
```

### Dashboard Template (`company/dashboard.html`)
```html
{% extends "company/base.html" %}

{% block company_content %}
<div class="page-header">
    <h1>Company Dashboard</h1>
</div>

<div class="row">
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5>Total Users</h5>
                <p class="h2">{{ total_users }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5>Active Users</h5>
                <p class="h2">{{ active_users }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5>Total Teams</h5>
                <p class="h2">{{ total_teams }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5>Total Roles</h5>
                <p class="h2">{{ total_roles }}</p>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-6">
        <h3>Quick Actions</h3>
        <a href="{% url 'company:users-create' %}" class="btn btn-primary">Invite User</a>
        <a href="{% url 'company:teams-create' %}" class="btn btn-primary">Create Team</a>
    </div>
</div>
{% endblock %}
```

---

## 6. URL Configuration (`urls.py`)

```python
from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    # Dashboard
    path('', views.CompanyDashboardView.as_view(), name='dashboard'),

    # Settings
    path('settings/', views.CompanySettingsView.as_view(), name='settings'),
    path('settings/company/', views.CompanyOverviewView.as_view(), name='company-overview'),
    path('settings/company/edit/', views.CompanyEditView.as_view(), name='company-edit'),

    # Roles
    path('settings/roles/', views.RoleListView.as_view(), name='roles-list'),
    path('settings/roles/create/', views.RoleCreateView.as_view(), name='role-create'),
    path('settings/roles/<str:role_id>/edit/', views.RoleEditView.as_view(), name='role-edit'),
    path('settings/roles/<str:role_id>/delete/', views.RoleDeleteView.as_view(), name='role-delete'),

    # Users
    path('people/users/', views.UserListView.as_view(), name='users-list'),
    path('people/users/create/', views.UserCreateView.as_view(), name='users-create'),
    path('people/users/<str:user_id>/edit/', views.UserEditView.as_view(), name='user-edit'),
    path('people/users/<str:user_id>/deactivate/', views.UserDeactivateView.as_view(), name='user-deactivate'),
    path('people/users/<str:user_id>/reactivate/', views.UserReactivateView.as_view(), name='user-reactivate'),

    # Teams
    path('people/teams/', views.TeamListView.as_view(), name='teams-list'),
    path('people/teams/create/', views.TeamCreateView.as_view(), name='team-create'),
    path('people/teams/<str:team_id>/edit/', views.TeamEditView.as_view(), name='team-edit'),
    path('people/teams/<str:team_id>/delete/', views.TeamDeleteView.as_view(), name='team-delete'),

    # Team Members
    path('people/teams/<str:team_id>/members/', views.TeamMembersView.as_view(), name='team-members'),
    path('people/teams/<str:team_id>/members/add/', views.AddTeamMemberView.as_view(), name='team-member-add'),
    path('people/teams/<str:team_id>/members/<str:user_id>/remove/', views.RemoveTeamMemberView.as_view(), name='team-member-remove'),
]
```

---

## 7. Access Control Mixins (Phase 3)

```python
from django.contrib.auth.mixins import UserPassesTestMixin

class CompanyAccessMixin(UserPassesTestMixin):
    """Ensure user belongs to company"""
    def test_func(self):
        return self.request.user.company is not None

class CompanyOwnerMixin(UserPassesTestMixin):
    """Ensure user is company owner"""
    def test_func(self):
        return (self.request.user.company and
                self.request.user.role.name == 'Owner')

class RoleManagementMixin(UserPassesTestMixin):
    """Ensure user can manage roles"""
    def test_func(self):
        return (self.request.user.company and
                self.request.user.role and
                self.request.user.role.can_manage_roles)

class TeamManagementMixin(UserPassesTestMixin):
    """Ensure user can manage teams"""
    def test_func(self):
        return (self.request.user.company and
                self.request.user.role and
                self.request.user.role.can_manage_team)
```

---

## Summary

| Component | Location | Status |
|-----------|----------|--------|
| Views (12 classes) | `apps/core/views/` | 📋 Planned |
| Forms (6 classes) | `apps/core/forms/` | 📋 Planned |
| Templates (12 files) | `apps/core/templates/company/` | 📋 Planned |
| URLs | `apps/core/urls.py` | 📋 Planned |
| Mixins | `apps/core/mixins.py` | 📋 Phase 3 |

**Next Step:** Review this plan, then we start building! 🚀

