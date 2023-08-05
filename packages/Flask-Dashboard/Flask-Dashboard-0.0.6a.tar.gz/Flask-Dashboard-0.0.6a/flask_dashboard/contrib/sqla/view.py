from __future__ import unicode_literals
from sqlalchemy import or_, desc, inspect
from sqlalchemy.orm import RelationshipProperty, ColumnProperty
from sqlalchemy.orm.interfaces import MANYTOONE

# TODO: reimplement
from flask.ext.admin.contrib.sqla.view import ModelView as _ModelView

from flask.ext.dashboard.model import BaseModelView
from flask.ext.dashboard.contrib.sqla.filters import BaseSQLAFilter


class ModelView(BaseModelView, _ModelView):

    def get_pk_value(self, model):
        """
            Return the PK value from a model object.
            PK will always be a tuple.
        """
        return inspect(self.model).primary_key_from_instance(model)

    def scaffold_list_columns(self):
        """
            Return a list of columns from the model.
        """
        columns = []
        for key, prop in inspect(self.model).attrs.items():
            if isinstance(prop, RelationshipProperty):
                if self.column_display_all_relations or \
                        prop.direction == MANYTOONE:
                    columns.append(key)
            elif isinstance(prop, ColumnProperty):
                column = prop.expression
                if column.primary_key:
                    if not self.column_display_pk:
                        continue
                elif column.foreign_keys:
                    continue
                columns.append(key)
        return columns

    def scaffold_sortable_columns(self):
        """
            Return a dictionary of sortable columns.
            Key is column name, value is sort column/field.
        """
        columns = {}
        for key, prop in inspect(self.model).column_attrs.items():
            if len(prop.columns) > 1:
                continue
            column = prop.expression
            if column.foreign_keys:
                continue
            if not self.column_display_pk and column.primary_key:
                continue
            columns[key] = column
        return columns

    def init_search(self):
        # TODO: reimplement
        return super(ModelView, self).init_search()

    def scaffold_form(self):
        # TODO: reimplement
        return super(ModelView, self).scaffold_form()

    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True):
        count, query = super(ModelView, self).get_list(
            page, sort_column, sort_desc, search, filters)
        if execute:
            query = query.all()
        return count, query

    def get_one(self, id):
        """
            Return a single model by its id.

            :param id:
                Model id
        """
        return self.session.query(self.model).get(id)

    def create_model(self, form):
        # TODO: reimplement
        return super(ModelView, self).create_model(form)

    def update_model(self, form, model):
        # TODO: reimplement
        return super(ModelView, self).update_model(form, model)

    def delete_model(self, model):
        # TODO: reimplement
        return super(ModelView, self).delete_model(model)

    def is_valid_filter(self, filter):
        """
            Verify that the provided filter object is derived from the
            SQLAlchemy-compatible filter class.

            :param filter:
                Filter object to verify.
        """
        return isinstance(filter, BaseSQLAFilter)

    def scaffold_filters(self, name):
        # TODO: reimplement
        return super(ModelView, self).scaffold_filters(name)

    def get_lazy_data_set(self):
        return self.get_query()

    def apply_search(self, query, search):
        if self._search_supported and search:
            words = search.split(" ")
            for word in words:
                if not word:
                    continue
                stmt = "%{0}%".format(word)
                query = query.filter(or_(*map(
                    lambda x: x.ilike(stmt),
                    self._search_fields,
                )))
        return query

    def apply_filters(self, query, filters):
        if filters and self._filters:
            for idx, value in filters:
                flt = self._filters[idx]
                query = flt.apply(query, value)
        return query

    def apply_sorting(self, query, sort_field, sort_desc):
        if sort_field is not None:
            if sort_field in self._sortable_columns:
                sort_field = self._sortable_columns[sort_field]
                if isinstance(sort_field, basestring):
                    sort_field = getattr(self.model, sort_field)
                if sort_desc:
                    sort_field = desc(sort_field)
                query = query.order_by(sort_field)
        return query

    def apply_pagination(self, query, page):
        if page is not None:
            query = query.offset(page * self.page_size)
        query = query.limit(self.page_size)
        return query

    def get_count(self, query):
        return query.count()
