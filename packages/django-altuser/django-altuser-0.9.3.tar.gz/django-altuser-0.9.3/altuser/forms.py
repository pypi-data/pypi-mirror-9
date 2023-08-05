from __future__ import unicode_literals

from django import forms
from django.contrib.auth.forms import (ReadOnlyPasswordHashField,
                                       AuthenticationForm,
                                       PasswordResetForm, 
                                       SetPasswordForm, 
                                       PasswordChangeForm, 
                                       AdminPasswordChangeForm)
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    It could be used also for derived MailUser models, it gets User model from
    settings.AUTH_USER_MODEL .
    """
    error_messages = {
        'duplicate_email': _("A user with that email already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    email = forms.EmailField(label=_("Email"), max_length=254,
        help_text=_("Required. Valid email for registration and login."),
        error_messages={
            'invalid': _("This value must be a valid email address.")})
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = get_user_model()
        fields = ("email",)

    def clean_email(self):
        # Since User.email is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data["email"]
        try:
            get_user_model()._default_manager.get(email=email)
        except get_user_model().DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """
    Changes user email and password
    """
    email = forms.EmailField(
        label=_("Email"), max_length=254,
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = get_user_model()
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('profile_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AuthenticationForm(AuthenticationForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    
    Derives auth.contrib.AuthenticationForm and it is usable for
    username password sematic
    """
    pass


class PasswordResetForm(PasswordResetForm):
    """
    Derives auth.contrib.PasswordResetForm and it is usable for
    mail password sematic
    """
    pass


class SetPasswordForm(SetPasswordForm):
    """
    A form that lets a user change set his/her password without entering the
    old password
    """
    pass

class PasswordChangeForm(PasswordChangeForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    pass


class AdminPasswordChangeForm(AdminPasswordChangeForm):
    """
    A form used to change the password of a user in the admin interface.
    """
    pass

class AdminUserPasswordChangeForm(UserChangeForm):
    """ 
    A form to change the username and the password simultaneously
    without asking the previous password to the user
    """
    password = forms.CharField(label=_("Password"),
                               help_text=_("Leave empty to not update the password"),
                               required=False,
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"),
                                required=False,
                                widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2:
            if password != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password

    def save(self, commit=True):
        """
        Saves the new password.
        """
        if self.cleaned_data['password']:
            self.instance.set_password(self.cleaned_data["password"])
            if commit:
                self.instance.save()
        return super(AdminUserPasswordChangeForm, self).save(commit)


try:
    from .models import FollowsConfirmed

    class FollowConfirmUserForm(forms.Form):
        """
        A form that permits another user to follow another
        """
        email = forms.EmailField(help_text=_('The user email address'))

        def __init__(self, check_existence=True, *args, **kwargs):
            super(FollowConfirmUserForm, self).__init__(*args, **kwargs)
            self._check_existence = check_existence

        def clean_email(self):
            email = self.cleaned_data['email']
            if self._check_existence:
                try:
                    user = get_user_model().objects.get(email=self.cleaned_data['email'])
                except get_user_model().DoesNotExist:
                    self._errors['email'] = _('No user with this email exists')
            return email

        def save(self, commit=True, follower=None, mutual=False, 
                 askconfirm=True, followeraskconfirm=False):
            if not follower:
                raise ValueError("follower parameter must not be None")
            user = get_user_model().objects.get(email=self.cleaned_data.get('email', None))
            instance_r = FollowsConfirmed(follower=follower, followed=user)
            if commit:
                instance_r.save(askconfirm)
                if mutual:
                    instance_d = FollowsConfirmed(follower=user, followed=follower)
                    instance_d.save(followeraskconfirm)
            return instance_r


    class FollowConfirmUserWithpasswordForm(FollowConfirmUserForm):
        """
        A form that permits another user to follow another one providing his password
        """
        password = forms.CharField(widget=forms.PasswordInput)

        def __init__(self, check_password=True, *args, **kwargs):
            super(FollowConfirmUserWithpasswordForm, self).__init__(*args, **kwargs)
            self._check_password = check_password
            if not check_password:
                self.fields['password'].required = False
                self.fields['password'].help_text = _('The password will not be checked if the user exists, insert only the user email')

        def clean(self):
            cleaned_data = super(FollowConfirmUserWithpasswordForm, self).clean()
            try:
                user = get_user_model().objects.get(email=cleaned_data.get('email', None))
                if not self._check_password or (user and user.check_password(cleaned_data.get('password', None))):
                    return cleaned_data 
                else:
                    cleaned_data['password'] = ""
                    self._errors['password'] = [_('Your username and password didn\'t match.')]
            except get_user_model().DoesNotExist:
                pass

            return cleaned_data 

except ImportError:
    pass
