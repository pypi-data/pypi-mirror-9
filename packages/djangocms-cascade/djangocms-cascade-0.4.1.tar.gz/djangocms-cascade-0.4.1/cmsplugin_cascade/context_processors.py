# -*- coding: utf-8 -*-


def placeholder_glossary(request):
    context = {
        'COLUMN_GLOSSARY': {
            'breakpoints': ['xs', 'sm', 'md', 'lg'],
            'container_max_widths': {'xs': 750, 'sm': 750, 'md': 970, 'lg': 1170},
            'fluid': False,
            'media_queries': {
                'xs': ['(max-width: 768px)'],
                'sm': ['(min-width: 768px)', '(max-width: 992px)'],
                'md': ['(min-width: 992px)', '(max-width: 1200px)'],
                'lg': ['(min-width: 1200px)'],
            },
        }
    }
    return context
