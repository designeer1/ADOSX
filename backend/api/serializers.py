from rest_framework import serializers
from .models import ComparisonResult

class ComparisonResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComparisonResult
        fields = ['id', 'record_id', 'field_name', 'system_a_value', 
                 'system_b_value', 'reason', 'location', 'created_at']

