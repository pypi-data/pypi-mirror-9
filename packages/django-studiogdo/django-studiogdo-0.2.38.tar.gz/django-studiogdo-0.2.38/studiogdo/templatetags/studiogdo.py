from django import template
from django.utils.safestring import mark_safe
from django.template.loader import get_template, get_template_from_string
from base64 import b64encode as encode, b64decode as decode
from django.conf import settings


register = template.Library()

default_facet_mode = getattr(settings, "STUDIOGDO_FACET_MODE", "dom5")


class SkelNode(template.Node):

    def __init__(self, skeleton, path):
        self.skeleton = skeleton
        self.path = path

    def render(self, context):
        skel = self.skeleton.resolve(context)
        path = self.path.resolve(context) if self.path else self.path
        t = get_template(skel)

        # get HTML renderer
        request = context['request']

        # render facet
        if settings.STUDIOGDO_FACET == "django":
            renderer = request.html_renderer
            facet = renderer.render(path, t.render(context))
        elif settings.STUDIOGDO_FACET == "java":
            api = request.studiogdo_api
            unprocessed_skel = t.render(context)
            facet_mode = context.get("studiogdo_facet_mode", default_facet_mode)
            response = api.post_facet(encode(path), unprocessed_skel, facet_mode)
            facet = unicode(response.content, 'utf-8')
            if facet_mode == "trans":
                rederended_skel = get_template_from_string("{%% load i18n %%}\n%s" % facet)
                facet = rederended_skel.render(context)

        # set trace
        studiogdo_debug = context.get('studiogdo_debug', None)
        if studiogdo_debug or (studiogdo_debug is None and getattr(settings, "STUDIOGDO_DEBUG", None)):
            return mark_safe("<!-- start %s (%s)-->\n" % (skel, path) + facet + "<!-- end %s -->\n" % skel)

        return mark_safe(facet)


@register.tag
def skel(parser, token):
    contents = token.split_contents()
    if len(contents) != 3:
        raise template.TemplateSyntaxError('skel needs at 2 arguments')
    else:
        skeleton = parser.compile_filter(contents[1])
        path = parser.compile_filter(contents[2])
        return SkelNode(skeleton, path)


@register.filter
def b64encode(value):
    return encode(value)

@register.filter
def b64decode(value):
    return decode(value)
