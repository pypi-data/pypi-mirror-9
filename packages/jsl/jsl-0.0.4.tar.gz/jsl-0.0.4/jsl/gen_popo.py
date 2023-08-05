import inspect
import zzz


def get_classes(module):
    def accept(member):
        return inspect.isclass(member) and module.__name__ == member.__module__
    return inspect.getmembers(zzz, accept)


print get_classes(zzz)


def get_pycharm_type_hint(name, field):
    return ":param {0} {1}:".format(name, "str")