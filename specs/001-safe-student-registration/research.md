# Research & Decisions

## 1. Soft Delete Pattern Implementation

**Decision**: Implement an abstract `SoftDeleteModel` utilizing a custom Django `models.Manager` as the default manager (`objects`) which automatically filters out deleted resources (`is_deleted=False`). A secondary manager (`all_objects`) will be preserved to fetch deleted objects for administrative logs.

**Rationale**: By making this abstract and attaching a custom manager, all extending models (Student, Teacher, etc.) will transparently exclude soft-deleted records from standard QuerySets. This satisfies the Constitution's DRY principle and Data Integrity mandate without writing custom query logic everywhere.

**Alternatives considered**: 
- Shadow tables/archives (moves data physically, breaks foreign keys).
- DB triggers (hides logic from Django ORM, causing mismatches).

## 2. Model `delete()` Override

**Decision**: Override the `.delete()` method of `SoftDeleteModel` (and any related user extensions) to set `is_deleted = True` and cascade a deactivation to the associated `auth.User` object (`user.is_active = False`). 

**Rationale**: Properly prevents login instantly by targeting Django's built-in authentication system. The objects themselves stay physically on disk, maintaining historical contexts. 

**Alternatives considered**: 
- Disconnecting the foreign key rather than deactivating the user (leaves orphaned users).
- Complete physical cascade delete (violates the Constitution's Hard Delete prohibition).

## 3. Immediate Fallback Credentials

**Decision**: Implement `django.contrib.messages.success` within the `core/views.py` `admin_panel` student registration logic. Append the plaintext username and randomly generated password into the success message payload.

**Rationale**: It is safe for the current admin who just initiated the action to see it once inside their temporary session framework. This guarantees immediate fallback availability should the SMTP server fail.

**Alternatives considered**:
- An exposed REST endpoint returning the payload (unnecessary scope increase and potential security risk).
- Adding the password temporarily to the database (dangerous, violates Zero Plain-Text Secrets).
