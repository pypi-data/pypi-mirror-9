from anyblok.blok import Blok
from anyblok_pyramid.release import version


class Pyramid(Blok):
    version = version

    required = [
        'anyblok-core',
    ]

    @classmethod
    def import_declaration_module(cls):
        from . import base  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import base
        reload(base)
