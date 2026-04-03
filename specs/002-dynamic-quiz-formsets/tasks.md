---
description: "Task list for Dynamic Quiz Formsets Refactoring implementation"
---

# Tasks: Dynamic Quiz Formsets Refactoring

**Input**: Design documents from `/specs/002-dynamic-quiz-formsets/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths are included in the descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project readiness and structural checks

- [x] T001 [P] Verify `quiz/forms.py`, `quiz/views.py`, and `quiz/templates/quiz/add_question.html` locations exist.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that must be present before views and templates can tie the elements together.

- [x] T002 Create a base `BaseChoiceFormSet` and configure `ChoiceFormSet` using `inlineformset_factory(Question, Choice, ...)` in `quiz/forms.py`

**Checkpoint**: Foundation ready - Formset definitions exist and are accessible by views. User story implementations can begin.

---

## Phase 3: User Story 1 - Flexible Question Choices (Priority: P1) 🎯 MVP

**Goal**: When creating a quiz question, the teacher needs the flexibility to add varying amounts of choices instead of being constrained to a fixed number. They should be able to instantly add or remove answer options depending on the scenario.

**Independent Test**: Navigate to the question creation interface as a Teacher, click to add new options multiple times observing new fields appearing, and click remove on a few options observing them disappear.

### Implementation for User Story 1

- [x] T003 [US1] Create basic UI Formset layout loop rendering management forms and form inputs directly in `quiz/templates/quiz/add_question.html`
- [x] T004 [US1] Write Vanilla JavaScript function to dynamically duplicate the hidden Django `empty_form` modifying `TOTAL_FORMS` when "Add Option" clicked in `quiz/templates/quiz/add_question.html`
- [x] T005 [US1] Write Vanilla JavaScript listener bounded to the "Remove Option" button masking/hiding inputs or dropping the DOM node directly in `quiz/templates/quiz/add_question.html`
- [x] T006 [US1] Refactor `add_question` view stripping legacy hardcoded POST fetching logic, replacing it with instantiated `QuestionForm` and `ChoiceFormSet` parsing in `quiz/views.py`

**Checkpoint**: At this point, User Story 1 is fully functional. Teachers can freely generate unlimited option slots in the GUI without backend crashing initially.

---

## Phase 4: User Story 2 - Question Integrity Validation (Priority: P1)

**Goal**: To prevent broken quizzes from reaching students, the system must enforce strict logical rules before saving a question. A question must have enough choices to be valid, and must unambiguously identify exactly one correct answer.

**Independent Test**: Attempt to submit a question with only one option, or with zero correct options selected. The system must block the submission and route a validation error.

### Implementation for User Story 2

- [x] T007 [P] [US2] Implement `clean()` override loop enforcing >= 2 valid choices inside `BaseChoiceFormSet` in `quiz/forms.py`
- [x] T008 [P] [US2] Implement `clean()` logic tracking `is_correct` field evaluating exactly 1 truth value inside `BaseChoiceFormSet` in `quiz/forms.py`
- [x] T009 [US2] Verify `add_question` successfully intercepts `.is_valid()` rejections safely rolling back to the template state displaying form errors in `quiz/views.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work interchangeably mapping secure datasets into the SQLite instance.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that wrap up the implementation features.

- [x] T010 [P] Integrate proper class stylings onto dynamically appended JS nodes ensuring adherence to standard theme colors.
- [x] T011 Verify Constitution DRY rules are met: ensuring `TOTAL_FORMS` cleanly loops through logic.
- [x] T012 Run quickstart.md validation checklist locally mimicking the Teacher workflow.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends strictly on structure checks.
- **User Story 1 (P1)**: Strong coupling inside `UIView` mapping to `templates` and base form bindings.
- **User Story 2 (P2)**: Strictly builds upon Phase 2 model validation.
- **Polish (Final Phase)**: Depends on all user stories completed.

### Parallel Opportunities

```bash
# Form modifications and validation code can develop alongside JS frontend:
Developer A: Phase 3 GUI Scripts (T003, T004, T005 -> add_question.html) 
Developer B: Phase 4 Validation layers (T007, T008 -> forms.py)
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2: Setup Foundation
2. Bypass Phase 4 to directly target Phase 3 (US1 JS scripts tracking input logic).
3. **STOP and VALIDATE**: Test User Story 1 frontend manipulation dynamically mapping elements independently.

### Incremental Delivery

1. Complete Setup + Foundational.
2. Complete US1 → Deploy Formset rendering in Django Views (MVP Delivery).
3. Complete US2 → Enforce database-level logic guarantees avoiding broken quizzes reaching live servers.
