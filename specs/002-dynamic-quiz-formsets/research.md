# Research & Technical Decisions: Dynamic Quiz Formsets

## 1. Dynamic Forms Implementation
**Decision**: Use Django's native `inlineformset_factory` binding `Choice` to `Question`.
**Rationale**: Hardcoded `<input>` fields bounded out of POST directly are extremely brittle and violate DRY principles. Formsets are an idiomatic Django solution that natively handle arbitrary iteration loops via `formset.management_form`, which tracks total active forms.
**Alternatives considered**: Pure AJAX approach. This was rejected because it requires constructing separate REST endpoints and overcomplicates the atomic saving of the Question and its Choices in a single transaction.

## 2. Frontend DOM Interactions
**Decision**: Vanilla ES6 JavaScript leveraging HTML templates.
**Rationale**: Adding and removing options dynamically shouldn't rely on heavyweight frameworks like React or jQuery for such an isolated component. We can duplicate the `empty_form` provided by Django to seamlessly clone choice templates.
**Alternatives considered**: HTMX. While standard in advanced Django applications, it requires introducing external dependencies and learning curves for minimal gain over vanilla JS here.

## 3. Form Validation Mechanics
**Decision**: Implement custom `BaseInlineFormSet` clean override logic.
**Rationale**: Guaranteeing that the user has at least two active answers and exactly one correct answer can't be reliably left to the frontend alone. Extending `clean()` allows looping through `self.cleaned_data` explicitly ignoring forms flagged for deletion.
**Alternatives considered**: Model-level `clean()`. Rejected because validation logic on formsets often requires analyzing sibling sets simultaneously, which is easiest inside the FormSet itself.
