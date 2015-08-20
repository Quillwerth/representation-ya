from django.db import models

# Create your models here.
class Tag(models.Model):
	title = models.CharField(max_length=200)
	def __str__(self):
		return self.title

class Author(models.Model):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	tags = models.ManyToManyField(Tag)
	def __str__(self):
		return self.first_name+" "+self.last_name

class Book(models.Model):
	title = models.CharField(max_length=200)
	isbn = models.CharField(max_length=20)
	author = models.ManyToManyField(Author)
	tags = models.ManyToManyField(Tag)
	def __str__(self):
		return self.title+" ("+self.isbn+")"



