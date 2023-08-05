from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from .models import MailUser, MailSocialUser
from .forms import UserCreationForm, UserChangeForm

class MailUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    # The forms to add and change user instances
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    list_display = ('email', 'is_staff')
    search_fields = ('email', 'is_staff')
    ordering = ('email',)


class MailSocialUserAdmin(MailUserAdmin):
    fieldsets = MailUserAdmin.fieldsets + (
        (_('Social interactions'), {'fields': ('follows', 'likes')}),
    )


admin.site.register(MailUser, MailUserAdmin)
admin.site.register(MailSocialUser, MailSocialUserAdmin)


try: 
    from .models  import MailConfirmedUser, MailConfirmedSocialUser, MailSocialConfirmfollowUser, MailConfirmedSocialConfirmfollowUser


    class MailConfirmedUserAdmin(MailUserAdmin):
        fieldsets = MailUserAdmin.fieldsets + (
            (_('Confirmed'), {'fields': ('confirmed',)}),
        )
        list_display = MailUserAdmin.list_display + ('confirmed',)


    class MailConfirmedSocialUserAdmin(MailConfirmedUserAdmin):
        fieldsets = MailConfirmedUserAdmin.fieldsets + (
            (_('Social interactions'), {'fields': ('follows', 'likes')}),
        )


    class FollowsInline(admin.TabularInline):
        model = FollowsConfirmed
        fields = ['date', 'follower', 'followed', 'confirmed']


    class MailSocialConfirmfollowUserAdmin(MailSocialUserAdmin):
        inlines = ['FollowsInline',]


    class MailConfirmedSocialConfirmfollowUserAdmin(MailConfirmedUserAdmin):
        inlines = ['FollowsInline',]


    admin.site.register(MailConfirmedUser, MailConfirmedUserAdmin)
    admin.site.register(MailConfirmedSocialUser, MailConfirmedSocialUserAdmin)

    admin.site.register(MailSocialConfirmfollowUser, MailSocialConfirmfollowUserAdmin)
    admin.site.register(MailConfirmedSocialConfirmfollowUser, MailConfirmedSocialConfirmfollowUserAdmin)


except:
    pass
