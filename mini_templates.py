import os
import json


class Tmp:
    def __init__(self):
        try:
            f = open("templates.json")
            self._templates = json.load(f)
        except Exception:
            self._templates = {}
        # print(self._templates)

    def get_templates_from_host_name(self, host_name):
        template = self._templates.get(host_name)
        if template is None:
            return self._get_default_template()
        return template

    @staticmethod
    def _get_default_meta_tags():
        return []

    @staticmethod
    def _get_default_text_tags():
        return ['p', 'h1', 'h2', 'li']

    @staticmethod
    def _get_default_deleted_tags():
        return ['footer']

    def _get_default_template(self):
        return {'meta_tags': self._get_default_meta_tags(),
                'text_tags': self._get_default_text_tags(),
                'delete_tags': self._get_default_deleted_tags()}
