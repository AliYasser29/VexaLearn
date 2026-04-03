# Research & Technical Decisions: Chat Perf & Security

## 1. Chat Users Fetching
**Decision**: Refactor contact extraction leveraging `django.db.models.Q` with `.distinct()`.
**Rationale**: The previous approach iterated through Python list comprehensions and explicit `|` OR unions appending user records. This scales exponentially in memory. `User.objects.filter(Q(student_profile__enrollment__course__teacher__user=request.user) | ...).distinct()` forces query analysis downstream onto PostgreSQL/SQLite C-level binaries rendering near zero computational cost on the python process.
**Alternatives considered**: Redis Caching. Rejected to avoid overcomplicating stack with Redis just to resolve poorly formed Python querying logic.

## 2. Agora Token Expiration Bound
**Decision**: Hardcode expiration variables down to `7200` seconds from `86400` inside Python payload hashing.
**Rationale**: 2 hours spans the longest configured lecture format natively expected. Limiting the attack window by 22 hours per footprint exponentially reduces the risk of playback abuse.

## 3. Pre-Token Authorization
**Decision**: Enforce course linkage filters actively wrapping `RtcTokenBuilder` instantiations.
**Rationale**: Returning validly hashed tokens to properly authenticated users who simply 'aren't in the specific given course' defeats the role of video security. Token bounds must verify class assignment directly.
