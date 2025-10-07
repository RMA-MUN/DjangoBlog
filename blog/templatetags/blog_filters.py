from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """自定义过滤器，用于从字典中获取值"""
    return dictionary.get(key)