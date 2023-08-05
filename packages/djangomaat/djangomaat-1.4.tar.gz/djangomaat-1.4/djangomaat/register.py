from __future__ import unicode_literals

from django.db.models.base import ModelBase
try:
    from django.contrib.contenttypes.fields import GenericRelation
except ImportError:
    # Django < 1.7
    from django.contrib.contenttypes.generic import GenericRelation


from .exceptions import ModelNotRegistered, ModelAlreadyRegistered
from .models import MaatRanking

def get_handler_instance(model, handler_class, options):
    """ Returns an handler instance for the given *model*. """
    handler = handler_class(model)
    for key, value in options.items():
        setattr(handler, key, value)
    return handler

def contribute_to_class(model, related_name=None):
    """
    Adds a 'maat_ranking' attribute to each instance of model.
    The attribute is a generic relation to MaatRanking, used by the
    handler to retrieve the ordered queryset.
    """
    try:
        generic_relation = GenericRelation(MaatRanking, related_query_name=related_name)
    except TypeError:
        # Django < 1.7
        generic_relation = GenericRelation(MaatRanking, related_name=related_name)
    generic_relation.contribute_to_class(model, 'maat_ranking')


class MaatRegister(object):
    """
    Register class.
    """
    def __init__(self):
        self._registry = {}

    def get_handler_for_model(self, model):
        """
        Returns an handler for the given *model*. If the model has not been
        registered, it raises a *ModelNotRegistered* exception.
        """
        try:
            return self._registry[model]
        except KeyError:
            raise ModelNotRegistered('Model {} is not handled'.format(model))

    def get_registered_handlers(self):
        """ Returns a list of all the registered handlers. """
        return list(self._registry.values())

    def register(self, model_or_iterable, handler_class, **kwargs):
        """
        Registers a model or a list of models to be handled by *handler_class*.
        Once registered, a model gains a new attribute *maat* which can be
        used to retrieve an ordered queryset.

        Eg:

            from djangomaat.register import maat

            maat.register(Article, ArticleMaatHandler)

            ordered_article_list = Article.maat.ordered_by('popularity')

        Plus, the management command `populate_maat_ranking` will
        automatically process the model.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model in self._registry:
                try:
                    model_name = model._meta.model_name
                except AttributeError:
                    # Django < 1.6
                    model_name = model._meta.module_name
                raise ModelAlreadyRegistered(
                    "The model {} is already registered.".format(model_name))
            handler = get_handler_instance(model, handler_class, kwargs)
            self._registry[model] = handler
            contribute_to_class(model, handler.related_name)

    def unregister(self, model_or_iterable):
        """ Do not use it. Just for testing, really. """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model in self._registry:
                del self._registry[model]

maat = MaatRegister()
