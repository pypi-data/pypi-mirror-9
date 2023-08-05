from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from cmsplugin_news.models import LatestNewsPlugin, News
from cmsplugin_news import settings

from cms.utils import get_language_from_request
from django.db.models import Q


class CMSLatestNewsPlugin(CMSPluginBase):
    """
        Plugin class for the latest news
    """
    model = LatestNewsPlugin
    name = _('Latest news')
    render_template = "news/latest_news.html"

    def render(self, context, instance, placeholder):
        """
            Render the latest news
        """
        language = get_language_from_request(context['request'])
        News.published.select_language(language)
        latest = News.published.all()[:instance.limit]
        context.update({
            'instance': instance,
            'latest': latest,
            'placeholder': placeholder,
        })
        return context

if not settings.DISABLE_LATEST_NEWS_PLUGIN:
    plugin_pool.register_plugin(CMSLatestNewsPlugin)
