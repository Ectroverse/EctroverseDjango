from django.urls import path
from django.conf.urls import url

from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),  # root page
    path('headquarters', views.headquarters, name='headquarters'),
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
    url(r'^empire(?P<empire_id>[0-9]+)/$', views.empire, name='empire'),
    path('vote', views.vote, name='vote'),
    path('vote_results', views.vote, name='voteresults'),
    path('pm_options', views.pm_options, name='prime_minister_options'),
    path('relations', views.relations, name='relations'),
    path('results', views.results, name='results'),
    path('research', views.research, name='research'),
    path('famaid', views.famaid, name='famaid'),
    path('famgetaid', views.famgetaid, name='famgetaid'),
    path('messages', views.game_messages, name='messages'),
    path('outbox', views.outbox, name='outbox'),
    url(r'^compose_message(?P<user_id>[0-9]*)/$', views.compose_message, name='compose_message'),
    url(r'^delete_message_inbox(?P<message_id>[0-9]+)/$', views.del_message_in, name='del_inbox'),
    url(r'^delete_message_outbox(?P<message_id>[0-9]+)/$', views.del_message_out, name='del_outbox'),
    path('delete_all_messages_inbox', views.bulk_del_message_in, name='delete_all_messages_inbox'),
    path('delete_all_messages_outbox', views.bulk_del_message_out, name='delete_all_messages_outbox'),
    path('guide', views.guide, name='guide'),
    path('faq', views.faq, name='faq'),
    path("registration/register", views.register, name="register"),
    path('logout', views.custom_logout, name='logout'),
    path('login', views.custom_login, name='login'),
    path('choose_empire_race', views.choose_empire_race, name='choose_empire_race'),
    path('fleets_orders', views.fleets_orders, name='fleets_orders'),
    path('fleets_orders_process', views.fleets_orders_process, name='fleets_orders_process'),
    path('fleets_disband', views.fleets_disband, name='fleets_disband'),
    path('fleets_disband', views.fleets_disband, name='fleets_disband'),
    path('famnews', views.famnews, name='famnews'),
    path('specops', views.specops, name='specops'),
    path('btn', views.btn, name='btn'),
	url(r'^battle(?P<fleet_id>[0-9]+)/$', views.battle, name='battle'),
    path('map_settings', views.map_settings, name='map_settings'),
    path('scouting', views.scouting, name='scouting'),
    path('halloffame', views.hall_of_fame, name='hall_of_fame'),
    url(r'^specop_show(?P<specop_id>[0-9]+)/$', views.specop_show, name='specop_show'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
