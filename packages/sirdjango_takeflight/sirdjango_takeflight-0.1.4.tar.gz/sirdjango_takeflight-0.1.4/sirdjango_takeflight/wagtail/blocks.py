from sirdjango.blocks import BaseBlock

from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.six import text_type

from wagtail.wagtailcore.rich_text import DbWhitelister, expand_db_html
from wagtail.wagtailcore.templatetags.wagtailcore_tags import richtext
from wagtail.wagtailimages.models import get_image_model, Filter, SourceImageIOError

__all__ = ['AdditionalInfoBlock', 'BlockquoteBlock', 'ByLineBlock', 'FullwidthImageBlock', 'FullwidthImageWithCaptionBlock',
           'HeadingBlock', 'Text', 'PullquoteBlock']

path_prefix = 'sirdjango_takeflight/wagtail/'


class ByLineBlock(BaseBlock):
    name = 'ByLineBlock'
    template = path_prefix + 'byline.html'

    class Media:
        js = [path_prefix + 'js/byline.js']

    def clean(self, data):
        if set(data.keys()) != {'text'}:
            raise ValidationError('Invalid data for {0} block'.format(self.name))
        return data

    def render_json(self, data):
        return render_to_string(self.template, data)


class AdditionalInfoBlock(BaseBlock):
    name = 'AdditionalInfoBlock'
    template = path_prefix + 'additionalinfo.html'

    class Media:
        js = [path_prefix + 'js/additionalinfo.js']

    def clean(self, data):
        if set(data.keys()) != {'title', 'text'}:
            raise ValidationError('Invalid data for {0} block'.format(self.name))
        return data

    def render_json(self, data):
        return render_to_string(self.template, data)


class BlockquoteBlock(BaseBlock):
    name = 'BlockquoteBlock'
    template = path_prefix + 'blockquote.html'

    class Media:
        js = [path_prefix + 'js/blockquote.js']

    def clean(self, data):
        if set(data.keys()) != {'quote', 'source'}:
            raise ValidationError('Invalid data for {0} block'.format(self.name))
        return data

    def render_json(self, data):
        return render_to_string(self.template, data)


class PullquoteBlock(BaseBlock):
    name = 'PullquoteBlock'
    template = path_prefix + 'pullquote.html'

    class Media:
        js = [path_prefix + 'js/pullquote.js']

    def clean(self, data):
        if set(data.keys()) != {'quote', 'source'}:
            raise ValidationError('Invalid data for {0} block'.format(self.name))
        return data

    def render_json(self, data):
        return render_to_string(self.template, data)


class HeadingBlock(BaseBlock):
    name = 'HeadingBlock'
    template = path_prefix + 'heading.html'

    class Media:
        js = [path_prefix + 'js/heading.js']

    def clean(self, data):
        if set(data.keys()) != {'heading', 'color'}:
            raise ValidationError('Invalid data for {0} block'.format(self.name))
        return data

    def render_json(self, data):
        return render_to_string(self.template, data)


class FullwidthImageWithCaptionBlock(BaseBlock):
    name = 'FullwidthImageWithCaptionBlock'
    filter_spec = 'max-165x165'
    template = path_prefix + 'fullwidthimagewithcaption.html'

    class Media:
        js = [path_prefix + 'js/fullwidthimagewithcaption.js']

    def clean(self, data):
        # May still exist if the image was not changed
        data.pop('image_tag', None)

        if set(data.keys()) != {'image_id', 'caption'}:
            raise ValidationError('Invalid data for {0} block'.format(self.name))

        Image = get_image_model()
        try:
            image = Image.objects.get(pk=data['image_id'])
        except Image.DoesNotExist:
            raise ValidationError('Image does not exist')

        filter, _ = Filter.objects.get_or_create(spec=self.filter_spec)
        try:
            rendition = image.get_rendition(filter)
        except SourceImageIOError:
            Rendition = image.renditions.model
            rendition = Rendition(image=image, width=0, height=0)
            rendition.file.name = 'not-found'

        image_tag = rendition.img_tag({'data-image-tag': True})
        data['image_tag'] = text_type(image_tag)

        return data

    def render_json(self, data):
        Image = get_image_model()
        try:
            image = Image.objects.filter(pk=data['image_id']).get()
        except Image.DoesNotExist:
            return ''
        context = data.copy()
        context.update({
            'image': image
        })
        return render_to_string(self.template, context)


class FullwidthImageBlock(BaseBlock):
    name = 'FullwidthImageBlock'
    filter_spec = 'max-165x165'
    template = path_prefix + 'fullwidthimage.html'

    class Media:
        js = [path_prefix + 'js/fullwidthimage.js']

    def clean(self, data):
        # May still exist if the image was not changed
        data.pop('image_tag', None)

        if set(data.keys()) != {'image_id'}:
            raise ValidationError('Invalid data for {0} block'.format(self.name))

        Image = get_image_model()
        try:
            image = Image.objects.get(pk=data['image_id'])
        except Image.DoesNotExist:
            raise ValidationError('Image does not exist')

        filter, _ = Filter.objects.get_or_create(spec=self.filter_spec)
        try:
            rendition = image.get_rendition(filter)
        except SourceImageIOError:
            Rendition = image.renditions.model
            rendition = Rendition(image=image, width=0, height=0)
            rendition.file.name = 'not-found'

        image_tag = rendition.img_tag({'data-image-tag': True})
        data['image_tag'] = text_type(image_tag)

        return data

    def render_json(self, data):
        Image = get_image_model()
        try:
            image = Image.objects.filter(pk=data['image_id']).get()
        except Image.DoesNotExist:
            return ''
        context = data.copy()
        context.update({
            'image': image,
        })
        return render_to_string(self.template, context)


class Text(BaseBlock):
    name = 'Text'

    class Media:
        js = [path_prefix + 'js/hallo.js']

    def clean(self, data):
        if set(data.keys()) != {'html'}:
            raise ValidationError('Invalid data for {0} block'.format(self.name))
        data['html'] = DbWhitelister.clean(data['html'])
        return data

    def json_for_editing(self, json):
        return {'html': expand_db_html(json['html'], for_editor=True)}

    def render_json(self, data):
        return richtext(data['html'])
