from django.db import models


# Create your models here.

class Author(models.Model):
    openalex_id = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    works_count = models.IntegerField()
    cited_by_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
