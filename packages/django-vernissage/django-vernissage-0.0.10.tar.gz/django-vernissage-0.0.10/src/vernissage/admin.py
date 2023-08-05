from django.contrib import admin

from adminsortable.admin import SortableInlineAdminMixin

from vernissage import settings
from vernissage.models import Image, Gallery

class ImageInline(SortableInlineAdminMixin, admin.StackedInline):
    model = Image

class GalleryAdmin(admin.ModelAdmin):
    inlines = [
        ImageInline
    ]

if settings.VERNISSAGE_ADMIN:
    admin.site.register(Gallery, GalleryAdmin)
