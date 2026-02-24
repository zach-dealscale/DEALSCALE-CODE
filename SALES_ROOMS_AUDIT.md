# Sales Rooms - Multi-Tenant Audit & Compliance Check
**Date:** 2025-11-07
**Status:** COMPREHENSIVE AUDIT COMPLETE
**Scope:** Models, Views, URLs, Guest User Relations, Company Scoping

---

## Executive Summary

✅ **MODELS:** Excellent - All models have proper company and creator tracking
⚠️ **VIEWS:** Partial - List/Create views need role-based filtering (like DealListView)
⚠️ **URLS:** Good structure but no access control at routing level
✅ **GUEST USERS:** Properly connected via ForeignKey to SalesRoom
✅ **COMPANY SCOPING:** All models have company field with auto-set in save()

---

## Part 1: Model Analysis

### 1.1 SalesRoom Model ✅ EXCELLENT

**File:** `apps/sale_rooms/models.py` (lines 15-52)

**Fields:**
```python
user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sale_rooms', null=True, blank=True)
client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='sales_room')
company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales_rooms', null=True, blank=True)
created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_sales_rooms')
```

**Save Method:**
```python
def save(self, *args, **kwargs):
    """Auto-set company from client if not already set."""
    if not self.company:
        if self.client and self.client.company:
            self.company = self.client.company
    if not self.created_by and self.user:
        self.created_by = self.user
    super().save(*args, **kwargs)
```

**Assessment:** ✅ **PERFECT**
- Company field properly cascades from client
- created_by automatically assigned from user
- Indexes: `salesroom_company_created_idx`
- OneToOne with Client ensures clean relationship
- Fallback auto-set in save()

---

### 1.2 SalesRoomMedia Model ✅ EXCELLENT

**File:** `apps/sale_rooms/models.py` (lines 55-142)

**Fields:**
```python
sales_room = models.ForeignKey(SalesRoom, on_delete=models.CASCADE, related_name='media')
uploaded_by_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
uploaded_by_guest = models.ForeignKey(GuestUser, null=True, blank=True, on_delete=models.SET_NULL)
company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales_room_media', null=True, blank=True)
document = models.ForeignKey('report_management.ReportDocument', on_delete=models.CASCADE, related_name='media', blank=True, null=True)
```

**Save Method:**
```python
def save(self, *args, **kwargs):
    """Auto-set company from sales_room or document if not already set."""
    if not self.company:
        if self.sales_room and self.sales_room.company:
            self.company = self.sales_room.company
        elif self.document and self.document.company:
            self.company = self.document.company
    super().save(*args, **kwargs)
```

**Assessment:** ✅ **PERFECT**
- Dual user tracking: `uploaded_by_user` AND `uploaded_by_guest`
- Company auto-cascades from sales_room → document
- Helper property `uploaded_by` returns dict with name/id
- Indexes: `sroommed_company_uploaded_idx`
- File properties: file_type, file_size, file_url

---

### 1.3 Comment Model ✅ EXCELLENT

**File:** `apps/sale_rooms/models.py` (lines 144-203)

**Fields:**
```python
document = models.ForeignKey('report_management.ReportDocument', on_delete=models.CASCADE, related_name='document_comments')
parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
created_by_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
created_by_guest = models.ForeignKey(GuestUser, null=True, blank=True, on_delete=models.SET_NULL)
company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
```

**Save Method:**
```python
def save(self, *args, **kwargs):
    """Auto-set company from document if not already set."""
    if not self.company and self.document and self.document.company:
        self.company = self.document.company
    super().save(*args, **kwargs)
```

**Assessment:** ✅ **PERFECT**
- Dual creator tracking: `created_by_user` AND `created_by_guest`
- Threaded replies via self-reference
- Company cascades from document
- Property `author_name` handles both user/guest
- Indexes: `cmt_co_doc_created_idx`

---

### 1.4 MutualActionItem Model ✅ EXCELLENT

**File:** `apps/sale_rooms/models.py` (lines 205-261)

**Fields:**
```python
sales_room = models.ForeignKey(SalesRoom, on_delete=models.CASCADE, related_name='action_items')
created_by_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
created_by_guest = models.ForeignKey(GuestUser, null=True, blank=True, on_delete=models.SET_NULL)
guest_assignee = models.ForeignKey(GuestUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='guest_actions')
admin_assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='admin_actions')
company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='action_items', null=True, blank=True)
```

**Save Method:**
```python
def save(self, *args, **kwargs):
    """Auto-set company from sales_room if not already set."""
    if not self.company and self.sales_room and self.sales_room.company:
        self.company = self.sales_room.company
    super().save(*args, **kwargs)
```

**Assessment:** ✅ **PERFECT**
- Dual creator + dual assignee tracking
- Company cascades from sales_room
- Status and priority choices
- Overdue notification tracking
- Indexes: `actionitem_company_status_idx`, `actionitem_company_due_idx`

---

### 1.5 ClientContact Model ✅ EXCELLENT

**File:** `apps/sale_rooms/models.py` (lines 263-326)

**Fields:**
```python
client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_contacts', null=True, blank=True)
user_account = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Linked user account if contact has login access")
company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='client_contacts', null=True, blank=True)
```

**Save Method:**
```python
def save(self, *args, **kwargs):
    """Auto-set company from client if not already set."""
    if not self.company and self.client and self.client.company:
        self.company = self.client.company
    super().save(*args, **kwargs)
```

**Assessment:** ✅ **PERFECT**
- Links contacts to client accounts
- OneToOne with User for login access
- Company cascades from client
- Salesforce integration support
- Indexes: `cntc_company_client_idx`

---

### 1.6 GuestUser Model ⚠️ NEEDS IMPROVEMENT

**File:** `apps/authentication/models.py` (lines 492-502)

**Current:**
```python
class GuestUser(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    visit_count = models.IntegerField(default=0)
    sales_room = models.ForeignKey("sale_rooms.SalesRoom", on_delete=models.CASCADE, related_name="visitors", null=True, blank=True)
```

**Assessment:** ⚠️ **MISSING COMPANY FIELD**

**Issues:**
1. ❌ No `company` field
2. ❌ No `created_by` tracking (if needed)
3. ✅ Has `sales_room` ForeignKey (good)
4. ❌ No auto-set mechanism
5. ❌ No indexes for performance

**Recommendation:** Add company field to GuestUser:
```python
# ✅ NEW: Company-level scoping
company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='guest_users',
    null=True,
    blank=True
)

def save(self, *args, **kwargs):
    """Auto-set company from sales_room if not already set."""
    if not self.company and self.sales_room and self.sales_room.company:
        self.company = self.sales_room.company
    super().save(*args, **kwargs)
```

---

### 1.7 GuestUserSessionKey Model ✅ GOOD

**File:** `apps/authentication/models.py` (lines 505-525)

**Assessment:** ✅ **ADEQUATE**
- Properly linked to GuestUser via ForeignKey
- Session key auto-generated on save()
- 30-day expiry
- Could benefit from company field for audit trail

---

## Part 2: View Analysis

### 2.1 SalesRoomListView ⚠️ NEEDS FILTERING

**File:** `apps/sale_rooms/room_views/user_room.py` (lines 50-98)

**Current:**
```python
class SalesRoomListView(LoginRequiredMixin, TemplateView):
    template_name = "sales_rooms/sales_room_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_q = self.request.GET.get("q")
        rooms = SalesRoom.objects.filter(user=self.request.user)  # ❌ ONLY USER'S ROOMS
```

**Issues:**
1. ❌ Filters by `user=request.user` (hardcoded)
2. ❌ Doesn't respect role hierarchy
3. ❌ Managers can't see subordinates' rooms
4. ❌ Admins can't see all company rooms
5. ✅ Has search and annotations

**Recommendation:** Apply RoleBasedClientAccessMixin pattern:
```python
class SalesRoomListView(LoginRequiredMixin, RoleBasedClientAccessMixin, TemplateView):
    template_name = "sales_rooms/sales_room_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Use role-based filtering via mixin
        accessible_clients = self.get_accessible_clients(user)
        rooms = SalesRoom.objects.filter(client__in=accessible_clients)

        search_q = self.request.GET.get("q")
        if search_q:
            rooms = rooms.filter(name__icontains=search_q)
```

---

### 2.2 SalesRoomDetailView ⚠️ NEEDS ACCESS VERIFICATION

**File:** `apps/sale_rooms/room_views/user_room.py` (lines 102-109)

**Current:**
```python
class SalesRoomDetailView(LoginRequiredMixin, View):
    template_name = 'sales_rooms/sales_room_detail.html'

    def get(self, request, uuid):
        try:
            sales_room = self.get_sales_room(uuid)  # ❌ NO ACCESS CHECK
```

**Issue:** No verification that user can access this room

**Recommendation:**
```python
def get_sales_room(self, uuid):
    sales_room = get_object_or_404(SalesRoom, uuid=uuid)

    # Verify user has access to this room's client
    accessible_clients = self.get_accessible_clients(self.request.user)
    if not accessible_clients.filter(pk=sales_room.client_id).exists():
        messages.error(self.request, "You don't have access to this sales room.")
        raise Http404("Sales room not found or access denied.")

    return sales_room
```

---

### 2.3 SalesRoomCreateView ⚠️ NEEDS ROLE-BASED FILTERING

**File:** `apps/sale_rooms/room_views/user_room.py` (lines 690-735)

**Current:**
```python
class SalesRoomCreateView(LoginRequiredMixin, FormView):
    def get_clients_data(self):
        clients = Client.objects.filter(user=self.request.user)  # ❌ HARDCODED

    def form_valid(self, form):
        sales_room = form.save(commit=False)
        sales_room.user = self.request.user  # ❌ MISSING COMPANY + CREATED_BY
        sales_room.save()
```

**Issues:**
1. ❌ `get_clients_data()` only shows user's own clients
2. ❌ `created_by` not set
3. ✅ Company will auto-set from client
4. Managers should see their team's clients

**Recommendation:**
```python
def form_valid(self, form):
    sales_room = form.save(commit=False)
    sales_room.user = self.request.user
    sales_room.company = self.request.user.company  # ✅ EXPLICIT
    sales_room.created_by = self.request.user       # ✅ EXPLICIT
    sales_room.save()
```

---

### 2.4 GuestLoginView ✅ GOOD (No Auth Required - By Design)

**File:** `apps/sale_rooms/room_views/guest_room.py` (lines 44-82)

**Assessment:** ✅ **ADEQUATE FOR GUEST ACCESS**
- No login required (public room access)
- Creates GuestUser if not exists
- Sets `sales_room` ForeignKey
- Creates session key
- ⚠️ Should set company via sales_room.company

---

### 2.5 GuestRoomView ✅ PROPER FILTERING

**File:** `apps/sale_rooms/room_views/guest_room.py` (lines 99-113)

**Current:**
```python
def get(self, request, uuid, *args, **kwargs):
    try:
        sales_room = SalesRoom.objects.get(uuid=uuid)  # ✅ SAFE - PUBLIC LOOKUP
    except SalesRoom.DoesNotExist:
        return JsonResponse({'error': 'Sales room not found'}, status=404)

    documents = ReportDocument.objects.filter(sales_room=sales_room)  # ✅ SCOPED
```

**Assessment:** ✅ **CORRECT**
- Looks up by uuid (safe)
- Filters documents by room (proper scoping)
- No user access check needed (guest route)

---

## Part 3: URL Routing Analysis

**File:** `apps/sale_rooms/urls.py`

### Issues Found:

1. ⚠️ **No access control at routing level** - Relies on view-level checks
2. ⚠️ **UUID lookup is safe** - Can't enumerate (good cryptographic UUIDs)
3. ✅ **Guest routes public** - Correct (no auth required)
4. ✅ **Authenticated routes use LoginRequiredMixin** - Good pattern

### URL Structure:

```
Authenticated Routes:
├── /rooms/                              → SalesRoomListView
├── /rooms/create/                       → SalesRoomCreateView
├── /rooms/<uuid>/                       → SalesRoomDetailView
├── /rooms/<uuid>/edit/                  → SalesRoomEditView
├── /rooms/<uuid>/delete/                → SalesRoomDeleteView
└── /rooms/<uuid>/upload/                → UploadMediaFileView

Guest Routes (No Auth):
├── /guest-room/<uuid>/access/           → GuestLoginView
├── /guest-room/<uuid>/documents/        → GuestRoomView
├── /guest-room/<uuid>/media/            → GuestRoomMediaView
└── /guest-room/<uuid>/                  → GuestRoomDashboard
```

**Assessment:** ✅ **ROUTING IS CLEAN** - Access control delegated to views (correct pattern)

---

## Part 4: Creation Flow - Room & Company Tracking

### 4.1 SalesRoom Creation

**Flow:**
```
User creates room (form submission)
    ↓
SalesRoomCreateView.form_valid()
    ├─ sales_room = form.save(commit=False)
    ├─ sales_room.user = request.user
    ├─ sales_room.company = request.user.company  (❌ NOT SET EXPLICITLY)
    ├─ sales_room.created_by = request.user       (❌ NOT SET)
    └─ sales_room.save()  → Auto-sets company from client ✅

Result: ✅ Company is set (via auto-set from client)
        ❌ created_by not explicitly set (relies on save())
```

**Recommendation:** Set both explicitly:
```python
sales_room.company = self.request.user.company
sales_room.created_by = self.request.user
```

### 4.2 GuestUser Creation

**Flow:**
```
Guest accesses room (GuestLoginView)
    ↓
guest_user, created = GuestUser.objects.get_or_create(email=email)
    ├─ guest_user.name = name
    ├─ guest_user.sales_room = sales_room
    ├─ guest_user.save()  → ❌ NO COMPANY SET (NO AUTO-SET MECHANISM)
    └─ No company field yet

Result: ❌ Company not set
        ✅ sales_room is set (good ForeignKey)
```

**Recommendation:**
1. Add company field to GuestUser
2. Add auto-set in save()
3. Set explicitly in view: `guest_user.company = sales_room.company`

---

## Part 5: Filtering & Access Control Summary

| Component | Current State | Issue | Impact |
|-----------|---------------|-------|--------|
| SalesRoomListView | user=request.user | No role filtering | Managers can't see team rooms |
| SalesRoomDetailView | No access check | User from URL can access | Access control missing |
| SalesRoomCreateView | user=request.user | No created_by | Can't audit creator |
| GuestUser model | No company field | Can't query by company | Reporting/filtering broken |
| GuestLoginView | No company set | Orphaned records | Data integrity issue |
| Comments/Actions | Has company field ✅ | Company properly scoped | OK |
| Media files | Has company field ✅ | Company properly scoped | OK |

---

## Part 6: Guest User Relationships - Current State

### Current ForeignKey Relationships:

```
GuestUser
├─ sales_room → SalesRoom (✅ has this)
├─ company → Company (❌ MISSING)
└─ sessions → GuestUserSessionKey (inverse relation, good)

GuestUserSessionKey
├─ guest_user → GuestUser (✅ has this)
└─ No company field (❌ Could be added for audit)
```

### Usage in Models:

```
SalesRoomMedia
├─ uploaded_by_guest → GuestUser (✅ can be NULL)

Comment
├─ created_by_guest → GuestUser (✅ can be NULL)

MutualActionItem
├─ created_by_guest → GuestUser (✅ can be NULL)
├─ guest_assignee → GuestUser (✅ can be NULL)
```

**Assessment:** ✅ **All relationships properly defined**
            ⚠️ **Missing company link at GuestUser level**

---

## Part 7: Recommended Fixes

### Fix #1: Add Company Field to GuestUser

**File:** `apps/authentication/models.py` (GuestUser model)

```python
# ✅ NEW: Company-level scoping
company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='guest_users',
    null=True,
    blank=True
)

class Meta:
    indexes = [
        models.Index(fields=['company', 'created_at'], name='guestuser_company_created_idx'),
    ]

def save(self, *args, **kwargs):
    """Auto-set company from sales_room if not already set."""
    if not self.company and self.sales_room and self.sales_room.company:
        self.company = self.sales_room.company
    super().save(*args, **kwargs)
```

**Impact:** Enables company-scoped queries and audit trails

---

### Fix #2: Update SalesRoomListView with Role-Based Filtering

**File:** `apps/sale_rooms/room_views/user_room.py`

```python
from apps.core.mixins import RoleBasedClientAccessMixin

class SalesRoomListView(LoginRequiredMixin, RoleBasedClientAccessMixin, TemplateView):
    template_name = "sales_rooms/sales_room_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Use mixin to get accessible clients
        accessible_clients = self.get_accessible_clients(user)
        rooms = SalesRoom.objects.filter(client__in=accessible_clients)

        # Rest of filtering...
```

**Impact:** Managers see team's rooms, admins see all

---

### Fix #3: Add Access Check to SalesRoomDetailView

**File:** `apps/sale_rooms/room_views/user_room.py`

```python
def get_sales_room(self, uuid):
    sales_room = get_object_or_404(SalesRoom, uuid=uuid)

    # Verify access
    accessible_clients = self.get_accessible_clients(self.request.user)
    if not accessible_clients.filter(pk=sales_room.client_id).exists():
        messages.error(self.request, "You don't have access to this sales room.")
        raise Http404("Sales room not found or access denied.")

    return sales_room
```

**Impact:** Prevents unauthorized access to rooms

---

### Fix #4: Add Explicit company & created_by to SalesRoomCreateView

**File:** `apps/sale_rooms/room_views/user_room.py`

```python
def form_valid(self, form):
    sales_room = form.save(commit=False)
    sales_room.user = self.request.user
    sales_room.company = self.request.user.company  # ✅ EXPLICIT
    sales_room.created_by = self.request.user       # ✅ EXPLICIT
    sales_room.save()
    messages.success(self.request, 'Sales room created successfully.')
    return redirect('sales_room_detail', uuid=sales_room.uuid)
```

**Impact:** Audit trail and explicit company scoping

---

### Fix #5: Set Company in GuestLoginView

**File:** `apps/sale_rooms/room_views/guest_room.py`

```python
guest_user.name = name
guest_user.sales_room = sales_room
guest_user.company = sales_room.company  # ✅ ADD THIS
guest_user.last_login = timezone.now()
guest_user.visit_count += 1
guest_user.save()
```

**Impact:** Ensures GuestUser has company set immediately

---

## Conclusion

### Current State:
- ✅ **Models:** Excellent company scoping (except GuestUser)
- ⚠️ **Views:** Partial filtering - needs role-based access
- ✅ **URLs:** Clean structure, safe UUID routing
- ✅ **Guest Relations:** Properly connected via FK to SalesRoom
- ⚠️ **Data Integrity:** GuestUser missing company field

### Required Actions:
1. **HIGH:** Add company field to GuestUser model (requires migration)
2. **HIGH:** Apply RoleBasedClientAccessMixin to SalesRoomListView
3. **HIGH:** Add access verification to SalesRoomDetailView
4. **MEDIUM:** Set company & created_by explicitly in SalesRoomCreateView
5. **MEDIUM:** Set company in GuestLoginView

### Risk Assessment:
- 🔴 **RED:** GuestUser can't be filtered by company (data isolation risk)
- 🟠 **ORANGE:** Managers can't see team's sales rooms (workflow broken)
- 🟠 **ORANGE:** created_by not set (audit trail incomplete)
- 🟡 **YELLOW:** No access verification on detail views (should be added)

---

**Status:** AUDIT COMPLETE - Ready for fixes
**Next:** Implement fixes per recommendations above
