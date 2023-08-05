from datetime import datetime, date
import json
from uuid import uuid4
from arangodb.api import Collection, Client


class ModelField(object):

    is_saved_in_model = True

    class NotNullableFieldException(Exception):
        """
            Field cannot be null
        """

    class WrongInputTypeException(Exception):
        """
            Field cannot be null
        """

    def __init__(self, verbose_name='', help_text='', required=True, blank=False, null=True, default=None, **kwargs):
        """
        """

        self.name = None
        self.verbose_name = verbose_name
        self.help_text = help_text
        self.required = required
        self.blank = blank
        self.null = null
        self.default = default

        self._set_default_attribute(attribute_name='read_only', default_value=False, **kwargs)

        self._model_instance = None

    def dumps(self):
        """
        """

        return None

    def loads(self, string_val):
        """
        """

        pass

    def to_python(self, value):
        """
        """

        return value

    def on_init(self, model_class, attribute_name):
        """
        """

        self.name = attribute_name

    def on_destroy(self, model_class):
        """
        """

        pass

    def on_create(self, model_instance):
        """
        """

        self.model_instance = model_instance

    def on_save(self, model_instance):
        """
        """

        pass

    def validate(self):
        """
        """

        pass

    def set(self, *args, **kwargs):
        """
        """

        pass

    def get(self):
        """
        """

        return self

    def _set_default_attribute(self, attribute_name, default_value, **kwargs):
        """
        """

        if attribute_name in kwargs:
            setattr(self, attribute_name, kwargs[attribute_name])
        else:
            setattr(self, attribute_name, default_value)

    def __eq__(self, other):
        """
        """

        return self.__class__ == other.__class__

    def __unicode__(self):
        """
        """

        return self.dumps()

    def __getattribute__(self, item):
        """
        """

        if item == 'attname':
            return object.__getattribute__(self, 'name')
        elif item == 'rel':
            return None
        else:
            return super(ModelField, self).__getattribute__(item)


class ListField(ModelField):

    def __init__(self, **kwargs):
        """
        """

        super(ListField, self).__init__(**kwargs)

        # If null is allowed, default value is None
        if self.null and self.default is None:
            self.saved_list = None
        else:
            # If default value was set
            if not self.default is None:
                self.saved_list = self.default
            else:
                self.saved_list = []


    def dumps(self):
        """
        """

        json_save_list = []

        # Check if there was set anything
        if isinstance(self.saved_list, (list, tuple)):
            for saved_entry in self.saved_list:
                is_number =  isinstance(saved_entry, int) or isinstance(saved_entry, float)

                # Check if entry is base type
                if isinstance(saved_entry, basestring) or is_number or isinstance(saved_entry, bool):
                    json_save_list.append(saved_entry)
                else:
                    json_save_list.append(self._get_json_save_value(saved_entry))


        return json_save_list

    def _get_json_save_value(self, value):
        """
        """

        if isinstance(value, list) or isinstance(value, tuple):
            return value

        if isinstance(value, dict):
            return value

        else:
            return u'%s' % value

    def loads(self, saved_list):
        """
        """

        self.saved_list = saved_list

    def validate(self):
        """
        """

        if self.saved_list is None and self.null is False:
            raise ListField.NotNullableFieldException()

    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            saved_list = args[0]

            if saved_list is None and self.null is False:
                raise ListField.NotNullableFieldException()

            if isinstance(saved_list, list) or isinstance(saved_list, tuple):
                self.saved_list = saved_list
            elif isinstance(saved_list, basestring):
                self.saved_list = json.loads(saved_list)
            else:
                self.saved_list = args

    def get(self):
        """
        """

        if self.saved_list is None and self.null is False:
            self.saved_list = []

        return self.saved_list

    def __eq__(self, other):
        """
        """

        return super(ListField, self).__eq__(other)

    def __unicode__(self):
        """
        """

        return self.dumps()


class DictField(ModelField):

    def __init__(self, **kwargs):
        """
        """

        super(DictField, self).__init__(**kwargs)

        # If null is allowed, default value is None
        if self.null and self.default is None:
            self.saved_dict = None
        else:
            # If default value was set
            if not self.default is None:
                self.saved_dict = self.default
            else:
                self.saved_dict = {}


    def dumps(self):
        """
        """

        json_save_dict = {}
        for key, saved_entry in self.saved_dict.iteritems():
            is_number =  isinstance(saved_entry, int) or isinstance(saved_entry, float)

            # Check if entry is base type
            if isinstance(saved_entry, basestring) or is_number or isinstance(saved_entry, bool):
                json_save_dict[key] = saved_entry
            else:
                json_save_dict[key] = self._get_json_save_value(saved_entry)


        return json_save_dict

    def _get_json_save_value(self, value):
        """
        """

        if isinstance(value, list) or isinstance(value, tuple):
            return value

        if isinstance(value, dict):
            return value

        else:
            return u'%s' % value

    def loads(self, saved_dict):
        """
        """

        self.saved_dict = saved_dict

    def validate(self):
        """
        """

        if self.saved_dict is None and self.null is False:
            raise DictField.NotNullableFieldException()

    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            saved_dict = args[0]

            if saved_dict is None and self.null is False:
                raise DictField.NotNullableFieldException()

            if isinstance(saved_dict, dict):
                self.saved_dict = saved_dict
            elif isinstance(saved_dict, basestring):
                self.saved_list = json.loads(saved_dict)
            else:
                self.saved_dict = args

    def get(self):
        """
        """

        if self.saved_dict is None and self.null is False:
            self.saved_dict = {}

        return self.saved_dict

    def __eq__(self, other):
        """
        """

        return super(DictField, self).__eq__(other)

    def __unicode__(self):
        """
        """

        return self.dumps()


class BooleanField(ModelField):

    def __init__(self, **kwargs):
        """
        """

        super(BooleanField, self).__init__(**kwargs)

        # If null is allowed, default value is None
        if self.null and self.default is None:
            self.boolean = None
        else:
            # If default value was set
            if not self.default is None:
                self.boolean = self.default
            else:
                self.boolean = False

    def dumps(self):
        """
        """

        return self.boolean

    def loads(self, boolean_val):
        """
        """

        self.boolean = boolean_val

    def validate(self):
        """
        """

        if self.boolean is None and self.null is False:
            raise BooleanField.NotNullableFieldException()

    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            boolean = args[0]

            if isinstance(boolean, bool):
                self.boolean = args[0]
            else:
                raise BooleanField.WrongInputTypeException()

    def get(self):
        """
        """

        return self.boolean

    def __eq__(self, other):
        """
        """

        if super(BooleanField, self).__eq__(other):
            return self.boolean == other.boolean
        else:
            return False


class TextField(ModelField):

    def __init__(self, **kwargs):
        """
        """

        super(TextField, self).__init__(**kwargs)

        # If null is allowed, default value is None
        if self.null and not self.default:
            self.text = None
        else:
            # If default value was set
            if self.default:
                self.text = self.default
            else:
                self.text = u''

    def dumps(self):
        """
        """

        return self.text

    def loads(self, string_val):
        """
        """

        self.text = string_val

    def validate(self):
        """
        """

        if self.text is None and self.null is False:
            raise TextField.NotNullableFieldException()

    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            text = args[0]

            if not text and not self.null:
                raise Exception('Value cannot be None')

            if isinstance(text, basestring):
                self.text = u'%s' % args[0]
            else:
                raise TextField.WrongInputTypeException()

    def get(self):
        """
        """

        return self.text

    def __eq__(self, other):
        """
        """

        if super(TextField, self).__eq__(other):
            return self.text == other.text
        else:
            return False


class CharField(TextField):

    class TooLongStringException(Exception):
        """
        String is too long
        """

    def __init__(self, max_length=255, **kwargs):
        """
        """

        super(CharField, self).__init__(**kwargs)

        self.max_length = max_length

    def validate(self):
        """
        """

        super(CharField, self).validate()

        if self.text:
            if len(self.text) > self.max_length:
                raise CharField.TooLongStringException()

    def __getattribute__(self, item):
        """
        """

        if item == 'flatchoices':
            return None
        else:
            return super(CharField, self).__getattribute__(item)


class UuidField(CharField):

    def __init__(self, auto_create=True, **kwargs):
        """
        """

        super(UuidField, self).__init__(**kwargs)

        self.auto_create = auto_create

    def on_create(self, model_instance):
        """
        """

        if self.auto_create and self.text is None or self.text == '':
            self.text = str(uuid4())


class ChoiceField(ModelField):
    """
    """

    def __init__(self, choices, multiple=False, **kwargs):
        """
        """

        super(ChoiceField, self).__init__(**kwargs)

        self.choices = choices

        # If null is allowed, default value is None
        if self.null and not self.default:
            self.choice_value = None
        else:
            # If default value was set
            if self.default:
                self.choice_value = self.default
            else:
                self.choice_value = u''

    def dumps(self):
        """
        """

        return self.choice_value

    def loads(self, string_val):
        """
        """

        self.choice_value = string_val

    def validate(self):
        """
        """

        has_match = False

        for choice_pair in self.choices:
            if choice_pair[0] == self.choice_value:
                has_match = True
                break

        if not has_match:
            raise ChoiceField.WrongInputTypeException()

        if self.choice_value is None and self.null is False:
            raise ChoiceField.NotNullableFieldException()

    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            choice_value = args[0]
            self.choice_value = choice_value

            self.validate()

    def get(self):
        """
        """

        return self.choice_value

    def __eq__(self, other):
        """
        """

        if super(ChoiceField, self).__eq__(other):
            return self.choice_value == other.choice_value
        else:
            return False

    def __getattribute__(self, item):
        """
        """

        if item == 'flatchoices':
            return object.__getattribute__(self, 'choices')
        else:
            return super(ChoiceField, self).__getattribute__(item)


class NumberField(ModelField):

    def __init__(self, **kwargs):
        """
        """

        super(NumberField, self).__init__(**kwargs)


        # If null is allowed, default value is None
        if self.null and not self.default:
            self.number = None
        else:
            # If default value was set
            if self.default:
                self.number = self.default
            else:
                self.number = 0

    def dumps(self):
        """
        """

        return self.number

    def loads(self, number_val):
        """
        """

        self.number = number_val

    def validate(self):
        """
        """

        if self.number is None and self.null is False:
            raise NumberField.NotNullableFieldException()

    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            number = args[0]

            if isinstance(number, int) or isinstance(number, float):
                self.number = args[0]
            else:
                raise NumberField.WrongInputTypeException

    def get(self):
        """
        """

        return self.number

    def __eq__(self, other):
        """
        """

        if super(NumberField, self).__eq__(other):
            return self.number == other.number
        else:
            return False


class DatetimeField(ModelField):

    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, **kwargs):
        """
        """

        super(DatetimeField, self).__init__(**kwargs)

        if self.null and not self.default:
            self.time = None
        else:
            if self.default:
                self.time = self.default
            else:
                self.time = datetime.now()

    def dumps(self):
        """
        """

        if self.null and self.time is None:
            return None
        else:
            if self.time is None:
                raise Exception('Datetime cannot be None')
            else:
                return u'%s' % self.time.strftime(DatetimeField.DATE_FORMAT)

    def loads(self, date_string):
        """
        """

        if not self.null:
            self.time = datetime.strptime(date_string, DatetimeField.DATE_FORMAT)
        else:
            self.time = None

    def validate(self):
        """
        """

    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            time = args[0]
            if isinstance(args, basestring):
                self.loads(time)
            else:
                self.time = time

    def get(self):
        """
        """

        return self.time

    def __eq__(self, other):
        """
        """

        if super(DatetimeField, self).__eq__(other):
            return self.time == other.time
        else:
            return False


class DateField(ModelField):

    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, **kwargs):
        """
        """

        super(DateField, self).__init__(**kwargs)

        if self.null and not self.default:
            self.date = None
        else:
            if self.default:
                self.date = self.default
            else:
                self.date = date.today()

    def dumps(self):
        """
        """

        if self.null and self.date is None:
            return None
        else:
            if self.date is None:
                raise Exception('Datetime cannot be None')
            else:
                return u'%s' % self.date.strftime(DateField.DATE_FORMAT)

    def loads(self, date_string):
        """
        """

        if not self.null:
            self.date = datetime.strptime(date_string, DateField.DATE_FORMAT)
        else:
            self.date = None

    def validate(self):
        """
        """

    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            date = args[0]
            if isinstance(args, basestring):
                self.loads(date)
            else:
                self.date = date

    def get(self):
        """
        """

        return self.date

    def __eq__(self, other):
        """
        """

        if super(DateField, self).__eq__(other):
            return self.date == other.date
        else:
            return False


class ForeignKeyField(ModelField):

    def __init__(self, to, related_name=None, **kwargs):
        """
        """

        super(ForeignKeyField, self).__init__(**kwargs)

        # If null is allowed, default value is None
        if self.null and not self.default:
            self.relation_model = None
        else:
            # If default value was set
            if self.default:
                self.relation_model = self.default
            else:
                self.relation_model = ''

        self.relation_class = to
        self.related_name = related_name

        if 'other_side' in kwargs:
            self.other_side = True
            self.other_attribute_name = kwargs['other_side']
        else:
            self.other_side = False

    def on_init(self, model_class, attribute_name):
        """
        """

        super(ForeignKeyField, self).on_init(model_class=model_class, attribute_name=attribute_name)

        # Set this only if there is a related name
        if self.related_name:
            fields = self.relation_class._model_meta_data._fields
            # Create field on other side
            otherside_field = ForeignKeyField(to=model_class, other_side=attribute_name, read_only=True)
            fields[self.related_name] = otherside_field

    def dumps(self):
        """
        """

        if self.relation_model:
            return u'%s' % self.relation_model.document
        else:
            return None

    def loads(self, model_id):
        """
        """

        if isinstance(model_id, basestring):
            model = self.relation_class.objects.get(_id=model_id)
        elif isinstance(model_id, self.relation_class):
            model = model_id
        else:
            raise ForeignKeyField.WrongInputTypeException()

        self.relation_model = model

    def validate(self):
        """
        """

        if self.relation_model is None and self.null is False:
            raise ForeignKeyField.NotNullableFieldException()

        if self.relation_model:
            pass

    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            relation_model = args[0]
            self.relation_model = relation_model

    def get(self):
        """
        """

        if self.other_side:
            kwargs = { self.other_attribute_name: self.model_instance.document.id }
            return self.relation_class.objects.filter(**kwargs)
        else:
            return self.relation_model

    def __eq__(self, other):
        """
        """

        if super(ForeignKeyField, self).__eq__(other):
            return self.relation_model == other.relation_model
        else:
            return False


class ManyToManyField(ModelField):

    is_saved_in_model = False

    def __init__(self, to, related_name, **kwargs):
        """
        """

        super(ManyToManyField, self).__init__(**kwargs)

        self.relation_class = to
        self.related_name = related_name
        self.relation_collection = None

        # Data
        self.unsaved_data = False
        self.related_queryset = None

    def on_init(self, model_class, attribute_name):
        """
        """

        super(ManyToManyField, self).on_init(model_class=model_class, attribute_name=attribute_name)

        if not self.related_name is None:
            relation_name = self._get_relation_collection_name(model_class)

            try:
                self.relation_collection = Collection.create(name=relation_name, database=Client.instance().database, type=3)
            except:
                self.relation_collection = Collection.get_loaded_collection(name=relation_name)

            fields = self.relation_class._model_meta_data._fields
            otherside_field = ManyToManyField(to=model_class, related_name=None)
            fields[self.related_name] = otherside_field

            # Configure other side field
            otherside_field.related_queryset = self.relation_class.objects.all()
            otherside_field.relation_collection = self.relation_collection

            self.related_queryset = self.relation_class.objects.all()

    def on_destroy(self, model_class):
        """
        """

        if not self.related_name is None:
            relation_name = self._get_relation_collection_name(model_class)
            Collection.remove(name=relation_name)

    def on_save(self, model_instance):
        """
        """

        if self.unsaved_data:
            new_models = self.related_queryset._cache

            # We don't want to have problems
            if not new_models:
                return

            for model in new_models:
                related_model_document = model.document
                model_document = model_instance.document

                # Create relation
                self.relation_collection.create_edge(from_doc=model_document, to_doc=related_model_document)

    def _get_relation_collection_name(self, model_class):
        """
        """

        return 'relation_%s_%s' % ( model_class.get_collection_name(), self.relation_class.get_collection_name() )

    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            related_models = args[0]
            self.related_queryset._cache = related_models
            self.unsaved_data = True

    def get(self):
        """
        """

        if self.unsaved_data is True:
            return self.related_queryset
        else:

            if self.related_name is None:
                return self.related_queryset.get_field_relations(
                    end_model=self.model_instance,
                    relation_collection=self.relation_collection.name,
                    related_model_class=self.relation_class
                )
            else:
                return self.related_queryset.get_field_relations(
                    start_model=self.model_instance,
                    relation_collection=self.relation_collection.name,
                    related_model_class=self.relation_class
                )

    def loads(self, model_list):
        """
        """

        self.set(model_list)

    def __eq__(self, other):
        """
        """

        if super(ManyToManyField, self).__eq__(other):
            return self.related_queryset == other.related_queryset
        else:
            return False