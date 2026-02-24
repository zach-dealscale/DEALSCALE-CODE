# Management Command: init_user_company

## Overview

This management command migrates all existing users to the new multi-tenant company-based system. It creates companies for users who don't have one, automatically assigns them as owners, and links all their associated data.

## Execution Flow

### Phase 1: Create Companies for Users
```
For each user without a company:
  1. Create a new Company (named from user's email)
  2. Signal auto-creates "Owner" role with full permissions
  3. Assign user to company as Owner
  4. Set is_active_in_company = True
  5. Set joined_company_at = now()
```

### Phase 2: Link Clients to Companies
```
For all clients where user exists:
  1. Find user's company (guaranteed to exist from Phase 1)
  2. Set client.company = user.company
  3. Set created_by = client.user (original owner)
  4. Set primary_owner = client.user (if not already set)
```

### Phase 3: Link Other Entities
```
For all transcripts where user exists:
  1. Set transcript.company = user.company
  2. Set uploaded_by = user
  3. If transcript has client without company, link client too

For all reports where user exists:
  1. Set report.company = user.company
  2. Set created_by = user
  3. If report has client without company, link client too
```

## Usage

### Run for all users without companies:
```bash
python manage.py init_user_company
```

### Run for specific user:
```bash
python manage.py init_user_company --email user@example.com
```

### Test without making changes (dry-run):
```bash
python manage.py init_user_company --dry-run
```

### Verbose output (detailed progress):
```bash
python manage.py init_user_company --verbose
```

### Combine options:
```bash
python manage.py init_user_company --email user@example.com --dry-run --verbose
```

## Sample Output

```
============================================================
PHASE 1: CREATE COMPANIES FOR USERS
============================================================
Found 3 users without companies

  Processing user1@example.com...
    Creating company: user1's Company
    ✓ Created company & assigned owner
✓ user1@example.com

  Processing user2@example.com...
    Creating company: user2's Company
    ✓ Created company & assigned owner
✓ user2@example.com

  Processing user3@example.com...
    Creating company: user3's Company
    ✓ Created company & assigned owner
✓ user3@example.com

============================================================
PHASE 2: LINK CLIENTS TO COMPANIES
============================================================
  Found 5 clients to link
    ✓ Linked Client A to user1@example.com's company
    ✓ Linked Client B to user1@example.com's company
    ✓ Linked Client C to user2@example.com's company
    ✓ Linked Client D to user2@example.com's company
    ✓ Linked Client E to user3@example.com's company
  ✓ Linked 5 clients

============================================================
PHASE 3: LINK OTHER ENTITIES
============================================================
  Found 10 transcripts to link
    ✓ Linked transcript Transcript No. 1
    ✓ Linked transcript Transcript No. 2
    ... (8 more)
  ✓ Linked 10 transcripts

  Found 7 reports to link
    ✓ Linked report Sales Report
    ✓ Linked report Competitive Brief
    ... (5 more)
  ✓ Linked 7 reports

============================================================
SUMMARY
============================================================
✓ Users initialized: 3
✓ Clients linked: 5
✓ Transcripts linked: 10
✓ Reports linked: 7
```

## Key Features

✅ **Three-Phase Approach**: Users first, then clients, then other entities
- Ensures every user has a company before data linking
- Prevents foreign key constraint violations

✅ **Automatic Role Creation**: Signal auto-creates "Owner" role
- Every company gets an Owner role with full permissions
- User is assigned as Owner

✅ **Dry-Run Mode**: Test without committing changes
- `--dry-run` flag shows what would happen
- Useful for validation before running on production

✅ **Verbose Output**: Detailed progress tracking
- See exactly what's being linked
- Useful for debugging

✅ **Error Handling**: Continues on individual item failures
- Logs errors but processes remaining items
- Shows error summary at end

✅ **Atomic Transactions**: Each phase completes fully or rolls back
- Data consistency guaranteed
- No partial migrations

## What Gets Linked

**Phase 1 (User Companies):**
- User.company → New Company
- User.role → Owner role
- User.is_active_in_company → True
- User.joined_company_at → Now

**Phase 2 (Clients):**
- Client.company → User's company
- Client.created_by → User
- Client.primary_owner → User (if not set)

**Phase 3 (Entities):**
- Transcript.company → User's company
- Transcript.uploaded_by → User
- ReportDocument.company → User's company
- ReportDocument.created_by → User
- Related clients auto-linked if needed

## Behavior After Migration

After running this command:

1. **Every user** has a company assigned
2. **Every user** is an Owner of their company
3. **All legacy data** (clients, transcripts, reports) is company-scoped
4. **Data isolation** is enforced at the database level
5. **Permissions** are ready to implement based on role membership

## Rollback (if needed)

If you need to undo:

```bash
# Reset users
UPDATE authentication_customuser SET company_id = NULL, role_id = NULL WHERE is_active_in_company = True;

# Reset clients
UPDATE authentication_client SET company_id = NULL WHERE company_id IS NOT NULL;

# Reset transcripts
UPDATE report_management_transcript SET company_id = NULL WHERE company_id IS NOT NULL;

# Reset reports
UPDATE report_management_reportdocument SET company_id = NULL WHERE company_id IS NOT NULL;
```

Then delete the created companies:
```bash
DELETE FROM authentication_company WHERE created_by_id IS NOT NULL;
```

## Notes

- Command only processes users `WHERE company IS NULL` (unless specific email given)
- If user already has a company, they are skipped (not processed)
- Clients/transcripts/reports are linked based on their `user` field
- If a user field is NULL, the item is skipped
- The command is idempotent - running twice won't cause duplicates

