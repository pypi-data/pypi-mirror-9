from django.contrib import admin

#import local models
from djhcup_reporting.models import FilterGroup, Filter, ReportingTable, LookupTable, Universe, Column, Definition, DefLookups, Query, DataSet

#Register models
admin.site.register(FilterGroup)
admin.site.register(Filter)
admin.site.register(Column)
admin.site.register(ReportingTable)
admin.site.register(LookupTable)
admin.site.register(Universe)
admin.site.register(Definition)
admin.site.register(DefLookups)
admin.site.register(Query)
admin.site.register(DataSet)
