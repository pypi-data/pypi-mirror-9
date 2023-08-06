from django.db import models
from cms.models import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class InstagramPluginModel(CMSPlugin):

    title = models.CharField(_('title'), max_length=100, blank=True, null=True)
    client_id = models.CharField(_('client ID'), max_length=100)
    user_id = models.IntegerField(_('user ID'))
    pictures = models.IntegerField(
        _('pictures'),
        help_text=_("Number of pictures displayed.")
    )

    def __str__(self):
        return self.title + ' ' + str(self.client_id)
