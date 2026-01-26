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