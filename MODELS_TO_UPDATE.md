# Models Requiring Company-Scoping Updates

## Summary
After reviewing all models in `apps/sale_rooms/` and `apps/report_management/`, we've identified which models need company-scoping fields added.

---

## 🔴 REQUIRED UPDATES (Critical for multi-tenancy)

### 1. **SalesRoom** (`apps/sale_rooms/models.py`)
**Current State:**
```python
class SalesRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sale_rooms', null=True, blank=True)
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='sales_room')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Issue:** No company field - can't enforce multi-tenancy

**Required Changes:**
```python
# Add fields:
company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='sales_rooms',
    null=True,
    blank=True
)

created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='created_sales_rooms'
)

# Add save() method to auto-populate company from client
def save(self, *args, **kwargs):
    if not self.company and self.client and self.client.company:
        self.company = self.client.company
    if not self.created_by and self.user:
        self.created_by = self.user
    super().save(*args, **kwargs)

# Add index
class Meta:
    indexes = [
        models.Index(fields=['company', 'created_at'], name='salesroom_company_created_idx'),
    ]
```

---

### 2. **ReportFormation** (`apps/report_management/models.py`)
**Current State:**
```python
class ReportFormation(models.Model):
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name="templates")
    transcript = models.ForeignKey(Transcript, on_delete=models.SET_NULL, related_name="reports", null=True, blank=True)
    additional_transcripts = models.ManyToManyField(Transcript, blank=True, related_name="additional_reports")
    status = models.CharField(max_length=20, choices=ReportStatusChoices.choices, default="pending")
    output_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
```

**Issue:** No company field - can't filter by tenant

**Required Changes:**
```python
# Add fields:
company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='report_formations',
    null=True,
    blank=True
)

created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='created_report_formations'
)

# Add save() method to auto-populate company from transcript or user
def save(self, *args, **kwargs):
    if not self.company:
        if self.transcript and self.transcript.company:
            self.company = self.transcript.company
        elif self.client and self.client.company:
            self.company = self.client.company
        elif self.user and self.user.company:
            self.company = self.user.company
    if not self.created_by and self.user:
        self.created_by = self.user
    super().save(*args, **kwargs)

# Add index
class Meta:
    indexes = [
        models.Index(fields=['company', 'created_at'], name='reportformation_company_created_idx'),
        models.Index(fields=['company', 'status'], name='reportformation_company_status_idx'),
    ]
```

---

### 3. **SalesRoomMedia** (`apps/sale_rooms/models.py`)
**Current State:**
```python
class SalesRoomMedia(models.Model):
    sales_room = models.ForeignKey(SalesRoom, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to="salesroom/files/")
    uploaded_by_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    uploaded_by_guest = models.ForeignKey(GuestUser, null=True, blank=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document = models.ForeignKey('report_management.ReportDocument', on_delete=models.CASCADE, related_name='media', blank=True, null=True)
```

**Issue:** No company field - relies on sales_room for tenancy (indirect)

**Required Changes:**
```python
# Add field:
company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='sales_room_media',
    null=True,
    blank=True
)

# Add save() method
def save(self, *args, **kwargs):
    if not self.company:
        if self.sales_room and self.sales_room.company:
            self.company = self.sales_room.company
        elif self.document and self.document.company:
            self.company = self.document.company
    super().save(*args, **kwargs)

# Add index
class Meta:
    indexes = [
        models.Index(fields=['company', 'uploaded_at'], name='salesroommedia_company_uploaded_idx'),
    ]
```

---

### 4. **Comment** (`apps/sale_rooms/models.py`)
**Current State:**
```python
class Comment(models.Model):
    document = models.ForeignKey('report_management.ReportDocument', on_delete=models.CASCADE, related_name='document_comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_by_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_by_guest = models.ForeignKey(GuestUser, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Issue:** No company field - relies on document for tenancy (indirect)

**Required Changes:**
```python
# Add field:
company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='comments',
    null=True,
    blank=True
)

# Add save() method
def save(self, *args, **kwargs):
    if not self.company and self.document and self.document.company:
        self.company = self.document.company
    super().save(*args, **kwargs)

# Add index
class Meta:
    ordering = ['created_at']
    indexes = [
        models.Index(fields=['company', 'document', 'created_at'], name='comment_company_document_created_idx'),
    ]
```

---

### 5. **MutualActionItem** (`apps/sale_rooms/models.py`)
**Current State:**
```python
class MutualActionItem(models.Model):
    sales_room = models.ForeignKey(SalesRoom, on_delete=models.CASCADE, related_name='action_items')
    task_detail = models.TextField(default="")
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TaskStatusChoices.choices, default='todo')
    created_by_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_by_guest = models.ForeignKey(GuestUser, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=6, choices=PriorityChoices.choices, default=PriorityChoices.HIGH)
    guest_assignee = models.ForeignKey(GuestUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='guest_actions')
    admin_assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='admin_actions')
    last_overdue_notification_sent = models.DateTimeField(null=True, blank=True)
    is_notification_sent = models.BooleanField(default=False)
```

**Issue:** No company field - relies on sales_room for tenancy (indirect)

**Required Changes:**
```python
# Add field:
company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='action_items',
    null=True,
    blank=True
)

# Add save() method
def save(self, *args, **kwargs):
    if not self.company and self.sales_room and self.sales_room.company:
        self.company = self.sales_room.company
    super().save(*args, **kwargs)

# Add index
class Meta:
    indexes = [
        models.Index(fields=['company', 'status'], name='actionitem_company_status_idx'),
        models.Index(fields=['company', 'due_date'], name='actionitem_company_due_idx'),
    ]
```

---

## 🟡 INDIRECT UPDATES (Already company-scoped via FK)

These models are indirectly scoped through foreign keys but should still be added to migration for consistency:

### 6. **ClientContact** (`apps/sale_rooms/models.py`)
**Current State:**
```python
class ClientContact(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_contacts', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.TECHNICAL)
    is_active = models.BooleanField(default=True)
    salesforce_id = models.CharField(max_length=255, blank=True, null=True)
    user_account = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
```

**Status:** Indirectly scoped through `Client.company`
**Optional Addition:** Add company FK for direct queries (improves performance)

```python
# Add field (OPTIONAL - improves query performance):
company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='client_contacts',
    null=True,
    blank=True
)

# Add save() method
def save(self, *args, **kwargs):
    if not self.company and self.client and self.client.company:
        self.company = self.client.company
    super().save(*args, **kwargs)
```

---

## 🟢 NO CHANGES NEEDED

### 7. **ReportTemplate** (`apps/report_management/models.py`)
**Status:** GLOBAL/SHARED - No company field needed
- Used across all companies
- Only created by admins
- No multi-tenancy isolation needed

### 8. **Category & SubCategory** (`apps/report_management/models.py`)
**Status:** GLOBAL/SHARED - No company field needed
- Taxonomy for report organization
- Used across all companies
- Shared configuration

### 9. **TranscriptMedia** (`apps/report_management/models.py`)
**Status:** Indirectly scoped through Transcript (which has company)
- No direct company FK needed

---

## 📋 Implementation Priority

### Phase 1 (Critical - Required for multi-tenancy):
1. SalesRoom - add company + created_by
2. ReportFormation - add company + created_by
3. SalesRoomMedia - add company
4. Comment - add company
5. MutualActionItem - add company

### Phase 2 (Optional - Performance optimization):
6. ClientContact - add company (optional)

### Phase 3 (No changes):
7-9. ReportTemplate, Category, SubCategory, TranscriptMedia

---

## Migration Strategy

1. **Create migration file**: `0005_add_company_to_sales_and_reports.py`
2. **Add company fields** (nullable=True, blank=True) to all 5 required models
3. **Add created_by field** to SalesRoom and ReportFormation
4. **Add save() methods** to auto-populate company from related objects
5. **Update management command** to link SalesRoom and ReportFormation to companies:
   ```python
   # Phase 3 Update in init_user_company.py:
   sales_rooms = SalesRoom.objects.filter(user__isnull=False, company__isnull=True)
   for room in sales_rooms:
       room.company = room.user.company
       room.created_by = room.user
       room.save()
   ```

---

## Files to Modify

```
apps/sale_rooms/models.py
├── SalesRoom - ADD company, created_by
├── SalesRoomMedia - ADD company
├── Comment - ADD company
├── MutualActionItem - ADD company
└── ClientContact - ADD company (optional)

apps/report_management/models.py
└── ReportFormation - ADD company, created_by

apps/authentication/management/commands/init_user_company.py
└── Add Phase 3b: Link SalesRoom entities to companies
```

