from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import *
from import_export.admin import ImportExportModelAdmin

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

# Selective export
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

@admin.register(Recepient)
class RecepientAdmin(ImportExportModelAdmin):
    list_display = [i.name for i in Recepient._meta.get_fields()]
    actions = ["export_as_csv"]

@admin.register(Package)
class PackageAdmin(ImportExportModelAdmin):
    list_display = [i.name for i in Package._meta.get_fields()]
    actions = ["export_as_csv"]

@admin.register(Item)
class ItemAdmin(ImportExportModelAdmin):
    list_display = [i.name for i in Item._meta.get_fields()]
    actions = ["export_as_csv"]

@admin.register(Delivery)
class DeliveryAdmin(ImportExportModelAdmin):
    list_display = [i.name for i in Delivery._meta.get_fields()]
    actions = ["export_as_csv"]