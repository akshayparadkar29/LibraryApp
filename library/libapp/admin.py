from django.contrib import admin
from libapp.models import Book

# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_display = ['title','author','sdesc','price','borrow','purchase','cart','uid']
    list_filter = ['author','price','uid']

admin.site.register(Book,BookAdmin)