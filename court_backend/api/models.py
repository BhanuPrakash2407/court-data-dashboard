from django.db import models

class CaseQueryLog(models.Model):
    case_type = models.CharField(max_length=50)
    case_number = models.CharField(max_length=50)
    filing_year = models.CharField(max_length=4)
    raw_html = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
