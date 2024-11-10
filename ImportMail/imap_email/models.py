import uuid

from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    mail_pass = models.CharField(max_length=200, null=False)
    imap_server = models.CharField(max_length=200, null=False)
    last_login = models.DateTimeField(null=True, blank=True)
    auth_token = models.CharField(max_length=250, default=uuid.uuid4, unique=True)

    def __str__(self):
        return self.name


class Email(models.Model):
    id_message = models.TextField()
    bytes_message = models.CharField(max_length=101)
    title = models.TextField(null=True)
    data_export = models.CharField(null=True)
    data_import = models.CharField(max_length=104)
    message = models.TextField(null=True)
    attachment = models.CharField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
