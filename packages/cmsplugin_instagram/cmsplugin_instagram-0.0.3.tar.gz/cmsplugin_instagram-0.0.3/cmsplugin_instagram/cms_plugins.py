# -*- coding: utf-8 -*-

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from .models import InstagramPluginModel
import requests


class InstagramPlugin(CMSPluginBase):
    model = InstagramPluginModel
    name = 'Instagram Plugin'
    render_template = "instagram/_instagram_plugin.html"

    def getImages(self, client_id, user_id, pictures):
        url = "https://api.instagram.com/v1/users/%(user_id)s/media/recent/?client_id=%(client_id)s&count=%(pictures)s" % {
                'user_id': user_id,
                'client_id': client_id,
                'pictures': pictures,
                }
        response = requests.get(url=url)
        images = []
        for image in response.json()['data']:
            new_image = {}
            new_image['url'] = image['images']['low_resolution']['url']
            new_image['link'] = image['link']
            images.append(new_image)
        return images

    def render(self, context, instance, placeholer):
        images = self.getImages(
                instance.client_id,
                instance.user_id,
                instance.pictures
                )
        context['title'] = instance.title
        context['images'] = images
        return context


plugin_pool.register_plugin(InstagramPlugin)
