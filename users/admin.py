from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserCreationForm, UserChangeForm

class UserAdmin(BaseUserAdmin):
    # Formulários para adicionar e alterar usuários
    form = UserChangeForm
    add_form = UserCreationForm

    # Campos exibidos no admin
    list_display = ('email', 'username', 'name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'name', 'password')}),
        ('Permissões', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('date_joined', 'last_login')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'username', 'name')
    ordering = ('email',)

# Registro no admin
admin.site.register(User, UserAdmin)
