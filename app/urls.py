from django.urls import path
from django.conf.urls import url

from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('empire_ranking', views.empire_ranking, name='empire_ranking'),
    path('account', views.account, name='account'),
    url(r'^password/$', views.change_password, name='change_password'),
    path('units', views.units, name='units'),
    path('fleets', views.fleets, name='fleets'),
    path('fleetsend', views.fleetsend, name='fleetsend'),
    path('fleetdisband', views.fleetdisband, name='fleetdisband'),
    url(r'^empire(?P<empire_id>[0-9]+)/$', views.empire, name='empire'),
    path('vote', views.vote, name='vote'),
    path('vote_results', views.vote, name='voteresults'),
    path('pm_options', views.pm_options, name='prime_minister_options'),
    path('relations', views.relations, name='relations'),
    path('results', views.results, name='results'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)