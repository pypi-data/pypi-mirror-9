# -*- coding: utf-8 -*-

def __patch_unicode():
    import django.db.models
    from .utils import default_repr
    setattr(django.db.models.Model, '__unicode__', default_repr)

__patch_unicode()
