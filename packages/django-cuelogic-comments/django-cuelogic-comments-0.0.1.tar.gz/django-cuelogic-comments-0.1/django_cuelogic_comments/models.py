from django.db import models
from datetime import datetime
# Create your models here.

class Comments(models.Model):
	post_id=models.IntegerField(default=0)
	pub_date=models.DateField(default=datetime.now())
	name=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	contents=models.TextField()
	parent=models.IntegerField(default=0)

