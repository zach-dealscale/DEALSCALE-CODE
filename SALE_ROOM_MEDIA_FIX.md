# Sales Room Media Architecture Fix

## Current Architecture Analysis

### Current Relationships:
```
ReportDocument
    ├── SalesRoomMedia (FK to ReportDocument, CASCADE) - media gets deleted with document
    └── Comment (FK to ReportDocument, CASCADE) - comments get deleted with document

SalesRoom
    ├── SalesRoomMedia (FK to SalesRoom)
    └── ReportDocument.sales_room (FK to SalesRoom)
```

### Problems Identified:

1. **`SalesRoomMedia.document` uses `CASCADE`** - When ReportDocument is deleted, all linked media files are deleted too (immediate issue)

2. **`Comment` is attached to `ReportDocument`, not `SalesRoomMedia`** - Comments should be on media items shown in the sales room, not on the source document

3. **Hacky workaround in `GuestRoomMediaUploadView`** - Creates a **new ReportDocument for every guest upload** just to have somewhere to attach comments. This causes orphaned documents and cascade deletion problems.

4. **`ReportDocument` is dual-purpose** - It serves both as:
   - An internal document (generated reports)
   - A shareable item in sales rooms

5. **No clear separation between "Report" and "Shared Media"** - A ReportDocument becomes SalesRoomMedia only when shared, but the relationship is confusing

---

## Recommended Architecture Refactor

### Option A: Make `SalesRoomMedia` the primary entity for Sales Room content (RECOMMENDED)

**Concept:** `SalesRoomMedia` becomes the central entity for everything visible in a Sales Room. Comments attach to media, not documents.

```
SalesRoomMedia (primary entity in sales room)
    ├── sales_room (FK to SalesRoom) - required
    ├── source_document (FK to ReportDocument, SET_NULL, optional) - link to original
    ├── file (FileField) - could be the PDF copy or uploaded file
    ├── Comment (FK to SalesRoomMedia) - comments attach HERE
    └── Independent lifecycle from ReportDocument

ReportDocument (internal document)
    ├── No direct relationship to comments
    ├── is_shareble flag triggers COPY to SalesRoomMedia
    └── Deleting ReportDocument doesn't affect shared copy
```

**Flow:**
1. User generates a ReportDocument (internal)
2. User clicks "Share to Sales Room" → Creates a SalesRoomMedia entry with `source_document=ReportDocument`, copies the PDF file
3. Guest uploads a file → Creates SalesRoomMedia with `source_document=None`
4. Comments attach to SalesRoomMedia
5. Deleting ReportDocument: SalesRoomMedia stays (SET_NULL on source_document)

### Option B: Keep current structure but fix relationships (Minimal changes)

**Minimal changes:**

1. Change `SalesRoomMedia.document` from `CASCADE` to `SET_NULL`
2. Change `Comment.document` from `CASCADE` to `SET_NULL`
3. Add `Comment.media` FK to SalesRoomMedia (nullable)
4. Comments can attach to either document OR media
5. Stop creating fake ReportDocuments for guest uploads

---

## Recommendation: Option A

**Why:**
- Clean separation of concerns
- `SalesRoomMedia` = "what guests see in the room"
- `ReportDocument` = "internal document storage"
- No more hacky workarounds
- Comments naturally belong to the shared item, not the source
- Deleting internal documents doesn't break the guest experience

---

## Migration Path for Option A

### Phase 1: Model Changes

1. **Update `SalesRoomMedia` model:**
   ```python
   class SalesRoomMedia(models.Model):
       sales_room = models.ForeignKey(SalesRoom, on_delete=models.CASCADE, related_name='media')
       file = models.FileField(upload_to="salesroom/files/")
       source_document = models.ForeignKey(
           'report_management.ReportDocument',
           on_delete=models.SET_NULL,  # Changed from CASCADE
           related_name='shared_media',
           blank=True,
           null=True
       )
       title = models.CharField(max_length=255, blank=True)  # NEW: Independent title
       # ... other fields remain
   ```

2. **Update `Comment` model:**
   ```python
   class Comment(models.Model):
       # REMOVE or deprecate this:
       # document = models.ForeignKey('report_management.ReportDocument', ...)

       # ADD this:
       media = models.ForeignKey(
           'SalesRoomMedia',
           on_delete=models.CASCADE,
           related_name='comments'
       )
       # ... other fields remain
   ```

### Phase 2: Business Logic Changes

1. **Update share logic (`update_document_share` view):**
   - When `is_shareble=True`: Create/update SalesRoomMedia entry with file copy
   - When `is_shareble=False`: Optionally keep or remove SalesRoomMedia

2. **Update `GuestRoomMediaUploadView`:**
   - Remove the hacky ReportDocument creation
   - Simply create SalesRoomMedia with `source_document=None`

3. **Update comment views:**
   - Attach comments to SalesRoomMedia instead of ReportDocument
   - Update all comment fetch/create logic

### Phase 3: Data Migration

1. Create migration to:
   - Add new fields to SalesRoomMedia
   - Add new `media` FK to Comment
   - Migrate existing comments from document to media (where possible)

2. Clean up orphaned ReportDocuments created by guest uploads

### Phase 4: Template/Frontend Updates

1. Update sales room templates to use SalesRoomMedia.comments
2. Update comment submission endpoints

---

## Files to Modify

### Models:
- `apps/sale_rooms/models.py` - SalesRoomMedia, Comment

### Views:
- `apps/sale_rooms/room_views/guest_room.py` - GuestRoomMediaUploadView
- `apps/report_management/views.py` - share toggle logic
- Comment-related views

### Templates:
- Sales room templates showing comments
- Comment submission forms

---

## Immediate Quick Fix (Before Full Refactor)

If you need to stop the cascade deletion issue immediately:

1. Change `SalesRoomMedia.document` from `CASCADE` to `SET_NULL`
2. Run migration
3. This prevents media deletion when documents are deleted

```python
# In apps/sale_rooms/models.py
document = models.ForeignKey(
    'report_management.ReportDocument',
    on_delete=models.SET_NULL,  # Changed from CASCADE
    related_name='media',
    blank=True,
    null=True
)
```

This is a safe, non-breaking change that can be done immediately while planning the full refactor.
