from django.contrib import admin
from calaccess_raw import models
from .base import BaseAdmin


class FilernameCdAdmin(BaseAdmin):
    list_display = (
        "id",
        "xref_filer_id",
        "filer_id",
        "naml",
        "namf",
        "filer_type",
        "status",
        "effect_dt",
    )
    list_filter = ("filer_type", "status")
    search_fields = (
        "xref_filer_id",
        "filer_id",
        "naml",
        "namf",
    )
    date_hierarchy = "effect_dt"


class FilerFilingsCdAdmin(BaseAdmin):
    search_fields = ("filing_id", "filer_id")
    list_display = (
        "id", "filer_id", "form_id",
        "filing_id", "filing_sequence"
    )


class FilingsCdAdmin(BaseAdmin):
    pass


class SmryCdAdmin(BaseAdmin):
    pass


class TextMemoCdAdmin(BaseAdmin):
    pass


class CvrE530CdAdmin(BaseAdmin):
    pass


admin.site.register(models.FilernameCd, FilernameCdAdmin)
admin.site.register(models.FilerFilingsCd, FilerFilingsCdAdmin)
admin.site.register(models.FilingsCd, FilingsCdAdmin)
admin.site.register(models.SmryCd, SmryCdAdmin)
admin.site.register(models.TextMemoCd, TextMemoCdAdmin)
admin.site.register(models.CvrE530Cd, CvrE530CdAdmin)
