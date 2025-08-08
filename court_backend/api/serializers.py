from rest_framework import serializers

class CaseInputSerializer(serializers.Serializer):
    case_type = serializers.CharField()
    case_number = serializers.CharField()
    filing_year = serializers.CharField()
