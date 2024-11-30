from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'name', 'description', 'profile_picture',
                  'date_of_birth',)
        
class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'name', 'description', 'profile_picture',
                  'date_of_birth',)

    def clean_password(self):
        return self.initial["password"]
