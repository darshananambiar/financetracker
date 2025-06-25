from django import forms
from django.utils import timezone
from .models import Transaction, Category, Budget


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'description', 'type', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input'}),
            'description': forms.TextInput(attrs={'class': 'form-input'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            
            # If an instance is being edited, or a type is pre-selected, filter categories by type
            if self.instance.pk and self.instance.type:
                self.fields['category'].queryset = self.fields['category'].queryset.filter(type=self.instance.type)
            elif 'type' in self.initial:
                self.fields['category'].queryset = self.fields['category'].queryset.filter(type=self.initial['type'])
            elif 'type' in self.data:
                # For POST requests, if type is in data, filter by that type
                self.fields['category'].queryset = self.fields['category'].queryset.filter(type=self.data['type'])

        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        transaction_type = cleaned_data.get('type')
        
        if category and transaction_type:
            if category.type != transaction_type:
                raise forms.ValidationError(
                    f"Category '{category.name}' is for {category.type} but you selected {transaction_type}."
                )
        
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data['name']
        return name.strip().title()


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month']

    def clean_month(self):
        month = self.cleaned_data['month']
        return month.replace(day=1)
        widgets = {
            'month': forms.DateInput(attrs={'type': 'month', 'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Only show expense categories for budgets
            self.fields['category'].queryset = Category.objects.filter(
                user=user, type='expense'
            )
        
        # Set default month to current month
        if not self.instance.pk:
            self.fields['month'].initial = timezone.now().date().replace(day=1)