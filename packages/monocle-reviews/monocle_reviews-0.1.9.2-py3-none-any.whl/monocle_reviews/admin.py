from django.contrib import admin
from .models import *

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer','position','isShown',)
    list_editable = ('position','isShown',)



admin.site.register(Review, ReviewAdmin)
