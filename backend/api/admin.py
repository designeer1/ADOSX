from django.contrib import admin
from .models import SystemARecord, SystemBRecord, Location, ComparisonResult

@admin.register(SystemARecord)
class SystemARecordAdmin(admin.ModelAdmin):
    list_display = ['record_id', 'location_id', 'total_value', 'state']
    search_fields = ['record_id', 'location_id']

@admin.register(SystemBRecord)
class SystemBRecordAdmin(admin.ModelAdmin):
    list_display = ['entry_id', 'record_ref', 'location_id', 'value']
    search_fields = ['entry_id', 'record_ref']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['location_id', 'location_name', 'org_id']
    search_fields = ['location_id', 'location_name']

@admin.register(ComparisonResult)
class ComparisonResultAdmin(admin.ModelAdmin):
    list_display = ['record_id', 'field_name', 'reason', 'created_at']
    list_filter = ['reason']
    search_fields = ['record_id', 'field_name']