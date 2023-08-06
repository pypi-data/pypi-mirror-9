from __future__ import unicode_literals

from django.forms.fields import (
    MultiValueField,
    CharField,
    ImageField
)

from .widgets import (
    VersatileImagePPOIClickWidget,
    SizedImageCenterpointClickDjangoAdminWidget
)


class SizedImageCenterpointMixIn(object):

    def compress(self, data_list):
        return tuple(data_list)


class VersatileImageFormField(ImageField):

    def to_python(self, data):
        """
        Ensures data is prepped properly before handing off to
        ImageField
        """
        if data is not None:
            if hasattr(data, 'open'):
                data.open()
            return super(VersatileImageFormField, self).to_python(data)


class VersatileImagePPOIClickField(SizedImageCenterpointMixIn,
                                   MultiValueField):
    widget = VersatileImagePPOIClickWidget

    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length', None)
        del max_length
        fields = (
            VersatileImageFormField(label='Image'),
            CharField(required=False)
        )
        super(VersatileImagePPOIClickField, self).__init__(
            tuple(fields), *args, **kwargs
        )


class SizedImageCenterpointClickDjangoAdminField(
        VersatileImagePPOIClickField):
    widget = SizedImageCenterpointClickDjangoAdminWidget
    # Need to remove `None` and `u''` so required fields will work
    # TODO: Better validation handling
    empty_values = [[], (), {}]
