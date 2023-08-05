"""
A very light-weight "model" structure to lazy-load (or generate) and save YAML
from Python objects composed of specialized fields
"""

import collections
import os

from contextlib import contextmanager

from yaml import safe_load as yaml_load, dump as yaml_dump


immutable_types = (int, float, str, tuple, None.__class__)


class ValidationError(Exception):
    """
    Raised when model validation failed in some way
    """
    def __init__(self, messages):
        if not isinstance(messages, (tuple, list)):
            messages = [messages]

        self.messages = tuple(messages)

        super(ValidationError, self).__init__("\n".join(self.messages))

    def __add__(self, other):
        if isinstance(other, ValidationError):
            return ValidationError(self.messages + other.messages)

        return super(ValidationError, self).__add__(other)


class NoValueError(Exception):
    """
    Raised when a field has no value, no generator and no default
    """
    def __init__(self, cls, var_name, *args):
        super(NoValueError, self).__init__(*args)
        self.cls = cls
        self.var_name = var_name

    def __str__(self):
        return "No value for field '%s'" % self.var_name


class TransientValueError(Exception):
    """
    Raised to signal that a returned value may not be final, so shouldn't be
    cached, or saved automatically
    """
    def __init__(self, value):
        self.value = value


def hash_value(value):
    """
    Provide a hash for comparing value (in)equality
    """
    try:
        return hash(value)

    except TypeError:
        return hash(value.__repr__())


class OnAccess(object):  # pylint:disable=too-few-public-methods
    """
    Mark a field as having a one-time call associated with it's retrieval
    """
    var_name = None
    func = None

    def __init__(self, func, input_transform=None, output_transform=None):
        self.func = func
        self.input_transform = input_transform
        self.output_transform = output_transform

    def process_generate_default(self, self_, generate, default):
        """
        Process the generate/default values to get a value
        """
        if generate is not None:
            # TODO generated values aren't marked dirty
            return self.process_value_generator(self_, generate)

        elif default is not None:
            raise TransientValueError(
                self.process_value_generator(self_, default)
            )

        else:
            raise NoValueError(self_.__class__, self.var_name)

    def process_value_generator(self, self_, gen_value):
        """
        Process a generate/default argument for a value
        """
        return gen_value(self_) if callable(gen_value) else gen_value

    def modify_class(self):
        """
        Generate a property to put in place of this object instance on the
        concrete model object
        """
        def getter(self_):
            """
            Getter for the attribute value that checks for a cached value
            before trying to generate/acquire it
            """
            # pylint:disable=protected-access
            try:
                value = self_._dirty_vals[self.var_name]

            except KeyError:
                try:
                    value = self_._lazy_vals[self.var_name]

                except KeyError:
                    try:
                        self_._lazy_vals[self.var_name] = self.func(self_)
                        self_.recheck_dirty(self.var_name)
                        value = self_._lazy_vals[self.var_name]

                    except TransientValueError as ex:
                        value = ex.value

            if self.output_transform:
                return self.output_transform(value)

            else:
                return value

        def setter(self_, value):
            """
            Basic setter to write the value to the cache dict
            """
            if self.input_transform:
                value = self.input_transform(value)

            # pylint:disable=protected-access
            self_._dirty_vals[self.var_name] = value

        f_attrs = self.future_cls[2]
        f_attrs[self.var_name] = property(getter, setter)


class LoadOnAccess(OnAccess):  # pylint:disable=too-few-public-methods
    """
    Mark a field as being lazy loaded with the _load method of the model
    class
    """
    def __init__(self, default=None, generate=None, *args, **kwargs):
        def loader(self_):
            """
            Loader function to load the model and return the requested
            attribute value if possible. Fall back to default/generated values
            """
            try:
                self_.load()
                # pylint:disable=protected-access
                return self_._lazy_vals[self.var_name]

            except (FileNotFoundError, KeyError):
                return self.process_generate_default(self_, generate, default)

        super(LoadOnAccess, self).__init__(loader, *args, **kwargs)

    def modify_class(self):
        # pylint:disable=no-member
        super(LoadOnAccess, self).modify_class()
        f_attrs = self.future_cls[2]
        lst = f_attrs.setdefault('_load_on_access', [])
        lst.append(self.var_name)


#class ModelReference(OnAccess):
#    """
#    A model reference field that adds both a model field, and a _slug field
#    that reference each other
#    """
#    def __init__(self,
#                 builder_func,
#                 stored=True,
#                 default=None,
#                 *args,
#                 **kwargs):
#        self.builder_func = builder_func
#        self.stored = stored
#        self.default = default
#
#        super(ModelReference, self).__init__(
#            self.model_builder, *args, **kwargs
#        )
#
#    @property
#    def model_builder(self):
#        """
#        Get a safe builder func that gets a model from a slug
#        """
#        def deferred_wrapper(*args, **kwargs):
#            """
#            Defer calling the wrapper until this object has been correctly
#            initialized
#            """
#            return self.wrapped_builder_for(
#                '%s_slug' % self.var_name,
#                self.builder_func,
#            )(*args, **kwargs)
#
#        return deferred_wrapper
#
#    @property
#    def slug_builder(self):
#        """
#        Get a safe builder func that gets a slug from a model
#        """
#        return self.wrapped_builder_for(
#            self.var_name,
#            lambda self_: getattr(self_, self.var_name).slug,
#        )
#
#    def wrapped_builder_for(self, var_name, inner_builder):
#        """
#        Decorator (sort of) to wrap a builder in a TransientValueError guard
#        """
#        def outer_builder(self_):
#            """
#            Wrap the inner_builder in a has_value guard and TransientValueError
#            """
#            if not self_.has_value(var_name):
#                raise TransientValueError(
#                    self.default(self_)
#                    if callable(self.default)
#                    else self.default
#                )
#
#            return inner_builder(self_)
#
#        return outer_builder
#
#    def modify_class(self):
#        super(ModelReference, self).modify_class()
#
#        if self.stored:
#            slug_field = LoadOnAccess(generate=self.slug_builder)
#
#        else:
#            slug_field = OnAccess(self.slug_builder)
#
#        slug_field.var_name = "%s_slug" % self.var_name
#        slug_field.future_cls = self.future_cls
#        slug_field.modify_class()


class ModelReference(OnAccess):
    """
    A model reference field that adds both a model field, and a _slug field
    that reference each other
    """
    def __init__(self,
                 builder_func,
                 stored=True,
                 default=None,
                 generate=None,
                 *args,
                 **kwargs):
        self.builder_func = builder_func
        self.stored = stored
        self.default = default

        super(ModelReference, self).__init__(
            self.model_builder, *args, **kwargs
        )

    @property
    def slug_var_name(self):
        """
        The name of the slug property for this model field
        """
        return "%s_slug" % self.var_name

    def process_value_generator(gen_value):
        """
        Process a generate/default argument for a slug value
        """
        is_model = isinstance(gen_value, Model)

        # Get value from callable, unless it's a Model instance
        if not is_model and callable(gen_value):
            value = gen_value(self_)
        else:
            value = gen_value

        if is_model:
            return value.slug

        return value

    def slug_builder(self, self_):
        """
        Builder to get the slug from the model object
        """
        if self_.has_value(self.var_name):
            return getattr(self_, self.var_name).slug

        return self.process_generate_default(self_,
                                             self.generate,
                                             self.default)

    def model_builder(self, self_, slug=None):
        """
        Builder to create a model object from the associated slug
        """
        try:
            return self.builder_func(self_)

        except NoValueError:
            raise NoValueError(self_.__class__, self.var_name)

    def modify_class(self):
        super(ModelReference, self).modify_class()

        if self.stored:
            slug_field = LoadOnAccess(generate=self.slug_builder)

        else:
            slug_field = OnAccess(self.slug_builder)

        slug_field.var_name = self.slug_var_name
        slug_field.future_cls = self.future_cls
        slug_field.modify_class()


class ModelMeta(type):
    """
    Metaclass for replacing OnAccess and child classes in fields with their
    associated caching behaviour
    """
    def __new__(mcs, f_clsname, f_bases, f_attrs):
        f_cls = (f_clsname, f_bases, f_attrs)
        for name, val in list(f_attrs.items()):
            if isinstance(val, OnAccess):
                val.var_name = name
                val.future_cls = f_cls
                val.modify_class()

        return super(ModelMeta, mcs).__new__(mcs, f_clsname, f_bases, f_attrs)


# pylint:disable=abstract-class-little-used
class Model(object, metaclass=ModelMeta):
    """
    A model-like base for the YAML data store
    """
    @property
    def slug(self):
        """
        Unique string to identify this instance of the model (like a primary
        key)
        """
        raise NotImplementedError("You must override the 'slug' property")

    def __init__(self):
        self._lazy_vals = {}
        self._lazy_vals_hashes = {}
        self._dirty_vals = {}

    @classmethod
    def data_name(cls):
        """
        Get the data name associated with this model type
        """
        return '%ss' % cls.__name__.lower()

    @classmethod
    def data_dir_path(cls):
        """
        Path parts used to create the data directory
        """
        return ['data', cls.data_name()]

    def recheck_dirty(self, fields=None):
        """
        Force the dirty values list to be updated, based on hashes. This takes
        into account in-place modification of objects
        """
        if fields is None:
            fields = self._lazy_vals.keys()

        elif isinstance(fields, str):
            fields = (fields,)

        for var_name in fields:
            try:
                value = self._lazy_vals[var_name]

            except KeyError:
                continue

            if value.__class__ in immutable_types:
                continue

            new_hash = hash_value(value)

            if var_name in self._lazy_vals_hashes:
                if  new_hash != self._lazy_vals_hashes[var_name]:
                    self._dirty_vals[var_name] = value
                    del self._lazy_vals[var_name]

            else:
                self._lazy_vals_hashes[var_name] = new_hash

    def has_value(self, var_name):
        """
        Check if there's a value for the given property
        """
        return var_name in self._lazy_vals or \
               var_name in self._dirty_vals

    def is_dirty(self, var_name, recheck=True):
        """
        Check if the given property is dirty or not. If the value is mutable, a
        recheck may be necessary to get the correct response
        """
        if recheck:
            self.recheck_dirty(var_name)

        return var_name in self._dirty_vals

    def data_file_path(self):
        """
        Path parts used to create the data filename
        """
        return self.__class__.data_dir_path() + ['%s.yaml' % self.slug]

    def exists(self, data_file=None):
        """
        Check to see if the model file exists (if not, maybe it's new)
        """
        if data_file is None:
            data_file_path = self.data_file_path()
            data_file = os.path.join(*data_file_path)

        return os.path.isfile(data_file)

    def load(self, data_file=None, recheck_dirty=True):
        """
        Fill the object from the job file
        """
        if data_file is None:
            data_file = os.path.join(*self.data_file_path())

        with open(data_file) as handle:
            data = yaml_load(handle)
            self.from_dict(data, dirty=False)

        if recheck_dirty:
            self.recheck_dirty()

    def save(self,
             data_file=None,
             force=False,
             reload=True,
             reload_recheck_dirty=True):
        """
        Save the job data
        """
        if not force:  # if forced, validation is unnecessary
            self.validate()

        if reload and self.exists(data_file):
            self.load(data_file=data_file, recheck_dirty=reload_recheck_dirty)

        if data_file is None:
            data_file_path = self.data_file_path()
            data_file = os.path.join(*data_file_path)

            # Make the dir first
            os.makedirs(os.path.join(*data_file_path[0:-1]), exist_ok=True)

        yaml_data = self.as_yaml()
        with open(data_file, 'w') as handle:
            handle.write(yaml_data)

        # Update the lazy vals and rehash
        self._lazy_vals.update(self._dirty_vals)
        self.recheck_dirty(self._dirty_vals.keys())
        self._dirty_vals.clear()

    def validate(self):
        """
        Validate the model fields to make sure they are sane. Raises
        ValidationError on failure
        """
        if not self.slug:
            raise ValidationError('Slug can not be blank')

        return True

    @contextmanager
    def parent_validation(self, klass):
        """
        Context manager to wrap validation with parent validation and combine
        ValidationError messages
        """
        errors = []
        for validate in (super(klass, self).validate, None):
            try:
                if validate:
                    validate()

                else:
                    yield errors

            except ValidationError as ex:
                errors += list(ex.messages)

        if errors:
            raise ValidationError(errors)

    def from_yaml(self, data, dirty=True):
        """
        Deserialize from YAML
        """
        return self.from_dict(yaml_load(data), dirty)

    def as_yaml(self):
        """
        Serialize to YAML
        """
        return yaml_dump(self.as_dict(), default_flow_style=False)

    def from_dict(self, data, dirty=True):
        """
        Deserialize from dict
        """
        if not data:
            return

        if not hasattr(self, '_load_on_access'):
            return

        vals_dict = self._dirty_vals if dirty else self._lazy_vals
        for var_name in self._load_on_access:  # pylint:disable=no-member
            if var_name in data:
                vals_dict[var_name] = data[var_name]

        self.recheck_dirty()

    def as_dict(self):
        """
        Serialize to dict
        """
        data = {}
        if hasattr(self, '_load_on_access'):
            for var_name in self._load_on_access:  # pylint:disable=no-member
                try:
                    value = getattr(self, var_name)
                    if self.has_value(var_name):
                        data[var_name] = value

                except NoValueError:
                    pass

        return data


class SingletonModel(Model):
    """
    Model with just 1 instance
    """
    @property
    def slug(self):
        """
        Auto generate a slug for this model matching it's model data_name
        """
        return self.__class__.data_name()

    @classmethod
    def data_dir_path(cls):
        return ['data']
