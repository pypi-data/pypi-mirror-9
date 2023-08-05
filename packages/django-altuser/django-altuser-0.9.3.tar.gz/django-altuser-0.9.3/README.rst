INSTALL
=======

Put altuser in INSTALLED_APPS

::

    INSTALLED_APPS += (
        'altuser',
        )

and configure your preferred user model from available altuser/models.py,
for example

::

    AUTH_USER_MODEL = 'altuser.MailSocialUser'

Available models
----------------

 - MailUser
 - MailSocialUser

 - MailConfirmedUser
 - MailConfirmedSocialUser

 - MailSocialConfirmfollowUser
 - MailConfirmedSocialConfirmfollowUser

USAGE
=====

OneToOne
--------

If you use this User model with another Profile model you 
should put this field on you Profile model

::

    user = models.OneToOneField(settings.AUTH_USER_MODEL,   
                               related_name='profile')

If you have multiple profile types, you should use User.get_profile() to get
the right profile associated with this user, but you also must set
  
::

    ALTUSER_PROFILES_BREL = ['profile']

to a list of backward relation names (relate_name), of various profiles you have.
For example if you have two models, client and managers, associated with a OneToOneField to 
our user model, and they have different related_name, one client_profile and the other 
manager_profile, then ALTUSER_PROFILES_BREL must be ['client_profile', 'manager_profile']


GenericRelation
---------------

Actually you can also use the internal profile_type generic relation
on the provided AbstractMailUser, that will permit you to coerce one 
profile type per user, it is up to you if using that or not.

::

    # used in this way: self.user.get().usermodelfield
    user = generic.GenericRelation(settings.AUTH_USER_MODEL,
    content_type_field='profile_type',
    object_id_field='profile_id')

Generic relations in this way permits to have your user and profile
in the same inline and for example in the admin:

::

    from django.contrib import admin
    from .models import MannequineProfile
    from django.contrib.auth import get_user_model
    from django.contrib.contenttypes import generic

    class UserInline(generic.GenericTabularInline):
	model=get_user_model()
	extra=1
	max_num=1
    ct_field = 'profile_type'
    ct_fk_field = 'profile_id'
    exclude = ('last_login', 'is_staff', 'is_superuser',
            'groups', 'user_permissions' ,'likes',
            'follows')


    class ProfileAdmin(admin.ModelAdmin):
	inlines = [
        UserInline,
	]


    admin.site.register(Profile, ProfileAdmin)


Note also, that if you delete an object that has a GenericRelation, any objects which have a GenericForeignKey pointing at it will be deleted as well. 
In the example above, this means that if a Profile object were deleted, any user objects pointing at it would be deleted at the same time.


Confirmed Models
================

for using the mail confirmed models you must use [django-mail_confirmation](http://v.licheni.net/drc/django-mail_confirmation.git)

to filter out users that has confirmed social relations you do something like this:
    
    get_user_model().objects.filter(id=user.id, follows=otheruser, relations__confirmed__confirmed=True)
