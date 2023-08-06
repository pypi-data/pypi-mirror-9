import urllib, json, re
from django.db import models

class Video(models.Model):

    channel_id = models.SlugField()

    def get_video_json(self):
        url = 'http://gdata.youtube.com/feeds/users/' + self.channel_id + '/uploads?alt=json'
        response = urllib.urlopen(url)
        data = json.loads(response.read())

        videos = []
        for v in data['feed']['entry']:

            videos.append({
                'title': v['title']['$t'],
                'id': re.findall(r'[^/]*$',v['id']['$t'])[0],
                'thumnails': v['media$group']['media$thumbnail']
            })

        return videos



