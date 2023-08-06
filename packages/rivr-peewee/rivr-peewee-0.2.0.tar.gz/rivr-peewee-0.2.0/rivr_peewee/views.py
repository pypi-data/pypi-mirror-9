from rivr.views import View
from rivr.http import ResponseRedirect

try:
    from rivr_jinja import JinjaView
except ImportError:
    raise ImportError('rivr-peewee views are missing an optional ' \
                      'dependency of rivr-jinja')


class QueryMixin(object):
    model = None
    query = None

    def get_model(self):
        if self.model:
            return self.model

        return self.query.model_class

    def get_query(self):
        if self.query:
            return query

        if self.model:
            return self.model.select()

        raise Exception('QueryMixin requires either a definition of'
                        '`model` or `query`, or an implementation of'
                        '`get_query()`')

    def get_model_name(self):
        return self.get_model().__name__.lower()


class SingleObjectMixin(QueryMixin):
    def get_object(self):
        pk = self.kwargs['pk']
        return self.get_query().filter(id=pk).get()

    def get_template_names(self):
        return [
            '{}_detail.html'.format(self.get_model_name()),
        ]

    def get_context_data(self, **kwargs):
        kwargs[self.get_model_name()] = self.get_object()
        return kwargs


class DetailView(SingleObjectMixin, JinjaView):
    pass


class MultipleObjectMixin(QueryMixin):
    def get_objects(self):
        return self.get_query()

    def get_template_names(self):
        return [
            '{}_list.html'.format(self.get_model_name()),
        ]

    def get_context_data(self, **kwargs):
        context_name = '{}_list'.format(self.get_model_name())
        kwargs[context_name] = self.get_objects()
        return kwargs


class ListView(MultipleObjectMixin, JinjaView):
    pass

