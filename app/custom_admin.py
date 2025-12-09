from django import forms
from django.contrib import messages
from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.admin.utils import unquote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect
from django.urls import reverse

class StaffManagerChangeForm(forms.ModelForm):
    password1 = forms.CharField(label="New password", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ["username", "is_staff"]

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 or p2:
            if not p1 or not p2 or p1 != p2:
                raise forms.ValidationError("Passwords must be provided and must match.")
        return cleaned_data

class StaffManagerUserAdmin(UserAdmin):
    # Fields shown when a staff manager adds a user; we force staff status in save_model.
    staff_manager_add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    # Fields shown when a staff manager edits a user.
    staff_manager_change_fieldsets = (
        (None, {
            'fields': ('username', 'is_staff', 'password1', 'password2'),
        }),
    )

    def has_module_permission(self, request):
        return self.has_view_permission(request)

    def get_form(self, request, obj=None, **kwargs):
        is_staff_manager = request.user.groups.filter(name="Staff Manager").exists()
        if not request.user.is_superuser and is_staff_manager and obj is not None:
            kwargs["form"] = StaffManagerChangeForm
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        is_staff_manager = request.user.groups.filter(name="Staff Manager").exists()
        if not request.user.is_superuser and is_staff_manager:
            if obj is None:
                return self.staff_manager_add_fieldsets
            return self.staff_manager_change_fieldsets
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        is_staff_manager = request.user.groups.filter(name="Staff Manager").exists()
        if not request.user.is_superuser and is_staff_manager:
            # Allow normal inputs during add; restrict everything except username and is_staff on change.
            if obj is None:
                return []
            return [f.name for f in self.model._meta.fields if f.name not in ('username', 'is_staff')]
        return super().get_readonly_fields(request, obj)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        is_staff_manager = request.user.groups.filter(name="Staff Manager").exists()
        if not is_staff_manager:
            return False
        # Staff Manager can view only what they can edit, plus their own account.
        if obj is None:
            return True
        if obj.pk == request.user.pk:
            return True
        return self.has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.groups.filter(name="Staff Manager").exists():
            return False
        # Staff Manager can only change staff users who are not superusers and not in admin groups.
        if obj is None:
            return True
        is_admin_group = obj.groups.filter(name__in=["Trendify Admin", "Staff Manager"]).exists()
        return obj.is_staff and not obj.is_superuser and not is_admin_group

    def has_add_permission(self, request):
        # Allow staff managers to add staff accounts; superuser retains full access.
        return request.user.is_superuser or request.user.groups.filter(name="Staff Manager").exists()

    def has_delete_permission(self, request, obj=None):
        # The staff manager cannot delete users
        return request.user.is_superuser

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        if obj is not None and not self.has_view_permission(request, obj):
            messages.error(request, "You cannot view/edit this account.")
            return redirect(reverse('trendify_admin:auth_user_changelist'))
        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        # Enforce staff-only creations/edits by Staff Manager and prevent superuser escalation.
        staff_manager = request.user.groups.filter(name="Staff Manager").exists() and not request.user.is_superuser
        if staff_manager:
            # On creation force staff; on edits allow toggling staff status but never superuser.
            if not change:
                obj.is_staff = True
            obj.is_superuser = False
            password1 = form.cleaned_data.get("password1") if form else None
            if password1:
                obj.set_password(password1)
        super().save_model(request, obj, form, change)
        if staff_manager:
            staff_users_group = Group.objects.filter(name="Staff User").first()
            if staff_users_group:
                obj.groups.add(staff_users_group)

class CustomGroupAdmin(ModelAdmin):
    def has_module_permission(self, request):
        # Hide groups entirely for non-superusers.
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        # Only superusers can view groups
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Only superuser can change groups
        return request.user.is_superuser

    def has_add_permission(self, request):
        # Only superuser can add groups
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Only superuser can delete groups
        return request.user.is_superuser

class TrendifyAdminSite(AdminSite):
    site_header = "Trendify Admin Portal"
    site_title = "Trendify Administration"
    index_title = "Welcome to Trendify Admin"

    def has_permission(self, request):
        return (
            request.user.is_active
            and request.user.is_staff
            and request.user.groups.filter(name__in=["Trendify Admin", "Staff Manager", "Staff User"]).exists()
        )

# Create an instance of the custom admin site
trendify_admin_site = TrendifyAdminSite(name='trendify_admin')

# Register the auth models with custom admin classes
# The User model is registered with a custom admin class to restrict permissions for staff managers.
trendify_admin_site.register(User, StaffManagerUserAdmin)

# The Group model is registered with a custom admin class to ensure only superusers can modify groups.
trendify_admin_site.register(Group, CustomGroupAdmin)
