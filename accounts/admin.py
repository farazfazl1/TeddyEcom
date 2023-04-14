from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account


class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'username', 'last_login', 'date_joined', 'is_active',)

    list_display_links = ('email', 'first_name', 'last_name',)
    readonly_fields = ('last_login', 'date_joined',) #when clicked on user, these fileds are readonly
    ordering = ('-date_joined',)  # DESC based on date_joined

    search_fields = ('email', 'first_name', 'last_name',)

    # Required for accounts admin
    filter_horizontal = ()
    list_filter = ()

    # makes password read only
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
