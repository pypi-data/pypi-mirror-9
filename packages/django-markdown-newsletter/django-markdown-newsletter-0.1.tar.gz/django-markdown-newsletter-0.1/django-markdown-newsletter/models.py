from django.db import models

class Subscribe(models.Model):
	email = models.EmailField(unique=True)
	newsletter = models.CharField(max_length=20,default='newsletter')
	timestamp = models.DateTimeField( auto_now_add=True, auto_now=False);
	updated = models.DateTimeField( auto_now_add=False, auto_now=True);
	ip_address=models.CharField(max_length=120,default='ABC')


	def __unicode__(self):
		return self.email;

class Newsletter(models.Model):
	subject=models.CharField(max_length=40)
	body=models.TextField()
	attachement=models.FileField(upload_to="newsletter")
	newsletter = models.CharField(max_length=20,default='newsletter')

