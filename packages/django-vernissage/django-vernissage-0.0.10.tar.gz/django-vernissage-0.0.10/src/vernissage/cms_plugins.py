# This file assumes that djangocms is imported. It should not be manually
# imported if django-cms is not installed, and if it is, it will be imported
# by the plugins autodiscovery feature

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from vernissage.models import GalleryPlugin
from vernissage.admin import ImageInline



class CMSGalleryPlugin(CMSPluginBase):
    model = GalleryPlugin
    module = _("Gallery")
    name = _("Gallery Plugin")
    render_template = "vernissage/gallery_plugin.html"

    inlines = [
        ImageInline,
    ]

    def render(self, context, instance, placeholder):
        context.update({"instance": instance})
        return context


plugin_pool.register_plugin(CMSGalleryPlugin)
