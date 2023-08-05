from rest_framework.serializers import FileField as RestFileField, Field
from wq.db.rest import serializers
from .models import FileField


class FileSerializer(serializers.ModelSerializer):
    is_image = Field('is_image')

    def __init__(self, *args, **kwargs):
        self.field_mapping[FileField] = RestFileField
        super(FileSerializer, self).__init__(*args, **kwargs)

    def from_native(self, data, files):
        obj = super(FileSerializer, self).from_native(data, files)
        if obj and hasattr(obj, 'user') and obj.user is None:
            if 'request' in self.context:
                user = self.context['request'].user
                if user.is_authenticated():
                    obj.user_id = user.pk
        return obj
