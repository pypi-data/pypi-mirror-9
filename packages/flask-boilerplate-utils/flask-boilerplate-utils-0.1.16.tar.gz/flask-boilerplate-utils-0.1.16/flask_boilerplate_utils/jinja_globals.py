from flask import render_template_string, Markup

def render_field(field, **kwargs):
    """
    Returns a rendered field using the boilerplate's field renderer.

    :param field: A wtforms.field to render
    :param kwargs: Keyword arguments to send to the render macro. allows 
                   renderer configuration when calling this global within 
                   a template.
    """

    template = """
    {% from '_boilerplate/macros.html' import render_field %}
    {{ render_field(field, **kwargs) }}
    """
    return Markup(render_template_string(template, field=field, kwargs=kwargs))

def csrf_setup(**kwargs):
    """
    Return the CSRF setup global for injection into jinja templates.
    """

    template = """
    {% from '_boilerplate/macros.html' import csrf_setup %}
    {{ csrf_setup(**kwargs) }}
    """
    return Markup(render_template_string(template, kwargs=kwargs))