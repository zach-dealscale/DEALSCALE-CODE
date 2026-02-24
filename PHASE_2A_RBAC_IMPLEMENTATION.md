# Phase 2A: Simple Role-Based Access Control Implementation

## Overview

This document summarizes the Phase 2A implementation of Role-Based Access Control (RBAC) for the DealScale platform. The implementation is **simple** and **client-facing**, showing only what the client needs to see while building infrastructure for Phase 2B/3 upselling.

---

## What the Client Sees (Simple UI)

### 1. **Single Role Toggle**: "Admin Access" ✅/❌

**Location**: `/auth/company/roles/create/` and `/auth/company/roles/edit/`

- **Admin Access = ON** (can_view_all_data = True)
  - User can manage all company settings
  - Can manage teams, roles, users
  - Can view all company data
  - Can access `/auth/company/*` pages
  - Crown badge (👑) shown in header with "(Admin)" label

- **Admin Access = OFF** (can_view_all_data = False)
  - User can only see deals/transcripts they created
  - Can see subordinates' deals if they are a manager
  - No access to `/auth/company/*` pages
  - User tie badge (🎩) shown in header with role name

### 2. **Deal/Client Visibility**

**Location**: Deal List (`/deals/`) and Deal Detail pages

**Simple Rules:**
- **Admin Users**: See ALL deals in company
- **Manager Users**: See own deals + subordinates' deals
- **Regular Users**: See only their own deals

**Visual Indicators**:
- "My Deal" badge: Deals created by current user
- "Team Member" badge: Deals created by subordinates

---

## What's Hidden in the System (For Phase 2B/3)

All these granular permissions are in the database and functional but **NOT shown in UI**:

```python
# Hidden permission flags (in Role model)
- can_manage_team          # Control team management access
- can_view_hierarchy_data  # View org chart
- can_manage_roles         # Manage role settings
- can_manage_clients       # Manage client records
- can_upload_transcripts   # Upload transcripts
- can_generate_reports     # Generate AI reports
```

**Note**: Owner will have `can_view_all_data=True` by default, giving them access to all hidden features.

---

## Technical Implementation

### 1. Core Mixin: `RoleBasedClientAccessMixin`

**File**: `apps/core/mixins.py`

**Purpose**: Filters clients/deals based on user role and hierarchy

```python
# Access Logic:
if user.role.can_view_all_data:
    # ADMIN: See all deals in company
    return Client.objects.filter(company=company)
else:
    # REGULAR: See own + subordinates' deals
    subordinate_ids = user.get_subordinate_ids()
    return Client.objects.filter(
        Q(primary_owner_id__in=subordinate_ids) |
        Q(created_by_id__in=subordinate_ids)
    )
```

**Usage**: Applied to all deal views

### 2. Company Management Protection: `CompanyManagementAccessMixin`

**File**: `apps/core/mixins.py`

**Purpose**: Protect `/auth/company/*` pages - only admins can access

```python
# Applied to:
- CompanySettingsView
- CompanyEditView
- RoleListView / RoleCreateView / RoleEditView / RoleDeleteView
- UserListView / UserInviteView / UserEditView / UserDeactivateView
- TeamListView / TeamCreateView / TeamEditView / TeamDeleteView
- etc.

# Non-admins are redirected to home with error message
```

### 3. Updated Views with Access Control

**File**: `apps/core/deal_views.py`

```python
# All deal views now use mixins:

class DealListView(LoginRequiredMixin, RoleBasedClientAccessMixin, TeamDashboardMixin, ListView):
    # - Filters deals based on role
    # - Shows team stats if user is manager
    # - Displays role badge and access info

class DealDetailView(LoginRequiredMixin, RoleBasedClientAccessMixin, TemplateView):
    # - Verifies user can access specific deal
    # - Shows 404 if unauthorized

class DealUpdateView(LoginRequiredMixin, RoleBasedClientAccessMixin, UpdateView):
    # - Checks access before allowing edit
    # - Shows error if user lacks permission

class DealDeleteView(LoginRequiredMixin, RoleBasedClientAccessMixin, DeleteView):
    # - Protects deletion with access check
```

### 4. Simplified Role UI Templates

**Files**:
- `apps/authentication/templates/authentication/company/roles/create.html`
- `apps/authentication/templates/authentication/company/roles/edit.html`

**Changes**:
- ❌ Removed all granular permission checkboxes
- ✅ Added single "Admin Access" toggle
- ✅ Added helpful description
- ✅ Added note: "All other permissions managed in the system based on this setting"

### 5. Role Badge in Header

**File**: `apps/core/templates/core/main_base.html`

**Display**:
```
Company Name
├─ 👑 Owner (Admin)          [Amber badge]
├─ 🎩 Manager (VP)           [Blue badge]
└─ 🎩 Sales Rep              [Blue badge]
```

---

## Database Schema (Unchanged)

**No migrations needed!** All models already support this:

```python
# CustomUser Model
user.company              # Multi-tenant scoping
user.role                 # ForeignKey to Role
user.manager              # Self-referential for hierarchy

# Role Model
role.can_view_all_data    # Single toggle we show
role.can_manage_team      # Hidden
role.can_manage_roles     # Hidden
role.can_manage_clients   # Hidden
# ... other hidden permissions

# Client/Deal Model
client.company            # Company scoping
client.primary_owner      # Who owns the deal
client.created_by         # Who created the deal
```

---

## User Experience Flow

### Scenario 1: Owner/Admin User

```
1. User logs in
2. Header shows: "Company Name" + "👑 Owner (Admin)" badge
3. User can access:
   - /deals/ → sees ALL company deals
   - /auth/company/users/ → manage users
   - /auth/company/roles/ → manage roles
   - /auth/company/teams/ → manage teams
   - /auth/company/hierarchy/ → view org chart
```

### Scenario 2: Manager User

```
1. User logs in
2. Header shows: "Company Name" + "🎩 Manager (VP)" badge
3. User can access:
   - /deals/ → sees own + team's deals
   - Dashboard shows team stats:
     - Team size: X members
     - Total deals: Y
   - Team member list
4. User CANNOT access:
   - /auth/company/users/ → redirected to home
   - /auth/company/roles/ → redirected to home
   - etc.
```

### Scenario 3: Sales Rep User

```
1. User logs in
2. Header shows: "Company Name" + "🎩 Sales Rep" badge
3. User can access:
   - /deals/ → sees only OWN deals
   - Cannot see "Team" section in dashboard
4. User CANNOT access:
   - /auth/company/* → all redirected to home
```

---

## Files Modified

### Created:
- ✅ `apps/core/mixins.py` - All access control mixins

### Updated:
- ✅ `apps/core/deal_views.py` - Added mixins to all deal views
- ✅ `apps/authentication/views_company.py` - Added access protection to company management views
- ✅ `apps/authentication/templates/authentication/company/roles/create.html` - Simplified role creation
- ✅ `apps/authentication/templates/authentication/company/roles/edit.html` - Simplified role editing
- ✅ `apps/core/templates/core/main_base.html` - Added role badge to header

---

## Security Features

### 1. **URL-Based Protection**
- Users cannot bypass via direct URL
- `/auth/company/*` pages check `can_view_all_data` before rendering
- Non-admins get 404 or redirect to home

### 2. **Deal Access Verification**
- Deal detail views verify access before loading
- Users cannot view/edit/delete deals they don't have access to

### 3. **Hierarchy-Aware Filtering**
- Managers automatically see subordinates' data
- Uses cached subordinate IDs for performance
- Recursive hierarchy support (multi-level reporting)

---

## Performance Optimizations

### 1. **Cached Subordinate IDs**
```python
# CustomUser.get_subordinate_ids(use_cache=True)
# Caches for 1 hour in Redis
# Reduces DB queries when filtering deals
```

### 2. **Query Optimization**
```python
# Uses select_related() and prefetch_related()
# Minimal N+1 queries
# Indexed fields:
#   - company + created_at
#   - company + primary_owner
```

---

## Future Phase 2B/3: Upselling Opportunity

When ready to charge more:

### Step 1: Unhide Granular Permissions
```python
# Same templates, but show all 7 permission toggles:
[ ] Can Manage Teams
[ ] Can View All Data        (already have this)
[ ] Can Manage Roles
[ ] Can Manage Clients
[ ] Can Upload Transcripts
[ ] Can Generate Reports
[ ] Can View Hierarchy Data
```

### Step 2: Implement Fine-Grained Checks
```python
# Views already check these, just need to enforce:

# Can user manage teams?
if not user.role.can_manage_team:
    raise Http404()

# Can user upload transcripts?
if not user.role.can_upload_transcripts:
    raise Http404()

# Can user generate reports?
if not user.role.can_generate_reports:
    raise Http404()
```

### Step 3: Create Feature Tiers
- **Tier 1** (Phase 2A): Simple role + deal visibility = $X/month
- **Tier 2** (Phase 2B): Advanced RBAC with 7 permissions = $X * 1.5/month
- **Tier 3** (Phase 3): Custom permission builder + audit logs = $X * 2.5/month

---

## Testing Checklist

```
✅ Owner can see all deals
✅ Owner can access /auth/company/* pages
✅ Manager can see own + subordinates' deals
✅ Manager cannot access /auth/company/* pages
✅ Rep can see only own deals
✅ Rep cannot see team member deals
✅ Deal detail 404s if user lacks access
✅ Deal edit prevents unauthorized users
✅ Deal delete prevents unauthorized users
✅ Role toggle (Admin Access) works correctly
✅ Role badge displays in header
✅ Team stats show for managers
✅ Dark mode works everywhere
```

---

## Client Communication

### For the Client:
```
"Phase 2A includes simple role-based access control:

✅ Define roles (Owner, Manager, Sales Rep, etc.)
✅ Toggle 'Admin Access' to give full company access
✅ Non-admins see only their own deals + team's deals
✅ Managers see dashboard with team performance

Future Phases:
- Advanced permissions (manage teams, roles, transcripts, etc.)
- Custom permission builder
- Audit logs and compliance reports
```

---

## Summary

**Phase 2A** delivers a clean, simple role-based system that:
1. ✅ Meets client requirements (basic role + deal visibility)
2. ✅ Builds foundation for future upselling (all permissions in DB)
3. ✅ Maintains security and data privacy
4. ✅ Provides excellent UX with role badges and team dashboards
5. ✅ Requires NO schema changes (already built in!)

**Next Phase**: Simply unhide permissions and enable feature-level checks for premium tier.
