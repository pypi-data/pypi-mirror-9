from __future__ import absolute_import

import wtforms
import wtforms.widgets
import wtforms.fields


class ImageInput(wtforms.widgets.Input):
    """WTForms widget for image inputs (<input type="image">)
    """

    input_type = u'image'

    def __init__(self, src='', alt=''):
        self.src = src
        self.alt = alt

    def __call__(self, field, **kwargs):
        kwargs['src'] = self.src
        kwargs['alt'] = self.alt
        return super(ImageInput, self).__call__(field, **kwargs)


class ImageField(wtforms.fields.BooleanField):
    """WTForms field for image fields.
    """

    def __init__(self, src, alt='', **kwargs):
        widget = ImageInput(src, alt)
        super(wtforms.fields.BooleanField, self).__init__(widget=widget,
                **kwargs)
