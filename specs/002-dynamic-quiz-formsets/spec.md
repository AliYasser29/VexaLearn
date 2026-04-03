# Feature Specification: Dynamic Quiz Formsets Refactoring

**Feature Branch**: `002-dynamic-quiz-formsets`  
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: User description: "Dynamic Quiz Formsets Refactoring. Objective: Refactor the quiz question creation view to support dynamic choices..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Flexible Question Choices (Priority: P1)

When creating a quiz question, the teacher needs the flexibility to add varying amounts of choices instead of being constrained to a fixed number. They should be able to instantly add or remove answer options depending on whether they are creating a True/False question, a standard 4-option question, or a complex 6-option scenario.

**Why this priority**: Constraining teachers to hardcoded choice limits severely restricts assessment capabilities and increases frustration. It is the primary objective of this refactor.

**Independent Test**: Navigate to the question creation interface as a Teacher, click to add new options multiple times observing new fields appearing, and click remove on a few options observing them disappear.

**Acceptance Scenarios**:

1. **Given** a teacher is drafting a new question, **When** they click to add an option, **Then** a new blank choice field appears on the interface without reloading the page.
2. **Given** a teacher has added unnecessary options, **When** they click to remove an option, **Then** the selected choice field is immediately removed from the interface layout.

---

### User Story 2 - Question Integrity Validation (Priority: P1)

To prevent broken quizzes from reaching students, the system must enforce strict logical rules before saving a question. A question must have enough choices to be valid, and must unambiguously identify the correct answer.

**Why this priority**: Data integrity is crucial. If a teacher accidentally creates a question with zero correct answers, it breaks grading logic and causes false failures for students.

**Independent Test**: Attempt to submit a question with only one option, or with zero correct options selected. The system must block the submission and present a clear validation error.

**Acceptance Scenarios**:

1. **Given** a teacher tries to save a question with fewer than two options, **When** they submit the form, **Then** the system rejects the submission and alerts them that at least two options are required.
2. **Given** a teacher tries to save a question, **When** they submit without marking any option as correct, **Then** the system rejects the submission and prompts them to select exactly one correct answer.
3. **Given** a teacher tries to save a question, **When** they submit with multiple options marked as correct simultaneously, **Then** the system rejects the submission and asks them to specify exactly one correct choice.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow users to dynamically append new answer choices continuously to the question drafting form.
- **FR-002**: The system MUST allow users to dynamically delete appended answer choices from the drafting form.
- **FR-003**: The system MUST block the saving of any question that possesses fewer than two declared answer choices.
- **FR-004**: The system MUST block the saving of any question where exactly one choice is not explicitly marked as the correct answer.
- **FR-005**: (Constitution) The interface MUST use dynamic structured form data binding techniques rather than brittle hardcoded limits, ensuring adherence to the DRY and Code Quality principles.

### Key Entities

- **Question Draft**: The core configuration of the quiz question.
- **Flexible Answer Choices**: The variable list of potential answers tethered to a parent question draft, containing the text and the boolean correctness flag.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Interacting with the "Add" and "Remove" choice buttons completes instantaneously (perceived <100ms lag) without full page reloads.
- **SC-002**: 100% of newly created questions flowing into the database after this feature is deployed contain at least two valid options.
- **SC-003**: 100% of newly created questions contain exactly one identifiable correct answer payload.
- **SC-004**: Teachers report 0% occurrences of being unable to add more than 4 choices to a single question.

## Assumptions

- Questions continue to strictly follow a "Single Correct Answer" semantic rather than "Multiple Correct Answers" format.
- The interface enhancements are strictly constrained to the core web platform.
