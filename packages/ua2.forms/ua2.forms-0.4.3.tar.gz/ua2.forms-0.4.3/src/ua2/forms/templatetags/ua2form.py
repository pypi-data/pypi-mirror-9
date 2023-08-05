from django import template

register = template.Library()


@register.simple_tag
def ua2_render_field(bound_field, **attrs):
    widget = bound_field.field.widget

    attrs['class'] = widget.attrs.get('class', '') + ' ' + attrs.get('class', '')

    if bound_field.field.show_hidden_initial:
        return bound_field.as_widget(attrs=attrs) + bound_field.as_hidden(only_initial=True)
    return bound_field.as_widget(attrs=attrs)
