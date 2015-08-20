from django.db import models

# Create your models here.
class TagGroup(models.Model):
	title = models.CharField(max_length=100)
	def __str__(self):
		return self.title

class Tag(models.Model):
	group = models.ForeignKey(TagGroup)
	title = models.CharField(max_length=200)
	def __str__(self):
		return str(self.group) + ": " + self.title

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

class Character(models.Model):
	book = models.ForeignKey(Book)
	name = models.CharField(max_length=100)
	tags = models.ManyToManyField(Tag)
	def __str__(self):
		return self.name

