import tg
from tg.caching import cached_property
from formencode import FancyValidator

try:
    from tgext.datahelpers.validators import SQLAEntityConverter
except ImportError:
    pass

try:
    from tgext.datahelpers.validators import MingEntityConverter
except ImportError:
    pass


class ModelEntityConverter(FancyValidator):
    def __init__(self, klass, slugified=False):
        super(FancyValidator, self).__init__(not_empty=True)
        self.model_name = klass
        self.slugified = slugified

    @cached_property
    def _converter(self):
        from turbopress import model
        if tg.config.get('use_sqlalchemy', False):
            return SQLAEntityConverter(getattr(model, self.model_name),
                                       session=model.DBSession,
                                       slugified=self.slugified)
        elif tg.config.get('use_ming', False):
            return MingEntityConverter(getattr(model, self.model_name),
                                       slugified=self.slugified)
        else:
            raise ValueError('Turbopress should be used with sqlalchemy or ming')

    def _convert_to_python(self, value, state):
        return self._converter._to_python(value, state)

    def _convert_from_python(self, value, state):
        return self._converter._from_python(value, state)

    def _validate_python(self, value, state):
        return self._converter.validate_python(value, state)

    _to_python = _convert_to_python
    _from_python = _convert_from_python
    validate_python = _validate_python


try:
    from ming.odm.odmsession import ODMCursor as MingCursor
except ImportError:
    class MingCursor(object):
        pass

try:
    from tg.support.paginate import _MingQueryWrapper
    tg_supports_ming_pagination = True
except ImportError:
    tg_supports_ming_pagination = False
    class _MingQueryWrapper(object):
        def __init__(self, obj):
            self.obj = obj

        def __getitem__(self, range):
            return self.obj.skip(range.start).limit(range.stop-range.start)

        def __len__(self):
            return self.obj.count()


def make_paginable(query):
    if not tg_supports_ming_pagination and isinstance(query, MingCursor):
        return _MingQueryWrapper(query)
    return query