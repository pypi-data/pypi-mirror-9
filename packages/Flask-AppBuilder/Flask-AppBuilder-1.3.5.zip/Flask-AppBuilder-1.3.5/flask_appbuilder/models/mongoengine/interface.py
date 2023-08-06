import logging, sys
from flask import flash
from . import filters
from ..._compat import as_unicode
from ..base import BaseInterface
from mongoengine.fields import StringField, IntField, BooleanField, FloatField, \
    DateTimeField, ReferenceField, ListField, FileField, ImageField

log = logging.getLogger(__name__)


def _include_filters(obj):
    for key in filters.__all__:
        if not hasattr(obj, key):
            setattr(obj, key, getattr(filters, key))


class MongoEngineInterface(BaseInterface):

    filter_converter_class = filters.MongoEngineFilterConverter

    def __init__(self, obj, session=None):
        self.session = session
        _include_filters(self)
        super(MongoEngineInterface, self).__init__(obj)

    @property
    def model_name(self):
        """
            Returns the models class name
            useful for auto title on views
        """
        return self.obj.__name__

    def query(self, filters=None, order_column='', order_direction='',
              page=None, page_size=None):

        if filters:
            objs = filters.apply_all(self.obj.objects)
        else:
            objs = self.obj.objects
        count = len(objs)
        start, stop = 0, count
        if page:
            start = page * page_size
        if page_size:
            stop = start + page_size
        if order_column != '':
            if order_direction == 'asc':
                objs = objs.order_by('-{0}'.format(order_column))
            else:
                objs = objs.order_by('+{0}'.format(order_column))
        return count, objs[start:stop]

    def is_string(self, col_name):
        try:
            return isinstance(self.obj._fields[col_name], StringField)
        except:
            return False

    def is_integer(self, col_name):
        try:
            return isinstance(self.obj._fields[col_name], IntField)
        except:
            return False

    def is_float(self, col_name):
        try:
            return isinstance(self.obj._fields[col_name], FloatField)
        except:
            return False

    def is_boolean(self, col_name):
        try:
            return isinstance(self.obj._fields[col_name], BooleanField)
        except:
            return False

    def is_datetime(self, col_name):
        try:
            return isinstance(self.obj._fields[col_name], DateTimeField)
        except:
            return False

    def is_gridfs_file(self, col_name):
        try:
            return isinstance(self.obj._fields[col_name], FileField)
        except:
            return False

    def is_gridfs_image(self, col_name):
        try:
            return isinstance(self.obj._fields[col_name], ImageField)
        except:
            return False

    def is_relation(self, col_name):
        try:
            return isinstance(self.obj._fields[col_name], ReferenceField) or \
                    isinstance(self.obj._fields[col_name], ListField)
        except:
            return False

    def is_relation_many_to_one(self, col_name):
        try:
            return isinstance(self.obj._fields[col_name], ReferenceField)
        except:
            return False

    def is_relation_many_to_many(self, col_name):
        try:
            field = self.obj._fields[col_name]
            return isinstance(field, ListField) and isinstance(field.field, ReferenceField)
        except:
            return False

    def is_relation_one_to_one(self, col_name):
        return False

    def is_relation_one_to_many(self, col_name):
        return False

    def is_nullable(self, col_name):
        return not self.obj._fields[col_name].required

    def is_unique(self, col_name):
        return self.obj._fields[col_name].unique

    def is_pk(self, col_name):
        return col_name == 'id'

    def get_max_length(self, col_name):
        try:
            col = self.obj._fields[col_name]
            if col.max_length:
                return col.max_length
            else:
                return -1
        except:
                return -1

    def get_min_length(self, col_name):
        try:
            col = self.obj._fields[col_name]
            if col.min_length:
                return col.min_length
            else:
                return -1
        except:
                return -1

    def add(self, item):
        try:
            item.save()
            self.message = (as_unicode(self.add_row_message), 'success')
            return True
        except Exception as e:
            self.message = (as_unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Add record error: {0}".format(str(e)))
            return False

    def edit(self, item):
        try:
            item.save()
            self.message = (as_unicode(self.edit_row_message), 'success')
            return True
        except Exception as e:
            self.message = (as_unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Edit record error: {0}".format(str(e)))
            return False

    def delete(self, item):
        try:
            item.delete()
            self.message = (as_unicode(self.delete_row_message), 'success')
            return True
        except Exception as e:
            self.message = (as_unicode(self.general_error_message + ' ' + str(sys.exc_info()[0])), 'danger')
            log.exception("Delete record error: {0}".format(str(e)))
            return False

    def get_columns_list(self):
        return self.obj._fields.keys()

    def get_search_columns_list(self):
        ret_lst = list()
        for col_name in self.get_columns_list():
            for conversion in self.filter_converter_class.conversion_table:
                if getattr(self, conversion[0])(col_name):
                    ret_lst.append(col_name)
        return ret_lst

    def get_user_columns_list(self):
        """
            Returns all model's columns except pk
        """
        return [col_name for col_name in self.get_columns_list() if not self.is_pk(col_name)]

    def get_order_columns_list(self, list_columns=None):
        """
            Returns the columns that can be ordered

            :param list_columns: optional list of columns name, if provided will
                use this list only.
        """
        ret_lst = list()
        list_columns = list_columns or self.get_columns_list()
        for col_name in list_columns:
            if hasattr(self.obj, col_name):
                if not hasattr(getattr(self.obj, col_name), '__call__'):
                    ret_lst.append(col_name)
            else:
                ret_lst.append(col_name)
        return ret_lst

    def get_related_model(self, col_name):
        field = self.obj._fields[col_name]
        if isinstance(field, ListField):
            return field.field.document_type
        else:
            return field.document_type

    def get_related_interface(self, col_name):
        return self.__class__(self.get_related_model(col_name))

    def get_related_obj(self, col_name, value):
        rel_model = self.get_related_model(col_name)
        return rel_model.objects(pk=value)[0]

    def get_keys(self, lst):
        """
            return a list of pk values from object list
        """
        pk_name = self.get_pk_name()
        return [getattr(item, pk_name) for item in lst]

    def get_related_fk(self, model):
        for col_name in self.get_columns_list():
            if self.is_relation(col_name):
                if model == self.get_related_model(col_name):
                    return col_name

    def get_pk_name(self):
        return 'id'

    def get(self, id):
        return self.obj.objects(pk=id).first()
