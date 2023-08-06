# -*- coding: utf-8 -*-
#
#  quickapi/templatetags/quickapi.py
#  
#  Copyright 2012 Grigoriy Kramarenko <root@rosix.ru>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
#  
from __future__ import unicode_literals

from django import template
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from quickapi import conf

register = template.Library()

try:
    # Проверка установленного в системе markdown.
    from markdown import markdown
except:
    markdown_support = False
    markdown = None
else:
    markdown_support = True

try:
    # Проверка установленного в системе pygments.
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
except:
    highlight_support = False
    highlight = None
    get_lexer_by_name = None
    HtmlFormatter = None
else:
    highlight_support = True

def drop_space(doc):
    """
    Удаление начальных и конечных пробелов в документации.
    Выравнивает весь код по первой его строке.
    """
    L = []
    cut = None
    start_code = False
    for s in doc.split('\n'):
        # Если начинается код
        if s.strip(' ').startswith('`'):
            cut = len(s[:s.find('`')]) # только выставляем обрезку
            start_code = True          # устанавливаем начальный флаг
        # Если заканчивается код
        if s.strip().endswith('`') and not start_code:
            L.append(s[cut:])          # то записываем,
            cut = None                 # сбрасываем обрезку
            start_code = False         # сбрасываем начальный флаг
            continue                   # и прерываем цикл
        # Теперь записываем
        if not cut is None:
            L.append(s[cut:])          # с обрезкой
        else:
            L.append(s.strip(' '))     # или полностью очищенную строку
    return '\n'.join(L)

def highlight_prepare(text):
    """
    Обработка подстветки синтаксиса с помощью Pygments
    """
    TEXT = []
    MARK = []
    CODE = []
    start_code = False
    is_code = False
    lexer = None
    formatter = HtmlFormatter()

    for s in text.split('\n'):
        # Если начинается код
        if s.startswith('```') and not is_code:
            start_code = is_code = True # ставим флаги
            if markdown_support and MARK:
                # добавляем текст markdown
                try:
                    mark = markdown('\n'.join(MARK))
                except:
                    mark = ''
                TEXT.append(mark)
                MARK = [] # сбрасываем текст markdown
            continue # и прерываем цикл
        # Если закончился код
        elif s.startswith('```') and is_code:
            is_code = False # ставим флаги
            try:
                # Подсвечиваем код
                code = highlight('\n'.join(CODE), lexer, formatter)
            except:
                code = ''
            # Добавляем код в текст
            TEXT.append(code)
            CODE = []
            lexer = None
        # Если это первая строка кода
        elif start_code:
            if not s.startswith('#!'):
                raise ValueError('%s not start with #!' % s)
            # Устанавливем язык
            lexer = get_lexer_by_name(s.strip(' ').strip('#!'))
            start_code = False
            continue
        # Если это строка из кода
        elif is_code:
            CODE.append(s)
        elif markdown_support:
            MARK.append(s)
        else:
            TEXT.append(s)

    # Если что то осталось в markdown
    if markdown_support and MARK:
        # добавляем текст markdown
        try:
            mark = markdown('\n'.join(MARK))
        except:
            mark = ''
        TEXT.append(mark)

    return '\n'.join(TEXT)

@register.filter
def formatdoc(text):
    text = drop_space(force_text(text))
    if highlight_support:
        text = highlight_prepare(text)
    elif markdown_support:
        text = markdown(text)
    else:
        '<br>'.join(text.split('\n'))
    return text

@register.simple_tag
def PROJECT_NAME():
    return conf.PROJECT_NAME or _('Project')

@register.simple_tag
def PROJECT_URL():
    return conf.PROJECT_URL or '/'

@register.simple_tag
def DJANGO_VERSION():
    return conf.DJANGO_VERSION

@register.simple_tag
def QUICKAPI_VERSION():
    return conf.QUICKAPI_VERSION
