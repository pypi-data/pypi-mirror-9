from django.core.exceptions import ValidationError
from django.template import Library

register = Library()


@register.filter
def form_name(value):
    try:
        name = value.prefix
    except:
        name = 'Nope'
        raise ValidationError('Please, use it for form!')
    return name


@register.filter
def get_verbose_name_form(form):
    try:
        name = form.__dict__['forms'][0].__dict__['instance']._meta.verbose_name
    except:
        name = 'Nope'
    return name

@register.inclusion_tag('form_inlines/empty_formsets.html')
def empty_formsets(formsets):
    return {'formsets': formsets}

@register.inclusion_tag('form_inlines/main_form.html')
def main_form(form, formsets):
    return {'form': form, 'formsets': formsets}

@register.inclusion_tag('form_inlines/all_formsets.html')
def render_formsets(formsets):
    return {'formsets': formsets}
