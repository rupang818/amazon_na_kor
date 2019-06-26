from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import *
from import_export.admin import ImportExportModelAdmin
import copy

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

@admin.register(Recipient)
class RecipientAdmin(ImportExportModelAdmin):
    list_display = [i.name for i in Recipient._meta.get_fields()]
    actions = ["export_as_csv"]

@admin.register(Package)
class PackageAdmin(ImportExportModelAdmin):
    list_display = [i.name for i in Package._meta.get_fields()]
    actions = ["export_as_csv"]

@admin.register(Item)
class ItemAdmin(ImportExportModelAdmin):
    list_display = [i.name for i in Item._meta.get_fields()]
    actions = ["export_as_csv"]

#####################################
# Delivery Object utility functions #
#####################################
def mark_dropped_off(modeladmin, request, queryset):
    queryset.update(dropped_off=True)
mark_dropped_off.short_description = "SET selected as \"DROPPED OFF\""

def unmark_dropped_off(modeladmin, request, queryset):
    queryset.update(dropped_off=False)
unmark_dropped_off.short_description = "UNSET selected as \"DROPPED OFF\""

def mark_sent(modeladmin, request, queryset):
    queryset.update(sent=True)
mark_sent.short_description = "SET selected as \"SENT\""

def unmark_sent(modeladmin, request, queryset):
    queryset.update(sent=False)
unmark_sent.short_description = "UNSET selected as \"SENT\""

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_email', 'recipient_id', 'package_id', 'customs_fee_payee', 'method', 'agreement_signed', 'estimate', 'dropped_off', 'sent')
    actions = [mark_dropped_off, unmark_dropped_off, mark_sent, unmark_sent]