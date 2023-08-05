from django.contrib import admin
from django_cuelogic_comments.models import Comments
from django.db import models

# Register your models here.


class CommentAdmin(admin.ModelAdmin):
    list_display = ['name','email','contents','pub_date']

admin.site.register(Comments, CommentAdmin)