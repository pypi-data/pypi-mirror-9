from django.conf import settings
import redis as r

redis = r.from_url(settings.REDIS_URL)