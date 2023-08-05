#coding: utf-8
"""
Хелперы для удобного чтения конфигурационного файла проекта

@author: akvarats
"""

import ConfigParser

class ProjectConfig:
    """
    Обертка над парсером параметров конфигурации
    """
    def __init__(self, filenames=[], defaults={}):
        self.parser = ConfigParser.ConfigParser()
        if filenames:
            self.parser.read(filenames)
        self.defauls = defaults
        
    def read(self, filenames):
        """
        Загружает конфигурацию из файла(ов) filenames
        """
        self.parser = ConfigParser()
        self.parser.read(filenames)
    
    def set_defaults(self, defaults):
        """
        Устанавливает параметры проекта по умолчанию
        """
        self.defauls = defaults
        
    def items(self, section):
        """
        Возвращает список кортежей (key, value) из указанной секции.
        В случае, если такой секции нет, то возвращается пустой список.
        """
        return self.parser.items(section) if self.parser.has_section(section) else []
    
    def get(self, section, option):
        """
        Безопастно возвращает значение конфигурационного параметра option
        из раздела section
        """
        try:
            value = self.parser.get(section, option).strip()
            if not value:
                return self.defauls[(section,option)]
            return value
        except:
            if self.defauls.has_key((section,option)):
                return self.defauls[(section,option)]
        return ''
    
    def get_bool(self, section, option):
        """
        Безопастно возвращает булево из конфига
        """
        value = self.get(section, option)
        if isinstance(value, basestring):
            value = value.upper() == 'TRUE'

        return bool(value)

        
    def get_int(self, section, option):
        """
        Безопасно возвращает целое число из конфига
        """
        value = self.get(section, option)
        if isinstance(value, str):
            try:
                value = int(value)
            except:
                value = 0
        return value
        
    def get_uint(self, section, option):
        """
        Безопасно возвращает положительное целое число из конфига
        """
        value = self.get_int(section, option)
        if value < 0:
            value = 0
        return value
    