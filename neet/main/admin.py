from django.contrib import admin
from .models import Center, Operator
@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')
    search_fields = ('name',)

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'center', 'phone', 'created_by')
    search_fields = ('name', 'center__name')
    list_filter = ('center',)