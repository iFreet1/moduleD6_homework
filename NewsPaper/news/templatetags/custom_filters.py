from django import template


register = template.Library()

censor_words = [
    "ПлохоеСлово1",
    "ПлохоеСлово2",
    "ПС1",
]

@register.filter(name='censor')
def censor(value, arg):
    for word in censor_words:
        value = str(value).replace(word, "")

    return str(value)