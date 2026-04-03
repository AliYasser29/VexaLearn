from django import forms
from .models import Quiz, Question, Choice

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'duration', 'pass_score', 'specific_students']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'pass_score': forms.NumberInput(attrs={'class': 'form-control'}),
            
            'specific_students': forms.SelectMultiple(attrs={
                'class': 'form-control select2',  
                'data-placeholder': 'اختر الطلاب (اتركه فارغاً للجميع)'
            }),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'marks']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'نص السؤال'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
        }

from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.core.exceptions import ValidationError

class BaseChoiceFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        valid_choices_count = 0
        correct_choices_count = 0

        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            
            text = form.cleaned_data.get('text')
            is_correct = form.cleaned_data.get('is_correct')
            
            if text:
                valid_choices_count += 1
                if is_correct:
                    correct_choices_count += 1

        if valid_choices_count < 2:
            raise ValidationError('يجب إضافة خيارين على الأقل للسؤال.')

        if correct_choices_count != 1:
            raise ValidationError('يجب تحديد إجابة صحيحة واحدة فقط للسؤال.')

ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    formset=BaseChoiceFormSet,
    fields=['text', 'is_correct'],
    extra=0,
    can_delete=True,
    widgets={
        'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نص الخيار'}),
        'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input ms-2', 'style': 'transform: scale(1.5); cursor: pointer;'}),
    }
)