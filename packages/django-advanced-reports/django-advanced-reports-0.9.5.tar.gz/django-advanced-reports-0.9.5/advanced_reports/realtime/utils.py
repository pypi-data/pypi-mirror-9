from __future__ import unicode_literals


try:
    from swampdragon.models import SelfPublishModel
except ImportError:
    class SelfPublishModel(object):
        pass

try:
    from swampdragon.serializers.model_serializer import ModelSerializer
except ImportError:
    class ModelSerializer(object):
        pass
