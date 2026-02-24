# Phase 1: Django Admin Testing Guide

**Objective:** Validate that all models, relationships, and admin interfaces work correctly before Phase 2 (Data Migration)

**Duration:** ~15-20 minutes

---

## 🚀 Pre-Test Setup

```bash
# 1. Start fresh - create new superuser
python manage.py createsuperuser
# Email: test@example.com
# Password: testpass123

# 2. Start dev server
python manage.py runserver

# 3. Access admin
# URL: http://localhost:8000/admin
```

---

## ✅ TEST 1: Company Creation

**Location:** Admin → Companies → Add Company

### Steps:

1. Click **"Add Company"** button
2. Fill in:
   - **Name:** `Test Corp Inc`
   - **Website:** `https://testcorp.com`
   - **Logo:** (optional, skip for now)
   - Leave **is_active** = ✓ (checked)

3. Click **Save**

### Expected Results:

- ✅ Company created with ID like `company-abc123xyz`
- ✅ Page shows: `is_active = True`
- ✅ `created_by` field is empty (we didn't assign it yet)
- ✅ Return to Companies list
- ✅ Company shows in list with `created_at` timestamp

**Screenshot Check:**
- List shows: Name | is_active | created_by | created_at | Active Users
- "Active Users" column should show **0** (no users yet)

---

## ✅ TEST 2: Role Creation (Automatic Defaults)

**Location:** Admin → Roles

### Expected Auto-Created Roles:

When you created the Company, **default roles should NOT auto-create yet** (we handle that in signup flow).
So let's manually create them:

### Steps:

1. Click **"Add Role"** button
2. Fill in **Role 1 (Owner)**:
   - **Company:** `Test Corp Inc` (select from dropdown)
   - **Name:** `Owner`
   - **Level:** `0`
   - **Description:** `Full control of company`
   - ✅ Check: `can_manage_team`
   - ✅ Check: `can_view_all_data`
   - ✅ Check: `can_manage_roles`
   - ✅ Check: `can_manage_clients`
   - Leave other permissions unchecked
   - Click **Save**

3. Click **"Add Role"** button again for **Role 2 (VP/Admin)**:
   - **Company:** `Test Corp Inc`
   - **Name:** `VP/Admin`
   - **Level:** `1`
   - **Description:** `Manager with team visibility`
   - ✅ Check: `can_manage_team`
   - ✅ Check: `can_view_hierarchy_data`
   - ✅ Check: `can_manage_clients`
   - Leave other permissions unchecked
   - Click **Save**

4. Click **"Add Role"** button again for **Role 3 (Sales Rep)**:
   - **Company:** `Test Corp Inc`
   - **Name:** `Sales Rep`
   - **Level:** `2`
   - **Description:** `Individual contributor`
   - ✅ Check: `can_upload_transcripts`
   - ✅ Check: `can_generate_reports`
   - Leave other permissions unchecked
   - Click **Save**

### Expected Results:

- ✅ All 3 roles created with correct IDs (role-xxx)
- ✅ Roles list shows: Name | Company | Level | Permissions | Users Count
- ✅ Users count shows **0** for each role (no users assigned yet)
- ✅ Unique constraint prevents duplicate role names per company

**Verification:** Try to create another "Owner" role for same company → Should show error ✅

---

## ✅ TEST 3: Team Creation

**Location:** Admin → Teams → Add Team

### Steps:

1. Click **"Add Team"** button
2. Fill in **Team 1**:
   - **Company:** `Test Corp Inc`
   - **Name:** `Sales Team Alpha`
   - **Description:** `Enterprise sales division`
   - **lead:** (leave empty for now)
   - **created_by:** (leave empty for now)
   - Click **Save**

3. Click **"Add Team"** button again for **Team 2**:
   - **Company:** `Test Corp Inc`
   - **Name:** `Support Team Beta`
   - **Description:** `Customer support team`
   - Leave other fields empty
   - Click **Save**

### Expected Results:

- ✅ Teams created with IDs like `team-xyz123`
- ✅ Teams list shows: Name | Company | Lead | Members | created_at
- ✅ Members count shows **0** (no members yet)
- ✅ Can't create duplicate team names in same company (unique_together constraint)

---

## ✅ TEST 4: Create First User & Assign to Company

**Location:** Admin → Users → Add User

### Steps:

1. Click **"Add User"** button
2. Fill in:
   - **Email:** `owner@testcorp.com`
   - **Password:** (Django generates a secure one, click the link "generate")
   - Copy the password for later
   - Click **Save and Continue Editing**

3. Now edit the user fields:
   - **First Name:** `John`
   - **Last Name:** `Owner`
   - **Company:** `Test Corp Inc` (select from dropdown)
   - **Role:** `Owner` (select from dropdown)
   - **is_active_in_company:** ✓ (checked)
   - **Manager:** (leave empty - he's the top)
   - **is_active:** ✓ (checked)
   - Click **Save**

### Expected Results:

- ✅ User created with ID like `user-abc123`
- ✅ List now shows:
  - Email | Company | Role | Teams | is_active_in_company | is_staff
  - `owner@testcorp.com | Test Corp Inc | Owner | No teams | ✓ | —`
- ✅ **joined_company_at** auto-filled with current timestamp
- ✅ Users list for Role "Owner" now shows **1**

---

## ✅ TEST 5: Create Additional Users (VP & Sales Rep)

**Location:** Admin → Users → Add User

### Create User 2 (VP):

1. Click **"Add User"**
2. Fill in:
   - **Email:** `vp@testcorp.com`
   - **Password:** (generate)
   - Click **Save and Continue Editing**

3. Edit:
   - **First Name:** `Jane`
   - **Last Name:** `VP`
   - **Company:** `Test Corp Inc`
   - **Role:** `VP/Admin`
   - **Manager:** `John Owner` (select from dropdown)
   - **is_active_in_company:** ✓
   - Click **Save**

### Create User 3 (Sales Rep):

1. Click **"Add User"**
2. Fill in:
   - **Email:** `rep@testcorp.com`
   - **Password:** (generate)
   - Click **Save and Continue Editing**

3. Edit:
   - **First Name:** `Bob`
   - **Last Name:** `Rep`
   - **Company:** `Test Corp Inc`
   - **Role:** `Sales Rep`
   - **Manager:** `Jane VP` (select from dropdown - she manages this rep)
   - **is_active_in_company:** ✓
   - Click **Save**

### Expected Results:

- ✅ 3 users created
- ✅ Users list shows all with correct companies, roles, teams
- ✅ Hierarchy shows: Owner → VP → Sales Rep
- ✅ Hierarchy Level displayed correctly:
  - John Owner: "Level 0"
  - Jane VP: "Level 1"
  - Bob Rep: "Level 2"

---

## ✅ TEST 6: Team Membership (Multiple Teams)

**Location:** Admin → Team Membership → Add Team Membership

### Steps:

1. Click **"Add Team Membership"**
2. Fill in **Membership 1**:
   - **User:** `Jane VP` (vp@testcorp.com)
   - **Team:** `Sales Team Alpha`
   - **role_in_team:** `Team Lead` (optional)
   - **is_active:** ✓ (checked)
   - Click **Save**

3. Click **"Add Team Membership"** again:
   - **User:** `Bob Rep` (rep@testcorp.com)
   - **Team:** `Sales Team Alpha`
   - **role_in_team:** (leave empty)
   - **is_active:** ✓
   - Click **Save**

4. Click **"Add Team Membership"** again:
   - **User:** `Bob Rep` (rep@testcorp.com)
   - **Team:** `Support Team Beta` (add him to second team!)
   - **role_in_team:** (leave empty)
   - **is_active:** ✓
   - Click **Save**

### Expected Results:

- ✅ TeamMembership list shows:
  - User | Team | role_in_team | is_active | joined_at
  - `vp@testcorp.com → Sales Team Alpha | Team Lead | ✓ | timestamp`
  - `rep@testcorp.com → Sales Team Alpha | — | ✓ | timestamp`
  - `rep@testcorp.com → Support Team Beta | — | ✓ | timestamp`

- ✅ User can belong to MULTIPLE teams (Bob is in 2 teams!)

- ✅ Go back to Users → Edit Bob Rep:
  - **Teams** field shows: `2 team(s)` ✓

- ✅ Go to Teams → Edit Sales Team Alpha:
  - **Members** count shows: `2` ✓

---

## ✅ TEST 7: Client Creation (Company-Scoped)

**Location:** Admin → Clients → Add Client

### Steps:

1. Click **"Add Client"**
2. Fill in:
   - **Name:** `Acme Corp`
   - **Company:** `Test Corp Inc` (select from dropdown)
   - **primary_owner:** `Jane VP` (select from dropdown)
   - **created_by:** `John Owner` (select from dropdown)
   - **Website:** `https://acme.com`
   - **company_email:** `contact@acme.com`
   - **industry:** `Technology`
   - **company_size:** `500`
   - **notes:** `Enterprise client`
   - Click **Save**

### Expected Results:

- ✅ Client created
- ✅ Client list shows:
  - Name | Company | primary_owner | industry | created_at
  - `Acme Corp | Test Corp Inc | Jane VP | Technology | timestamp`
- ✅ Document count shows: `0` (no documents yet)
- ✅ Client linked to company, not just single user

---

## ✅ TEST 8: Hierarchy Verification

**Location:** Admin → Users → Select John Owner (the owner)

### Steps:

1. Click on **John Owner** user
2. Scroll to **Hierarchy** section (it's collapsed)
3. Click to expand

### Expected Results:

- ✅ **Manager:** (empty - he's the top)
- ✅ **Hierarchy Level:** `Level 0`
- ✅ Notes say: "John Owner is the top of the org chart"

### Now click on **Jane VP**:

- ✅ **Manager:** `John Owner` ✓
- ✅ **Hierarchy Level:** `Level 1` ✓

### Now click on **Bob Rep**:

- ✅ **Manager:** `Jane VP` ✓
- ✅ **Hierarchy Level:** `Level 2` ✓

---

## ✅ TEST 9: Role Permissions Verification

**Location:** Admin → Roles → Select Owner

### Steps:

1. Click on **Owner** role
2. Check **Permissions** section

### Expected Results:

- ✅ Owner permissions:
  - ✓ can_manage_team
  - ✓ can_view_all_data
  - ✓ can_manage_roles
  - ✓ can_manage_clients
  - ✓ can_upload_transcripts
  - ✓ can_generate_reports

### Repeat for **VP/Admin** role:

- ✅ VP permissions:
  - ✓ can_manage_team
  - ✓ can_view_hierarchy_data
  - ✓ can_manage_clients
  - ✓ can_upload_transcripts
  - ✓ can_generate_reports
  - ❌ can_view_all_data (NO - only hierarchy data)

### Repeat for **Sales Rep** role:

- ✅ Sales Rep permissions:
  - ✓ can_upload_transcripts
  - ✓ can_generate_reports
  - ❌ Everything else (NO)

---

## ✅ TEST 10: Soft Delete (Team Membership)

**Location:** Admin → Team Membership

### Steps:

1. Find the membership: `rep@testcorp.com → Support Team Beta`
2. Click to edit
3. Uncheck **is_active** ✓ → unchecked
4. Click **Save**

### Expected Results:

- ✅ Membership still exists in database (not deleted)
- ✅ List now shows `is_active = ✗` (unchecked) ✓
- ✅ Go to Users → Bob Rep → **Teams** field now shows: `1 team(s)` (was 2, now 1)
- ✅ Go to Teams → Support Team Beta → **Members** count now shows: `0` (was 1, now 0)

**This is soft delete in action!** ✅

---

## ✅ TEST 11: Search & Filter Tests

### Search in Users Admin:

1. Go to **Admin → Users**
2. Search box: type `test`
3. Should find: `owner@testcorp.com`, `vp@testcorp.com`, `rep@testcorp.com`

### Filter Users by Company:

1. Go to **Admin → Users**
2. **Filters** on right: Click **Company**
3. Select `Test Corp Inc`
4. Should show all 3 users ✓

### Filter Users by Role:

1. **Filters** → Click **Role**
2. Select `Owner`
3. Should show only `John Owner` ✓

### Filter TeamMembership by Team:

1. Go to **Admin → Team Membership**
2. **Filters** → Click **Team**
3. Select `Sales Team Alpha`
4. Should show: Jane VP (Lead) and Bob Rep ✓

---

## 📊 Summary Table (After All Tests)

| Entity | Count | Notes |
|--------|-------|-------|
| Companies | 1 | Test Corp Inc |
| Roles | 3 | Owner, VP/Admin, Sales Rep |
| Teams | 2 | Sales Team Alpha, Support Team Beta |
| Users | 3 | John (Owner), Jane (VP), Bob (Rep) |
| TeamMemberships | 2 | Jane→Sales, Bob→Sales (active), Bob→Support (inactive) |
| Clients | 1 | Acme Corp (company-scoped) |
| Hierarchy Depth | 3 | Level 0 → 1 → 2 |

---

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Admin page won't load | Check `python manage.py check` for errors |
| Can't select User in dropdown | Make sure user exists first (create in Users admin first) |
| Hierarchy Level shows "Error" | Likely circular reference; check manager assignments |
| TeamMembership unique constraint error | Can't add same user to same team twice; edit existing instead |
| Teams count doesn't match | Check `is_active` flag on TeamMembership |

---

## ✅ Final Verification Checklist

Before saying **"Phase 1 Complete"**, verify:

- [ ] 1 Company created
- [ ] 3 Roles created with correct permissions
- [ ] 2 Teams created
- [ ] 3 Users created with hierarchy (Owner > VP > Rep)
- [ ] 2 Active TeamMemberships
- [ ] 1 Inactive TeamMembership (soft-delete test)
- [ ] 1 Client linked to company
- [ ] All searches work
- [ ] All filters work
- [ ] Hierarchy levels display correctly
- [ ] Role permissions saved correctly
- [ ] Team member count updates when membership changes
- [ ] User team count updates when membership changes
- [ ] No errors in browser console
- [ ] No errors in Django logs

---

## 🚀 Once All Tests Pass:

Run this to confirm no errors:

```bash
python manage.py check
```

Then we move to **Phase 2: Data Migration** ✅

---

**Estimated Time:** 15-20 minutes
**Difficulty:** Easy
**Prerequisites:** Running Django dev server with superuser

Good luck! 🎉
