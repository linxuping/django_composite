from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Publisher(models.Model):
	id = models.IntegerField(primary_key=True)  # AutoField?
	name = models.CharField(unique=True, max_length=30)
	city = models.CharField(max_length=60, null=True)
	#timestamp = models.DateTimeField(blank=True, null=True)

	class Meta:
		#managed = False
		#db_table = 'publisher'
		unique_together = (('name', 'city'),)


