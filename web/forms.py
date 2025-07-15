from django import forms
from .models import Contribution, Project, District

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['first_name', 'last_name', 'phone_number', 'amount', 'project', 'district', 'zakah_type', 'number_of_people']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.Select(attrs={'class': 'form-select'}),
            'zakah_type': forms.Select(attrs={'class': 'form-select'}),
            'number_of_people': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of people', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].required = False
        self.fields['zakah_type'].required = False
        self.fields['number_of_people'].required = False
        self.fields['project'].queryset = Project.objects.filter(is_active=True)
        print(District.objects.all())
        self.fields['district'].queryset = District.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        zakah_type = cleaned_data.get('zakah_type')
        number_of_people = cleaned_data.get('number_of_people')

        if zakah_type == 'FITRI' and not number_of_people:
            self.add_error('number_of_people', 'Number of people is required for Zakah al-Fitr')
        
        return cleaned_data 