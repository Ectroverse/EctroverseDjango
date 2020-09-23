from django.contrib import admin
from django.contrib.auth.models import User
from app.models import *

admin.site.register(UserStatus)
admin.site.register(Planet)
admin.site.register(Construction)
admin.site.register(Fleet)
admin.site.register(UnitConstruction)
admin.site.register(RoundStatus)
admin.site.register(Empire)
admin.site.register(Relations)
admin.site.register(Messages)