from django import template

register = template.Library()

@register.filter
def percent_of(*num):
    """
    :param num: list of numbers
    returns the first element over the sum of all elements in num * 100. Used to get percentage that
    the first element makes up compared to the sum
    """
    return float(num[0])/sum(num)


@register.filter
def divide(value, arg):
    return float(value) / float(arg)
