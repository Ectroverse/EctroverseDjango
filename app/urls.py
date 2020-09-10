from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.headquarters, name='headquarters'), # root page
    path('council', views.council, name='council'),
    path('map', views.map, name='map'),
    path('planets', views.planets, name='planets'),
    url(r'^planet(?P<planet_id>[0-9]+)/$', views.planet, name='planet'),
    url(r'^raze(?P<planet_id>[0-9]+)/$', views.raze, name='raze'),
    url(r'^razeall(?P<planet_id>[0-9]+)/$', views.razeall, name='razeall'),
    url(r'^build(?P<planet_id>[0-9]+)/$', views.build, name='build'),
    path('ranking', views.ranking, name='ranking'),
    path('account', views.account, name='account'),
    url(r'^password/$', views.change_password, name='change_password'),
    path('units', views.units, name='units'),
    path('fleets', views.fleets, name='fleets'),
    path('fleetsend', views.fleetsend, name='fleetsend'),
    path('fleetdisband', views.fleetdisband, name='fleetdisband'),
    path('empire', views.empire, name='empire'),
]
