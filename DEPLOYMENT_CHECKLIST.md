# Phase 1 Deployment Checklist

## Pre-Deployment Verification

### Code Review
- [ ] Review all 12 model changes in `apps/authentication/models.py`
- [ ] Review all 5 model changes in `apps/sale_rooms/models.py`
- [ ] Review ReportFormation changes in `apps/report_management/models.py`
- [ ] Review admin registrations in `apps/authentication/admin.py`
- [ ] Review signal handlers in `apps/authentication/signals.py`
- [ ] Review management command in `apps/authentication/management/commands/init_user_company.py`

### Syntax & Validation
- [ ] Run `python manage.py check` - should show no errors
- [ ] Run `python manage.py makemigrations apps.sale_rooms apps.report_management` - should create new migrations
- [ ] Review generated migration files for correctness

### Dependencies
- [ ] All required imports present (Company, Role, Team, TeamMembership)
- [ ] No circular imports between authentication, sale_rooms, report_management
- [ ] Signal handlers properly connected via `apps.py`

---

## Database Migration Steps

### Step 1: Create Migrations (if not already created)
```bash
# Create migrations for sale_rooms and report_management models
python manage.py makemigrations apps.sale_rooms apps.report_management

# Review the generated files:
ls -la apps/sale_rooms/migrations/
ls -la apps/report_management/migrations/
```

**Expected Output:**
- New migration file with company FK additions
- No conflicts with existing migrations
- All model changes included

### Step 2: Dry Run Migration
```bash
# Test migrations without applying (if supported by your DB)
python manage.py migrate --plan apps.sale_rooms apps.report_management

# Should show the migration operations that will be performed
```

### Step 3: Apply Migrations
```bash
# Apply migrations to database
python manage.py migrate apps.sale_rooms apps.report_management

# Should complete without errors
```

**Expected Output:**
- "Running migrations... OK"
- All migrations applied successfully
- Database schema updated with company FKs

### Step 4: Verify Migration Status
```bash
# Check that all migrations are applied
python manage.py showmigrations apps.sale_rooms apps.report_management

# All migrations should have [X] mark (applied)
```

---

## Data Migration Steps

### Step 1: Test with Dry Run
```bash
# Test the command without making changes
python manage.py init_user_company --dry-run --verbose

# Should show what WOULD happen
```

**Expected Output:**
```
============================================================
PHASE 1: CREATE COMPANIES FOR USERS
============================================================
Found 1 users without companies

  Processing maazadmin@gmail.com...
    Creating company: maazadmin's Company
    Assigning maazadmin@gmail.com as Owner...
    Linking 1 transcripts...
  [DRY RUN] No changes committed
✓ maazadmin@gmail.com

============================================================
SUMMARY
============================================================
✓ Users initialized: 1
[DRY RUN] Skipping phases 2-4
```

### Step 2: Run Actual Migration
```bash
# Run the full migration command
python manage.py init_user_company --verbose

# Should link all users, clients, transcripts, reports, and sales rooms
```

**Expected Output:**
```
============================================================
PHASE 1: CREATE COMPANIES FOR USERS
============================================================
✓ User initialized: N

============================================================
PHASE 2: LINK CLIENTS TO COMPANIES
============================================================
✓ Clients linked: M

============================================================
PHASE 3: LINK REPORT & TRANSCRIPT ENTITIES
============================================================
✓ Transcripts linked: X
✓ Reports linked: Y
✓ Report Formations linked: Z

============================================================
PHASE 4: LINK SALES ROOM ENTITIES
============================================================
✓ Sales Rooms linked: W

============================================================
SUMMARY
============================================================
✓ Users initialized: N
✓ Clients linked: M
✓ Transcripts linked: X
✓ Reports linked: Y
✓ Report Formations linked: Z
✓ Sales Rooms linked: W
```

### Step 3: Verify Data Integrity
```bash
# Check that all users have companies
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(company__isnull=True).count()
# Should return 0

# Check that Owner roles were created
>>> from apps.authentication.models import Role
>>> Role.objects.filter(name='Owner').count()
# Should equal number of companies

# Check that clients are linked
>>> from apps.authentication.models import Client
>>> Client.objects.filter(company__isnull=True).count()
# Should return 0

# Check that transcripts are linked
>>> from apps.report_management.models import Transcript
>>> Transcript.objects.filter(company__isnull=True).count()
# Should return 0

# Exit shell
>>> exit()
```

---

## Admin Interface Testing

### Step 1: Access Admin
```bash
# Navigate to http://localhost:8000/admin
# Login with your superuser account
```

### Step 2: Test Company Admin
- [ ] Click "Companies" in sidebar
- [ ] Verify all companies listed
- [ ] Click on a company to edit
- [ ] Verify fields: name, website, logo, created_by, is_active
- [ ] Verify created_at and updated_at are read-only
- [ ] Try to delete a company - should be prevented

### Step 3: Test Role Admin
- [ ] Click "Roles" in sidebar
- [ ] Verify all roles listed with company and level
- [ ] Click on a role to edit
- [ ] Verify all permission checkboxes visible
- [ ] Click on "Owner" role - verify all permissions checked

### Step 4: Test Team Admin
- [ ] Click "Teams" in sidebar
- [ ] Verify all teams listed with member count
- [ ] Click on a team to edit
- [ ] Verify member count is read-only

### Step 5: Test TeamMembership Admin
- [ ] Click "Team Memberships" in sidebar
- [ ] Verify memberships listed with user, team, role, is_active, joined_at
- [ ] Click on a membership to edit
- [ ] Verify can change is_active (soft delete)
- [ ] Verify joined_at is read-only

### Step 6: Test CustomUser Admin
- [ ] Click "Custom Users" in sidebar
- [ ] Verify all users listed with company and role
- [ ] Click on a user to edit
- [ ] Verify company field now shows assigned company
- [ ] Verify role field now shows assigned role
- [ ] Verify hierarchy_level displays correctly

### Step 7: Test Client Admin
- [ ] Click "Clients" in sidebar
- [ ] Verify all clients listed with company
- [ ] Click on a client to edit
- [ ] Verify company, primary_owner, created_by fields present

### Step 8: Test Filters & Search
- [ ] Filter Users by Company - should show users for that company
- [ ] Filter Users by Role - should show users with that role
- [ ] Filter TeamMembership by Team - should show members of team
- [ ] Search Users by email - should find users
- [ ] Search Clients by name - should find clients

---

## Validation Tests

### Test 1: Signal Handler
```bash
python manage.py shell

# Create a new company
from apps.authentication.models import Company, Role
c = Company.objects.create(name="Test Signal Company")
c.save()

# Check if Owner role was auto-created
owner = Role.objects.filter(company=c, name='Owner')
print(f"Owner role created: {owner.exists()}")
# Should print: True

exit()
```

### Test 2: Auto-Population
```bash
python manage.py shell

from apps.authentication.models import Client, CustomUser, Company
from apps.report_management.models import Transcript

# Get a user with a company
user = CustomUser.objects.filter(company__isnull=False).first()
company = user.company

# Create a client for this user
client = Client(name="Test Client", user=user)
client.save()

# Check if company was auto-set
print(f"Client company auto-set: {client.company == company}")
# Should print: True

# Create a transcript
transcript = Transcript(user=user, title="Test Transcript")
transcript.save()

print(f"Transcript company auto-set: {transcript.company == company}")
# Should print: True

exit()
```

### Test 3: Hierarchy Methods
```bash
python manage.py shell

from apps.authentication.models import CustomUser

# Get a user with a manager
user = CustomUser.objects.filter(manager__isnull=False).first()
if user:
    # Test hierarchy methods
    print(f"Manager: {user.manager}")
    print(f"Hierarchy Level: {user.get_hierarchy_level()}")
    print(f"Subordinates: {user.get_subordinates()}")
    print(f"Is in company: {user.is_active_in_company}")
else:
    print("No users with managers found")

exit()
```

### Test 4: Team Methods
```bash
python manage.py shell

from apps.authentication.models import CustomUser

# Get a user
user = CustomUser.objects.first()

# Test team methods
print(f"Teams: {user.get_teams()}")
print(f"Team count: {user.get_team_count()}")

# Add user to a team (if team exists)
from apps.authentication.models import Team
team = Team.objects.filter(company=user.company).first()
if team:
    user.add_to_team(team, "Member")
    print(f"Is in team: {user.is_in_team(team)}")

exit()
```

---

## Performance Testing

### Query Optimization Test
```bash
python manage.py shell

from django.db import connection
from django.db import reset_queries
from django.conf import settings

# Enable query debugging
settings.DEBUG = True
reset_queries()

# Test query: Get users with their companies and roles
from apps.authentication.models import CustomUser
users = CustomUser.objects.select_related('company', 'role').all()[:10]

for user in users:
    print(f"{user.email}: {user.company.name if user.company else 'No Company'}")

# Check query count
print(f"\nTotal queries: {len(connection.queries)}")
# Should be low (around 1-2 for select_related)

exit()
```

### Cache Test
```bash
python manage.py shell

from apps.authentication.models import CustomUser
from django.core.cache import cache

# Clear cache
cache.clear()

# Get a user with subordinates
user = CustomUser.objects.filter(subordinates__isnull=False).first()

if user:
    # First call - should hit database
    subs1 = user.get_subordinate_ids()

    # Second call - should hit cache
    subs2 = user.get_subordinate_ids()

    # Check if cache key exists
    from django.core.cache import cache
    cache_key = f"user_subordinates_{user.id}"
    print(f"Cache hit: {cache.get(cache_key) is not None}")
    # Should print: True

exit()
```

---

## Post-Deployment Verification

### Step 1: Check System Health
```bash
python manage.py check
# Should show: System check identified no issues (0 silenced)
```

### Step 2: Verify All Models
```bash
python manage.py shell

from apps.authentication.models import Company, Role, Team, TeamMembership, CustomUser, Client
from apps.sale_rooms.models import SalesRoom, SalesRoomMedia, Comment, MutualActionItem, ClientContact
from apps.report_management.models import ReportFormation

print("✓ Company:", Company.objects.count())
print("✓ Role:", Role.objects.count())
print("✓ Team:", Team.objects.count())
print("✓ TeamMembership:", TeamMembership.objects.count())
print("✓ CustomUser:", CustomUser.objects.count())
print("✓ Client:", Client.objects.count())
print("✓ SalesRoom:", SalesRoom.objects.count())
print("✓ SalesRoomMedia:", SalesRoomMedia.objects.count())
print("✓ Comment:", Comment.objects.count())
print("✓ MutualActionItem:", MutualActionItem.objects.count())
print("✓ ClientContact:", ClientContact.objects.count())
print("✓ ReportFormation:", ReportFormation.objects.count())

exit()
```

### Step 3: Verify No Null Companies (after migration)
```bash
python manage.py shell

from apps.authentication.models import CustomUser, Client
from apps.report_management.models import Transcript, ReportDocument, ReportFormation
from apps.sale_rooms.models import SalesRoom

# Check for null companies (should be 0 after migration)
print(f"Users without company: {CustomUser.objects.filter(company__isnull=True).count()}")
print(f"Clients without company: {Client.objects.filter(company__isnull=True).count()}")
print(f"Transcripts without company: {Transcript.objects.filter(company__isnull=True).count()}")
print(f"ReportDocuments without company: {ReportDocument.objects.filter(company__isnull=True).count()}")
print(f"ReportFormations without company: {ReportFormation.objects.filter(company__isnull=True).count()}")
print(f"SalesRooms without company: {SalesRoom.objects.filter(company__isnull=True).count()}")

# All should be 0 after successful migration
exit()
```

### Step 4: Backup Checkpoint
```bash
# After all tests pass, create a database backup
# (Command depends on your database)

# PostgreSQL:
pg_dump database_name > backup_phase1_$(date +%Y%m%d_%H%M%S).sql

# SQLite:
cp db.sqlite3 db.sqlite3.backup_phase1_$(date +%Y%m%d_%H%M%S)
```

---

## Rollback Plan (If Needed)

### Quick Rollback via Migrations
```bash
# If migrations haven't been pushed to production yet
python manage.py migrate apps.sale_rooms <previous_migration_number>
python manage.py migrate apps.report_management <previous_migration_number>
python manage.py migrate apps.authentication <previous_migration_number>

# Delete the created companies (if you want to reset data)
python manage.py shell
from apps.authentication.models import Company
Company.objects.filter(created_at__gte='2025-11-04').delete()
exit()
```

### Manual Rollback (SQL)
```sql
-- Reset users (if needed)
UPDATE authentication_customuser
SET company_id = NULL, role_id = NULL, is_active_in_company = True;

-- Reset clients
UPDATE authentication_client
SET company_id = NULL;

-- Reset transcripts
UPDATE report_management_transcript
SET company_id = NULL;

-- Reset reports
UPDATE report_management_reportdocument
SET company_id = NULL;

-- Reset sales rooms
UPDATE sale_rooms_salesroom
SET company_id = NULL;

-- Delete companies
DELETE FROM authentication_company
WHERE created_at >= '2025-11-04';
```

---

## Sign-Off Checklist

- [ ] All code reviewed and approved
- [ ] Migrations created and tested
- [ ] Data migration tested with dry-run
- [ ] Data migration completed successfully
- [ ] Admin interface fully functional
- [ ] All admin tests pass (11 test cases)
- [ ] Signal handlers working correctly
- [ ] Auto-population logic verified
- [ ] Hierarchy methods tested
- [ ] Team methods tested
- [ ] No null companies in system (after migration)
- [ ] Query performance optimized
- [ ] Cache working correctly
- [ ] System health check passes
- [ ] Backup created
- [ ] Team notified of changes
- [ ] Documentation updated in Wiki/Docs
- [ ] Monitoring alerts configured
- [ ] Runbook updated for ops team

---

## Contacts & Support

**Implementation Lead:** Claude Code
**QA Lead:** [Your Name]
**DevOps Lead:** [Your Name]
**Stakeholder:** [Your Name]

---

**Status:** Ready for Deployment ✅

