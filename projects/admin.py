from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "client_name", "contract_value_excl_vat")
    search_fields = ("name", "client_name")
