from django.contrib.admin import AdminSite

class TrendifyAdminSite(AdminSite):
    site_header = "Trendify Admin Portal"
    site_title = "Trendify Administration"
    index_title = "Welcome to Trendify Admin"

    def has_permission(self, request):
        # Restrict access to users who are both staff and in the Trendify Admin group
        return (
            request.user.is_active 
            and request.user.is_staff 
            and request.user.groups.filter(name="Trendify Admin").exists()
        )

# Create an instance of the custom admin site
trendify_admin_site = TrendifyAdminSite(name='trendify_admin')