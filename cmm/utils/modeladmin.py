

class UserAdminMixin():
    """
    Mixin supposed to use with django.contrib.admin.UserAdmin
    Restrict user account availability.
    """
    readonly_fields = ("date_joined", "last_login",)

    def get_form(self, request, obj=None, **kwargs):
        """
        override ModelAdmin.get_form
        Return a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        form = super(UserAdminMixin, self).get_form(request, obj, **kwargs)
        disabled_fields = set()

        if not request.user.is_superuser:
            # disabled for "groups" is not working, maybe because it's a ManyToManyField?
            disabled_fields |= {"is_superuser", "username", "groups",}

            if obj is not None and obj == request.user:
                disabled_fields |= {"is_staff", "is_active", "user_permissions",}

            if obj is not None and obj != request.user:
                disabled_fields |= { "first_name", "last_name", "email", }

        for field in filter(lambda f: f in form.base_fields, disabled_fields):
            form.base_fields[field].disabled = True

        return form
