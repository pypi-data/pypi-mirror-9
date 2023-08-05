from django import template
register = template.Library()

@register.filter
def addattr(field, css):
   return field.as_widget(attrs={"class":css})
