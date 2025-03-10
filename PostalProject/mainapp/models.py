from django.db import models

class PostOffice(models.Model):
    circlename = models.CharField(max_length=100)
    regionname = models.CharField(max_length=100)
    divisionname = models.CharField(max_length=100)
    officename = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    officetype = models.CharField(max_length=50)
    delivery = models.CharField(max_length=50)
    district = models.CharField(max_length=100)
    statename = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.officename} - {self.pincode}"


class ScannedMail(models.Model):
    mail_image = models.ImageField(upload_to='scanned_mails/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
