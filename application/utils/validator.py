# -*- coding: utf-8 -*-
import imghdr
from datetime import datetime
import re
import xml.etree.cElementTree as et


class Validator:
    def __init__(self, data):
        self.data = dict(data)
        self.valid_data = ValidData(data)
        self.errors = {}

    def __getattr__(self, item):
        val = self.data.get(item, None)
        return val if len(val) > 1 else val[0]

    def field(self, name):
        return Field(self, name)

    def fields(self, name):
        return Field(self, name, as_list=True)

    def add_error(self, field, message, code=None, index=0):
        self.errors.setdefault(field, {})
        self.errors[field].setdefault(index, [])
        self.errors[field][index].append({"code": code, "message": message})

    def get_errors(self):
        return self.errors

    def is_valid(self):
        return False if self.errors else True


class ValidData:
    def __init__(self, data):
        self.__dict__.update({'_ValidData__data': dict(data)})

    def __setattr__(self, key, value):
        self.__data.set(key, list(value))

    def __getattr__(self, item):
        val = self.__data.get(item)
        if isinstance(val, list) and len(val) == 1:
            val = val[0]
        return val

    def __getitem__(self, item):
        return self.__data[item]

    def __setitem__(self, key, value):
        self.__data[key] = value

    def __repr__(self):
        return str(self.__data)

    def list(self, item):
        return self.__data.get(item)


class Field:
    def __init__(self, validator, name, as_list=False):
        self.validator = validator
        self.name = name
        self.as_list = as_list
        self.val = self.validator.data.get(self.name)
        if not isinstance(self.val, list):
            self.val = [self.val]

        self.validator.valid_data[name] = [v.strip().strip('\n').strip('\r') if isinstance(v, str) else v for v in self.val]

    @property
    def value(self):
        if self.as_list:
            return self.val
        else:
            return self.val[0]

    def required(self, message=None):
        code, message = get_message("required", message)
        for i, val in enumerate(self.val):
            if val is None or val is "":
                self.validator.add_error(self.name, message, code, index=i)
        return self

    def integer(self, message=None, nullable=False):
        code, message = get_message("not_integer", message)
        for i, val in enumerate(self.val):
            if nullable and val is "":
                self.validator.valid_data.list(self.name)[i] = None
            else:
                try:
                    self.validator.valid_data.list(self.name)[i] = int(val)
                except ValueError:
                    self.validator.add_error(self.name, message, code, index=i)
        return self

    def float(self, message=None, nullable=False):
        code, message = get_message("not_float", message)
        for i, val in enumerate(self.val):
            if nullable and val is "":
                self.validator.valid_data.list(self.name)[i] = None
            else:
                try:
                    self.validator.valid_data.list(self.name)[i] = float(val)
                except ValueError:
                    self.validator.add_error(self.name, message, code, index=i)
        return self

    def boolean(self, message=None, nullable=False):
        code, message = get_message("not_boolean", message)
        for i, val in enumerate(self.val):
            if nullable and (val is "" or val is None):
                self.validator.valid_data.list(self.name)[i] = None
            elif str(val).lower() in ['none', '', 'false', '0']:
                self.validator.valid_data.list(self.name)[i] = False
            else:
                self.validator.valid_data.list(self.name)[i] = True
        return self

    def length(self, max=None, min=None, message=None):
        if max is not None and min is not None:
            for i, val in enumerate(self.val):
                code, message = get_message("string_not_in_range", message)
                if len(val) < min or len(val) > max:
                    self.validator.add_error(self.name, message % {'min': min, 'max': max}, code, index=i)
        elif max is not None:
            for i, val in enumerate(self.val):
                code, message = get_message("string_too_long", message)
                if len(val) > max:
                    self.validator.add_error(self.name, message % {'min': min, 'max': max}, code, index=i)
        elif min is not None:
            for i, val in enumerate(self.val):
                code, message = get_message("string_too_short", message)
                if len(val) < min:
                    self.validator.add_error(self.name, message % {'min': min, 'max': max}, code, index=i)
        return self

    def image(self, formats=['png', 'gif', 'jpg', 'jpeg', 'tiff', 'bmp'], message=None):
        for i, val in enumerate(self.val):
            if val:
                code, message = get_message("not_image", message)
                try:
                    file_type = imghdr.what(val)
                except IOError:
                    file_type = None

                if type(formats) is list:
                    test_pass = file_type in formats
                else:
                    test_pass = file_type is formats
                if not test_pass:
                    self.validator.add_error(self.name, message, code, index=i)
        return self

    def svg(self, message=None):
        for i, val in enumerate(self.val):
            if val is not None:
                code, message = get_message("is_not_svg", message)
                filepath = val.file if type(val) is FileUpload else val
                tag = None
                try:
                    for event, el in et.iterparse(filepath, ('start',)):
                        tag = el.tag
                        break
                except et.ParseError:
                    self.validator.add_error(self.name, message, code, index=i)
                filepath.seek(0)
                if not tag == '{http://www.w3.org/2000/svg}svg':
                    self.validator.add_error(self.name, message, code, index=i)
        return self

    def email(self, message=None):
        code, message = get_message("wrong_email_format", message)
        for i, val in enumerate(self.val):
            if val is not None:
                val = val.strip()
                if re.match(r"[^@]+@[^@]+\.[^@]+", val):
                    self.validator.valid_data.list(self.name)[i] = val
                else:
                    self.validator.add_error(self.name, message, code, index=i)
        return self

    def datetime(self, message=None, format="%Y-%m-%d %H:%M:%S"):
        code, message = get_message("wrong_datetime_format", message)
        for i, val in enumerate(self.val):
            if val is not None and val != "":
                try:
                    val = val.strip()
                    self.validator.valid_data.list(self.name)[i] = datetime.strptime(val, format)
                except ValueError:
                    self.validator.add_error(self.name, message, code, index=i)
            else:
                self.validator.valid_data.list(self.name)[i] = None
        return self

    def equal(self, field, message=None):
        code, message = get_message("equal", message)
        if self.value != field.value:
            self.validator.add_error(self.name, message % {'field': field.name}, code)
        return self

    def old_password(self, message=None):
        code, message = get_message("old_password", message)
        self.validator.add_error(self.name, message, code)
        return self


def get_message(code, message):
    messages = {
        'required': "Обязательное поле",
        'not_integer': "Должно быть целым числом",
        'not_float': "Должно быть числом",
        'not_boolean': "Должно быть булевым значением",
        'string_not_in_range': "Длина текста должна быть не меньше %(min)d и не больше %(max)d символов",
        'string_too_short': 'Длина текста должна быть не меньше %(min)d символов',
        'string_too_long': 'Длина текста должна быть не больше %(max)d символов',
        'not_image': 'Файл не является картинкой',
        'is_not_svg': 'Файл не является SVG картинкой',
        'wrong_email_format': 'Введен неверный адрес электронной почты',
        'wrong_datetime_format': 'Неверный формат',
        'equal': "Должно повторять значение поля %(field)s",
        'old_password': 'Неверный старый пароль',
    }
    if message is None:
        message = messages[code]
    return code, message


__all__ = ["Validator"]
