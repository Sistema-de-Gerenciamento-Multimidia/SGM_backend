from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    # Formulários para adicionar e alterar usuários
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    # Campos exibidos no admin
    list_display = ('email', 'username', 'name', 'date_of_birth', 'is_staff', 'is_active', 'date_joined',)
    list_filter = ('is_staff','is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Informações Pessoais', {'fields': ('name', 'description', 'date_of_birth', 'profile_picture',)}),
        ('Permissões', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions',)}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'name', 'password1', 'password2',
                       'description', 'date_of_birth', 'profile_picture', 'is_staff', 'is_active',),
        }),
    )
    search_fields = ('email', 'username', 'name',)
    ordering = ('-date_joined', 'email',)

# Registro no admin
admin.site.register(CustomUser, CustomUserAdmin)
