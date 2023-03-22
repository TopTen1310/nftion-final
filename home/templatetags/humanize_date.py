from django import template

register = template.Library()


@register.simple_tag
def humanize_date(date: str):
    if date:
        if 'day' in date:
            date = date.split()
            return f'{date[0]} {date[1]}'
        else:
            date = date.split(':')
            if date[0] == '0':
                if date[1] == '00':
                    return f'{date[2]} sec'
                else:
                    return f'{date[1]} min'
            else:
                if date[1] == '00':
                    return f'{date[0]} {plural(date[0])}'
                else:
                    return f'{date[0]} {plural(date[0])}, {date[1]} min'




def plural(number):
    number = int(number)
    if number == 1:
        return 'hour'
    else:
        return 'hrs'
