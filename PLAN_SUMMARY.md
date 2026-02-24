# 📋 Implementation Plan Summary: Multi-Tenant + Team Hierarchy

## 🎯 Vision

Transform DealScale from a **single-user platform** to a **multi-tenant, team-based enterprise platform** where:

- **Company/Workspace** is the top-level organizational unit (tenant)
- **Users belong to Companies** and can share data with teammates
- **Hierarchy** is supported (users can manage other users)
- **Roles** control visibility and permissions (Owner → VP → Sales Rep)
- **Teams** group users by function (Sales, Support, Onboarding)
- **ALL data** (Transcripts, Reports, Documents, Clients) is company-scoped

---

## 🏗️ Core Architecture Change

### Before (Current State)
```
User (email, profile_picture, role)
├── Client (customer of user)
│   └── Transcript
│       └── Reports
└── SalesRoom
```

**Problem:** Only one user can own a client. No team collaboration. No company concept.

### After (Multi-Tenant Design)
```
Company (Tenant, Workspace)
├── Users (multiple, with hierarchy)
│   ├── Role (Owner, VP, Sales Rep)
│   ├── Team (Sales, Support, etc.)
│   └── Manager (who they report to)
├── Clients (company's customers)
│   └── Primary Owner (one user)
├── Transcripts (uploaded by users)
│   └── created_by + company
└── Reports
    ├── created_by + company
    └── accessible by: owner, manager, self
```

**Benefit:** Full team collaboration with hierarchical access control.

---

## 📊 New Models (7 total)

| Model | Purpose | Key Fields |
|-------|---------|-----------|
| **Company** | Tenant/Workspace | name, slug, created_by, subscription_tier |
| **Role** | Permission level per company | name, level, can_view_all_data, can_manage_team |
| **Team** | User group within company | company, name, lead |
| **CustomUser** (extended) | Platform user | company, role, team, manager, is_active_in_company |
| **Client** (extended) | Customer of company | company, primary_owner, created_by |
| **Transcript** (extended) | Meeting recording/upload | company, uploaded_by |
| **ReportDocument** (extended) | Generated report | company, created_by |

---

## 🔄 4-Phase Implementation (Zero Downtime)

### Phase 1: Create Models (Week 1)
- Add Company, Role, Team models
- Extend User, Client, Transcript, ReportDocument with **nullable** company fields
- ✅ **NO existing features break** (all fields optional)
- ✅ **NO data loss** (no deletions, only additions)

**Outcome:** New models exist but aren't used yet.

---

### Phase 2: Migrate Existing Data (Week 2)
- Run management command: `migrate_users_to_companies`
- For each existing User → Create a new Company
- Each User becomes "Owner" of their company
- Each Client → linked to its user's company
- Each Transcript → linked to company
- ✅ **Idempotent** (safe to run multiple times)
- ✅ **Dry-run first** to verify

**Outcome:** All existing data now has a company assigned.

---

### Phase 3: Scope All Queries (Weeks 3-4)
- Create `CompanyQuerySet` and `CompanyManager` mixins
- Update all views to filter by company
- Add hierarchy-aware visibility filtering
- Implement DataVisibilityFilter class
- Test all views with different roles

**Outcome:** All queries respect company isolation and role-based visibility.

---

### Phase 4: Make Fields Required (Week 5)
- Change `company` field from `null=True` to `null=False`
- Add database constraints
- Full multi-tenancy enforcement

**Outcome:** Company is mandatory everywhere.

---

## 🔐 Visibility Rules (Permission Logic)

### Owner (Level 0)
✅ Sees all company data
✅ Can manage users, roles, teams
✅ Can view dashboards with company-wide metrics

### VP/Admin (Level 1)
✅ Sees own data + all subordinates' data (recursive)
✅ Can manage their team members
❌ Cannot see other teams' data

### Sales Rep (Level 2)
✅ Sees only own data
❌ Cannot see team members' data

### Hierarchy Example
```
Owner (can see everything)
├── VP Sales (can see VP + 3 reps below)
│   ├── Rep 1 (can see only own)
│   ├── Rep 2 (can see only own)
│   └── Rep 3 (can see only own)
└── VP Support (can see VP + 2 reps below)
    ├── Rep 4 (can see only own)
    └── Rep 5 (can see only own)
```

---

## 💾 Data Migration Strategy

### Safe, Auditable, Reversible

```bash
# Step 1: Dry run (no changes)
python manage.py migrate_users_to_companies --dry-run
# Output: "Would create 150 companies, migrate 150 users"

# Step 2: Verify output
cat audit_migration_report.json

# Step 3: Run for real
python manage.py migrate_users_to_companies
# Output: "Created 150 companies, migrated 150 users"

# Step 4: Verify in Django admin
```

**Safety Measures:**
- ✅ All existing data preserved
- ✅ Dry-run mode to verify
- ✅ Audit log generated
- ✅ Idempotent (safe to run multiple times)
- ✅ Rollback possible (reverse migrations)

---

## 🧪 Quality Assurance Plan

### Unit Tests
- Hierarchy methods (get_subordinates, is_manager_of)
- Permission checks (can_view_user_data)
- Role creation (create_default_roles)

### Integration Tests
- Transcript visibility by role
- Report visibility by hierarchy
- Client scoping by company

### Multi-Tenancy Tests
- Complete isolation between companies
- No data leakage
- Permission enforcement

### Performance Tests
- Query optimization
- Index effectiveness
- Load test (1000+ users)

---

## ⚠️ Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Data loss | Backup before Phase 2, dry-run test, audit log |
| Query slowdown | Add indexes, profile queries, load test |
| Company isolation breach | Security audit, comprehensive tests, code review |
| Breaking existing features | Keep old fields nullable, gradual rollout |
| User confusion | Documentation, training videos, clear UI |

---

## ✨ Key Design Decisions

1. ✅ **Company (not User) is top-level unit** → Team collaboration
2. ✅ **Nullable fields in Phase 1** → Zero downtime
3. ✅ **Prefixed UUIDs** (company-{uuid}) → Consistency
4. ✅ **Role permission flags** → Fast lookups (no N+1)
5. ✅ **Self-referential manager field** → Flexible hierarchy
6. ✅ **QuerySet mixin pattern** → DRY, testable
7. ✅ **DataVisibilityFilter class** → Centralized permission logic
8. ✅ **Phase-based rollout** → Risk reduction

---

## 🚀 Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|-----------------|
| 1: Models | Week 1 | Company, Role, Team models; migrations |
| 2: Data Migration | Week 2 | Management command; all data migrated |
| 3: Query Scoping | Weeks 3-4 | All views company-scoped; hierarchy filtering |
| 4: Admin & UI | Week 5 | Admin panel; user management UI |
| 5: Testing | Weeks 6-7 | Full test suite; security audit |
| 6: Production | Week 8 | Deployment; monitoring; success metrics |

**Total: 8 weeks from start to production**

---

## 📈 Success Metrics

- ✅ All existing functionality works unchanged
- ✅ Zero data loss
- ✅ 100% test coverage (unit + integration)
- ✅ Multi-tenancy enforced (no data leakage)
- ✅ Hierarchy visibility working correctly
- ✅ Performance metrics stable or improved
- ✅ Zero production incidents
- ✅ User adoption (teams actively using feature)

---

## 🔮 Future Expansions (After MVP)

### Phase 3+ Features
- **Company Invitations:** Owner can invite users by email
- **Custom Roles:** Owner creates custom roles (not just default)
- **Fine-grained Permissions:** django-guardian for per-model control
- **Subdomain Routing:** acme.transcripts.io
- **Advanced Analytics:** Revenue by team, win rate by VP

### Phase 4+ Features
- **Billing & Subscription:** Per-company SaaS model
- **SSO Integration:** SAML/OIDC for enterprise
- **Company Switching:** Superuser/admin can switch companies
- **Audit Logging:** Complete activity trail per company

---

## 📚 Documentation Files Created

1. **`IMPLEMENTATION_PLAN.md`** (This detailed guide)
   - 500+ lines
   - Complete model definitions
   - Phase-by-phase breakdown
   - Test strategies
   - Risk assessment

2. **`CLAUDE.md`** (For Claude Code agents)
   - Project overview
   - Tech stack
   - Common commands
   - Architecture patterns

3. **`new_feature.txt`** (Original request)
   - Team hierarchy requirements
   - Signup flow
   - Visibility rules

---

## ✅ Next Steps

### Immediate (This Week)
1. ✅ Review IMPLEMENTATION_PLAN.md
2. ✅ Validate model design with team
3. ✅ Identify any missing use cases
4. ✅ Get approval to proceed

### Week 1-2 (Start Implementation)
1. Create models in Phase 1
2. Write and test migrations on local
3. Deploy to staging
4. Verify with team

### Week 2-3 (Data Migration)
1. Prepare production backup
2. Run dry-run on production
3. Review audit log
4. Execute real migration
5. Verify data integrity

### Week 3-4 (Query Scoping)
1. Create QuerySet mixins
2. Update views gradually
3. Add hierarchy filtering
4. Comprehensive testing

---

## 💡 Key Insights

### Why This Design Works

1. **Backward Compatible** → No breaking changes during rollout
2. **Phased Rollout** → Can stop/pause at any phase
3. **Testable** → Each phase has clear test criteria
4. **Scalable** → Designed for 1000+ companies, 100k+ users
5. **Flexible** → Easy to add custom roles, teams, permissions later
6. **Secure** → Company isolation enforced at database level
7. **Auditable** → All migrations logged, created_by tracked
8. **Professional** → Enterprise-grade multi-tenancy

### Why NOT Just Add Company to All Models?

❌ **Bad Approach:** Just add `company_id` to every model
- Breaks existing views
- Requires updating 50+ queries
- Risk of data leakage if query is missed
- Hard to test isolation

✅ **This Approach:** Phase-by-phase
- Phase 1: Safe addition (nothing breaks)
- Phase 2: Data migration (auditable)
- Phase 3: Scope queries (testable)
- Phase 4: Enforce (foolproof)

---

## 🎯 Final Notes

This plan ensures:
- **No existing functionality breaks** during implementation
- **All data is safely migrated** with audit trail
- **Progressive rollout** reduces risk
- **Comprehensive testing** before production
- **Easy to add more features** later (custom roles, permissions, etc.)
- **Professional multi-tenancy** design from day one

The design is intentionally **flexible and restriction-free now** but **ready for restrictions later** (Phase 3+).

---

**Status:** ✅ Ready for Implementation
**Complexity:** Medium (4 phases, 8 weeks, ~2000 lines of code)
**Risk Level:** Low (phased, tested, reversible)
**Impact:** High (enables team collaboration, enterprise features)

