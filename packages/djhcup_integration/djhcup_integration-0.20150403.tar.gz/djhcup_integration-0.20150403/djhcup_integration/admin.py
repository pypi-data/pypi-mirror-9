from django.contrib import admin

#import local models
from djhcup_integration.models import Edition, IntegrationTable, Definition, Column, ColumnName, IntTblStgTblMembers, MappedColumn

#Register models
admin.site.register(Edition)
admin.site.register(IntegrationTable)
admin.site.register(Definition)
admin.site.register(Column)
admin.site.register(ColumnName)
admin.site.register(IntTblStgTblMembers)
admin.site.register(MappedColumn)
