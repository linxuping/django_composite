from django.contrib import admin
from models import Publisher

# Register your models here.

	
class PublisherAdmin(admin.ModelAdmin):
   list_display =('title','timestamp')    

admin.site.register(Publisher, PublisherAdmin)  