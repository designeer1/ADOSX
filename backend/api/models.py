from django.db import models

class SystemARecord(models.Model):
    """System A records - one per event"""
    record_id = models.CharField(max_length=50, db_index=True)
    location_id = models.CharField(max_length=50, blank=True, null=True)
    event_date = models.CharField(max_length=50, blank=True, null=True)
    category_code = models.CharField(max_length=50, blank=True, null=True)
    actor_id = models.CharField(max_length=50, blank=True, null=True)
    base_value = models.CharField(max_length=50, blank=True, null=True)
    adjustment = models.CharField(max_length=50, blank=True, null=True)
    total_value = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'system_a_records'
    
    def __str__(self):
        return f"A-{self.record_id}"

class SystemBRecord(models.Model):
    """System B records - may have multiple entries per record"""
    entry_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    record_ref = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    location_id = models.CharField(max_length=50, blank=True, null=True)
    recorded_on = models.CharField(max_length=50, blank=True, null=True)
    value = models.CharField(max_length=50, blank=True, null=True)
    label = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        db_table = 'system_b_records'
    
    def __str__(self):
        return f"B-{self.entry_id}"

class Location(models.Model):
    """Location data with org mapping"""
    location_id = models.CharField(max_length=50, db_index=True)
    org_id = models.CharField(max_length=50)
    location_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'locations'
    
    def __str__(self):
        return f"{self.location_name} ({self.org_id})"

class ComparisonResult(models.Model):
    """Stored comparison results"""
    record_id = models.CharField(max_length=50, db_index=True)
    field_name = models.CharField(max_length=100)
    system_a_value = models.TextField(blank=True, null=True)
    system_b_value = models.TextField(blank=True, null=True)
    reason = models.CharField(max_length=50, db_index=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['record_id', 'field_name']
        db_table = 'comparison_results'
    
    def __str__(self):
        return f"{self.record_id} - {self.field_name}: {self.reason}"