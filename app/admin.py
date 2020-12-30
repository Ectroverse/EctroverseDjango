from django.contrib import admin
from django.contrib.auth.models import User
from app.models import *
from django.forms import TextInput, Textarea
from django.db import models

admin.site.register(UserStatus)
admin.site.register(Planet)
admin.site.register(Construction)
admin.site.register(Fleet)
admin.site.register(UnitConstruction)
admin.site.register(RoundStatus)
admin.site.register(Empire)
admin.site.register(Relations)
admin.site.register(Messages)
#admin.site.register(NewsFeed)

class YourModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'50'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

admin.site.register(NewsFeed, YourModelAdmin)
