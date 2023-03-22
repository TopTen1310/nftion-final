from django import template

register = template.Library()


@register.simple_tag
def price_deal_range(num_range: str, type_range: str):
    if type_range == 'price':
        nums = num_range.split('_')
        if nums[1] == 'inf':
            return f'from ${nums[0]}'

        elif nums[0] == 'inf':
            return f'from 0$ to {nums[1]}$'

        return f'${nums[0]} - ${nums[1]}'

    else:
        nums = num_range.split('_')
        if nums[1] == 'inf':
            return f'from {nums[0]}'
        elif nums[0] == 'inf':
            return f'from 0 to {nums[1]}'
        return f'{nums[0]} - {nums[1]}'
