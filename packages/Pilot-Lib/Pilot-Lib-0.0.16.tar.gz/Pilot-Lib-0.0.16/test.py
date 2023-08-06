
d = {
    "ENABLE": True,
    "FACEBOOK": {
        "ENABLE": True,
        "CLIENT_ID": "FB-1"
    },
    "GOOGLE": {
        "ENABLE": False,
        "CLIENT_ID": "G+"
    }
}

credentials = {}
for name, prop in d.items():
    if isinstance(prop, dict):
        if prop["ENABLE"]:
            _name = name.lower()
            credentials[_name] = prop["CLIENT_ID"]
print credentials
exit()

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