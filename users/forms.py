from django import forms
from .models import CustomUser

class UserCreationForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'name', 'description', 'profile_picture',
                  'date_of_birth',)
        
class UserChangeForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'name', 'description', 'profile_picture',
                  'date_of_birth',)

    def clean_password(self):
        return self.initial["password"]
