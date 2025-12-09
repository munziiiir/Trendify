from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

class StaffManagerUserAdmin(UserAdmin):
    def has_module_permission(self, request):
        return self.has_view_permission(request)

    def get_fieldsets(self, request, obj=None):
        if not request.user.is_superuser and request.user.groups.filter(name="Staff Manager").exists():
            return [(None, {'fields': ('groups',)})]
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and request.user.groups.filter(name="Staff Manager").exists():
            return [f.name for f in self.model._meta.fields if f.name != 'groups']
        return super().get_readonly_fields(request, obj)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name="Staff Manager").exists()

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name="Staff Manager").exists()

    def has_add_permission(self, request):
        # The staff manager cannot add new users
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # The staff manager cannot delete users
        return request.user.is_superuser

class CustomGroupAdmin(ModelAdmin):
    def has_module_permission(self, request):
        return self.has_view_permission(request)

    def has_view_permission(self, request, obj=None):
        # Allow viewing if user is superuser or in "Staff Manager"
        return request.user.is_superuser or request.user.groups.filter(name="Staff Manager").exists()

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
            and request.user.groups.filter(name__in=["Trendify Admin", "Staff Manager"]).exists()
        )

# Create an instance of the custom admin site
trendify_admin_site = TrendifyAdminSite(name='trendify_admin')

# Register the auth models with custom admin classes
# The User model is registered with a custom admin class to restrict permissions for staff managers.
trendify_admin_site.register(User, StaffManagerUserAdmin)

# The Group model is registered with a custom admin class to ensure only superusers can modify groups.
trendify_admin_site.register(Group, CustomGroupAdmin)