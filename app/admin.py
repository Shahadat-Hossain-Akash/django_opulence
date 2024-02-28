from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Transaction
from django.utils.translation import gettext_lazy as _

class CustomUser(UserAdmin):
    model = User
    list_display = ['username', 'email', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ['username', 'email']
    ordering = ['email']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    show_full_result_count = False


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['category', 'user', 'title', 'amount', 'created_at']
    list_filter = ['category']
    search_fields = ['title']
    list_select_related = ['category', 'user']
    show_full_result_count = False


admin.site.register(User, CustomUser)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Transaction, TransactionAdmin)
