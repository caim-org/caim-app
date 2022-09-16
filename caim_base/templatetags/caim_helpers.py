from django import template
from django.conf import settings
from sorl.thumbnail import get_thumbnail


register = template.Library()


@register.simple_tag(takes_context=True)
def modify_qs(context, key1=None, value1=None, key2=None, value2=None):
    request = context["request"]
    get = request.GET.copy()
    if key1:
        get[key1] = value1
    if key2:
        get[key2] = value2
    ret = get.urlencode()
    if ret == "":
        return ""
    return "?" + ret


# url | image_resize:"WxH crop|max"
@register.filter
def image_resize(value, resize):
    parts = resize.split(" ")
    if len(parts) == 1:
        parts.append("crop")
    if settings.IMAGE_RESIZE_USE_IMAGKIT:
        # Replace the S3 bucket with the imagekit CDN URL and add the resize params
        wh = parts[0].split("x")
        filter = "c-maintain_ratio,fo-auto,pr-true"
        if parts[1] == "max":
            filter = "c-at_max,pr-true"

        return (
            value.replace(settings.IMAGE_RESIZE_ORIGIN, settings.IMAGE_RESIZE_CDN)
            + f"?tr=w-{wh[0]},h-{wh[1]},{filter}"
        )
    else:
        # Use sorl-thumbnail to resize and return url
        value = value.replace("/media/", "")
        args = {
            "quality": 99,
        }
        if parts[1] == "crop":
            args["crop"] = "center"
        return get_thumbnail(value, parts[0], **args).url
