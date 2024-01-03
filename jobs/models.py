from django.db import models

# Create your models here.

class Job(models.Model):
    job_logo = models.ImageField(upload_to='images/')
    job_link = models.URLField(max_length=200)
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    time_added = models.DateTimeField(auto_now=True, editable=False)
    job_description = models.TextField()

    def __str__(self):
        return f"{self.company_name} - {self.job_title}"