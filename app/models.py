from django.db import models
from accounts.models import Account
from datetime import datetime 

class uploadFile(models.Model):
    uploaded_by = models.ForeignKey(Account, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=120)
    file_path = models.CharField(max_length=500)
    file_uploaded = models.FileField(upload_to="temp_folder")
    token = models.CharField(max_length=200)

    def __str__(self):
        return self.file_name

class urlMapping(models.Model):
    original_url = models.CharField(max_length=500)
    short_token = models.CharField(max_length=100)
    opened = models.BooleanField(default=False)

    def __str__(self):
        return self.original_url

class shareFile(models.Model):
    sender_id = models.IntegerField()
    receiver_id = models.EmailField(max_length=100, default="test@test.com")
    file_path = models.CharField(max_length=500, default="test")
    file_name = models.CharField(max_length=100)
    share_date_time = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=100)
    doctor_name = models.CharField(max_length=250, default="")

    def __str__(self):
        return self.file_name + self.doctor_name

class passwordResetRequest(models.Model):
    email = models.EmailField(max_length=100, default='test@test.com')
    token = models.CharField(max_length=250, default='')
    requestAcceptedAt = models.DateTimeField(default=datetime.now, blank=True)
    requestUsed = models.BooleanField(default=False)

    def __str__(self):
        return self.email