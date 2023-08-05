from django import template
from django.conf import settings
from django.utils import translation

register = template.Library()


def clean_path(path):
    splited = path.split('/',2)
    for lang in settings.LANGUAGES:
        if splited[1] == lang[0]:
            return splited[2]
    return path


@register.simple_tag(takes_context=True)
def set_lang_from_path(context):
    if 'request' not in context:
        return ''
    lang = translation.get_language_from_request(context.get('request'), check_path=True)
    translation.activate(lang)
    context['lang'] = lang
    return ''


@register.simple_tag(takes_context=True)
def get_lang(context):
    if 'request' in context:
        context['lang'] = translation.get_language()
    return ''


@register.inclusion_tag('langswitch/lang_items.html', takes_context=True)
def show_lang_switch(context):
    if not 'request' in context:
        return {'langs': []}
    current_language = translation.get_language()
    cleaned_path = clean_path(context['request'].path)
    languages = list()
    for lang in settings.LANGUAGES:
        if current_language != lang[0]:
            languages.append({'lang_code': lang[0], 'lang_name': lang[1], 'path': cleaned_path})
    return {'langs': languages}
