__author__ = 'mardochee.macxis'

class classproperty(property):
    """
    Just like @property, @classproperty let you do the same on class level
    """
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class PilotViewDecoratorsMixin(object):
    @classproperty
    def decorators(cls):
        return "Boom"


class UserMixin(PilotViewDecoratorsMixin):
    _decorators = ["C", "D"]
    pass

class AdminMixin(PilotViewDecoratorsMixin):
    _decorators = ["A", "B"]
    pass


class View(UserMixin, AdminMixin):
    pass


print View.decorators