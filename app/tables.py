import django_tables2 as tables
from .models import *
from django_tables2.utils import A  # alias for Accessor
from django_tables2 import SingleTableView

# User rank table
class UserRankTable(tables.Table):
    user_name = tables.Column(verbose_name='Player')
    empire_number  = tables.TemplateColumn('<a href="/empire{{record.empire_id}}/">{{record.empire_id}}</a>',accessor='empire.number', verbose_name='Empire')
    num_planets = tables.Column(verbose_name='Planets')
    networth = tables.Column(verbose_name='Networth')
    race = tables.Column(verbose_name='Race')
    class Meta:
        model = UserStatus
        attrs = {'class': 'table table-condensed'} # uses bootstrap table style
        fields = ("user_name", "empire_number", "num_planets", "networth", "race")

# Empire rank table
class EmpireRankTable(tables.Table):
    empire_names = tables.TemplateColumn('<a href="/empire{{record.id}}/">{{record.name_with_id}}</a>',verbose_name='Empire Name')
    planets = tables.Column(verbose_name='Planets')
    numplayers = tables.Column(verbose_name='Players')
    networth = tables.Column(verbose_name='Networth')
    class Meta:
        model = Empire
        attrs = {'class': 'table table-condensed'} # uses bootstrap table style
        fields = ("empire_names", "planets", "numplayers", "networth")

''' NEVER ENDED UP USING THIS
class PlanetTable(tables.Table):
    name = tables.TemplateColumn('<a href="{% url \'ootlist:oot_page\' record.id %}">{{record.name}}</a>') # links to oot_page
    tags = tables.Column(verbose_name='Categories')
    description = tables.Column(orderable=False) # no reason to ever sort by description imo
    last_commit = tables.Column(verbose_name='Most Recent Commit')
    gr_supported_version = tables.Column(verbose_name='GNU Radio supported versions')
    # this used the value of the status field to color the row, but it didn't look great
    def render_status(self, value, column):
        if value == 'maintained':
            column.attrs = {'td': {'bgcolor': 'lightgreen'}}
        elif value == 'undetermined':
            column.attrs = {'td': {'bgcolor': 'lightyellow'}}
        elif value == 'weak support':
            column.attrs = {'td': {'bgcolor': 'ffcccc'}}
        else:
            column.attrs = {'td': {}}
        return value

    class Meta:
        model = Planet
        fields = ('planet', 'size', 'total_buildings', 'overbuilt', '
        fields = ('name', 'last_commit', 'description', 'tags', 'gr_supported_version') # fields to display
        attrs = {'class': 'table table-condensed'} # uses bootstrap table style
'''
