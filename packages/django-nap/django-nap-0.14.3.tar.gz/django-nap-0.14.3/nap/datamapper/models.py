
from django.db.models.fields import NOT_PROVIDED
from django.utils.six import with_metaclass

from . import filters
from .fields import Field
from .mappers import DataMapper


# Map of ModelField name -> list of filters
FIELD_FILTERS = {
    'DateField': [filters.DateFilter],
    'TimeField': [filters.TimeFilter],
    'DateTimeField': [filters.DateTimeFilter],

    'BooleanField': [filters.BooleanFilter],
    'IntegerField': [filters.IntegerFilter],
}


class Options(object):
    def __init__(self, meta):
        self.model = getattr(meta, 'model', None)
        self.fields = getattr(meta, 'fields', [])
        self.exclude = getattr(meta, 'exclude', [])
        self.required = getattr(meta, 'required', {})


class MetaMapper(type):

    def __new__(mcs, name, bases, attrs):
        meta = Options(attrs.get('Meta', None))

        if meta.model is None:
            if name != 'ModelDataMapper':
                raise ValueError('model not defined on class Meta')
        else:
            # XXX Does the top base have all fields?

            for model_field in meta.model._meta.fields:
                if model_field.name in attrs:
                    continue
                if model_field.name in meta.exclude:
                    continue
                if meta.fields != '__all__' and \
                   model_field.name not in meta.fields:
                    continue

                # XXX Magic for field types
                kwargs = {}
                if model_field.null is True and model_field.default is NOT_PROVIDED:
                    kwargs['default'] = None
                else:
                    kwargs['default'] = model_field.default
                kwargs['required'] = meta.required.get(
                    model_field.name,
                    not model_field.blank,
                )
                kwargs['filters'] = FIELD_FILTERS.get(
                    model_field.__class__.__name__,
                    []
                )[:]
                if not model_field.null:
                    kwargs['filters'].insert(0, filters.NotNullFilter)
                attrs[model_field.name] = Field(model_field.name, **kwargs)

        attrs['_meta'] = meta

        return super(MetaMapper, mcs).__new__(mcs, name, bases, attrs)


class ModelDataMapper(with_metaclass(MetaMapper, DataMapper)):
    pass
