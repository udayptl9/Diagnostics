from django.db import models

class Account(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=200)
    hospital_name = models.CharField(max_length=300, default="")
    password = models.CharField(max_length=500)
    token = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.first_name