from django.contrib import admin
from django.contrib.auth.models import User
from app.models import *
from django.forms import TextInput, Textarea
from django.db import models

# admin.site.register(UserStatus)
# admin.site.register(Planet)
admin.site.register(Construction)
# admin.site.register(Fleet)
admin.site.register(UnitConstruction)
admin.site.register(RoundStatus)
admin.site.register(Empire)
admin.site.register(Relations)
admin.site.register(Messages)
admin.site.register(News)
admin.site.register(MapSettings)
admin.site.register(Scouting)
admin.site.register(HallOfFame)
# admin.site.register(Specops)


class registerModel(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'50'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

admin.site.register(NewsFeed, registerModel)


class FleetAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Fleet._meta.get_fields()]
admin.site.register(Fleet, FleetAdmin)

class SpecopsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Specops._meta.get_fields()]
admin.site.register(Specops, SpecopsAdmin)

class UserStatusAdmin(admin.ModelAdmin):
    list_display = ["user","user_name"]
admin.site.register(UserStatus, UserStatusAdmin)


class PlanetAdmin(admin.ModelAdmin):
    list_display = ["x","y","i","owner"]
admin.site.register(Planet, PlanetAdmin)
