# -*- coding: utf-8 -*-
from django_fabric.base import App


class UwsgiApp(App):
    ini_files = {}

    def __init__(self, ini_files=None, *args, **kwargs):
        super(UwsgiApp, self).__init__(*args, **kwargs)
        self.ini_files = ini_files or self.ini_files

    def restart_app(self, instance):
        self.run('sudo touch %s' % self.ini_files[instance])
