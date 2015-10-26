from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission

from .models import *
# Register your models here.

admin.site.register(Tag)
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Character)
admin.site.register(TagGroup)
admin.site.register(Permission)