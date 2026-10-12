from django.contrib import admin

from .models import Municipality, Petition


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("staff",)


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ("registry_label", "subject", "municipality", "status", "created_at", "due_date", "is_overdue")
    list_filter = ("status", "municipality")
    search_fields = ("subject", "last_name", "registry_number")
    readonly_fields = ("tracking_code", "created_at", "registry_number", "registry_year")
    actions = ["register_selected"]

    def get_queryset(self, request):
        """Data isolation: staff only see petitions of their own municipalities."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(municipality__staff=request.user)

    @admin.display(boolean=True, description="depășită")
    def is_overdue(self, obj):
        return obj.is_overdue

    @admin.action(description="Înregistrează sesizările selectate")
    def register_selected(self, request, queryset):
        for petition in queryset:
            petition.register()
