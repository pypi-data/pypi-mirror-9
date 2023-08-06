#!coding: utf-8
"""
Общие хелперы
"""

import re
import warnings
from uuid import uuid4
from django.utils import datetime_safe


def is_valid_email(value):
    if (value is None):
        return
    ptn = re.compile(
        r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)",
        re.IGNORECASE
    )
    return ptn.match(value)


def normalize(str):
    """
    Конвертирует строку в вид, понятный javascript'у
    """
    return str.replace(
        '\r', '\\r'
    ).replace(
        '\n', '\\n'
    ).replace(
        '"', '\\"'
    ).replace(
        "'", "\\'"
    )


def generate_client_id():
    """
    Генерирует уникальный id для визуального компонента.
    """
    return 'cmp_' + str(uuid4())[0:8]


def get_img_size(src_size, dest_size):
    """
    Возвращает размеры изображения в пропорции с оригиналом исходя из того,
    как направлено изображение (вертикально или горизонтально)
    """
    width, height = dest_size
    src_width, src_height = src_size
    if height >= width:
        return (int(float(width)/height*src_height), src_height)
    return (src_width,  int(float(height)/width*src_width))


def generate_id():
    """
    Генерирует восьмизначный random.
    """
    return str(uuid4())[0:8]


def date2str(date, template='%d.%m.%Y'):
    """
    datetime.strftime глючит с годом < 1900
    типа обходной маневр (взято из django)
    WARNING from django:
    # This library does not support strftime's \"%s\" or \"%y\" format strings.
    # Allowed if there's an even number of \"%\"s because they are escaped.
    """
    return datetime_safe.new_datetime(date).strftime(template)


#==============================================================================
# Общие функции получения объектов из базы данных
#==============================================================================
def get_object_by_id(model, object_id):
    """
    Возвращает объект из базы данных указанного типа и
    указанным идентификатором. В случае, если в object_id
    оказался объект типа model, то он и возвращается.
    """
    warnings.warn(
        u'get_object_by_id is deprecated',
        category=DeprecationWarning,
        stacklevel=2,
    )

    result = None

    if isinstance(object_id, (int, str, unicode)):
        try:
            result = model.objects.get(pk=object_id)
        except model.DoesNotExist:
            result = None
    elif isinstance(object_id, model):
        result = object_id

    return result
