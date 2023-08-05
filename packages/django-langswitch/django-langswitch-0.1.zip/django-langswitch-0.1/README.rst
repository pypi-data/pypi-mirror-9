=====
langswitch
=====

langswitch - is django app, that can be used on multilingual sites to allow users switch site language, and use some template tags for maintain multilang links etc.

Quick start
-----------

1. Add "langswitch" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'langswitch',
    )
    
    and make sure that you have django.core.context_processors.request in TEMPLATE_CONTEXT_PROCESSORS:
    
    TEMPLATE_CONTEXT_PROCESSORS = (
    ...
    'django.core.context_processors.request',
    ...
    )

2. Load langswitch in your template:
    {% load lang_switch %}

3. Use template tag {% set_lang_from_path %} to activate translation, from url path (like /en/example/article/ for english language or /ru/example/article/ for russian)
this tag also defines variable 'lang' in template context, so you can use it.

4. Also you can just get variable 'lang' to template context with {% get_lang %} template tag