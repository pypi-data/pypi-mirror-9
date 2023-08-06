"""
    Implements the server side for the instance operators.
"""
from django.core.management.color import no_style
from django.db import connection

from slumber.operations import Operation
from slumber.server import get_slumber_root
from slumber.server.http import require_user, require_permission
from slumber.server.json import to_json_data


def _reset_sequence_number(model):
    """Private utility function to perform a SQL sequence number reset.
    """
    cursor = connection.cursor()
    reset_sequence_command_lines = connection.ops.sequence_reset_sql(
        no_style(), [model])
    if len(reset_sequence_command_lines) != 0:
        cursor.execute(';'.join(reset_sequence_command_lines))


def instance_data(into, model, instance):
    """Fill in the dict `into` with information about the instance of the
    specified model.
    """
    root = get_slumber_root()
    into['type'] = root + model.path
    into['identity'] = root + model.path + \
        '%s/%s/' % ('data', instance.pk)
    into['display'] = unicode(instance)
    into['operations'] = dict(
        [(op.name, op(instance))
            for op in model.operations.values() if not op.model_operation])
    into['fields'] = {}
    for field, meta in model.fields.items():
        into['fields'][field] = dict(
            data=to_json_data(model, instance, field, meta),
            kind=meta['kind'], type=meta['type'])
    into['data_arrays'] = {}
    for field in model.data_arrays:
        into['data_arrays'][field] = \
            into['identity'] + '%s/' % field


class InstanceData(Operation):
    """Return the instance data.
    """
    model_operation = False

    @require_user
    def get(self, request, response, pk, dataset=None):
        """Implement the fetching of attribute data for an instance.
        """
        instance = self.model.model.objects.get(pk=pk)
        if dataset:
            self._get_dataset(request, response, instance, dataset)
        else:
            self._get_instance_data(request, response, instance)

    def put(self, request, response, pk):
        """Allow a new version of the resource to be PUT here.
        """
        @require_permission('%s.add_%s' % (
                self.model.app, self.model.name.lower()))
        def do_put(_cls, request):
            """Apply the permission check to this inner function.
            """
            key_name = self.model.model._meta.pk.name
            pk_filter = {key_name: pk}
            created = (
                self.model.model.objects.filter(**pk_filter).count() == 0)

            instance = self.model.model(**dict(pk_filter.items() +
                [(k, v) for k, v in request.POST.items()]))
            instance.save()

            if created:
                response['_meta']['status'] = 201
                _reset_sequence_number(self.model.model)

            instance_data(response, self.model, instance)
            response['pk'] = to_json_data(self.model, instance, key_name,
                self.model.fields[key_name])

        return do_put(self, request)

    def delete(self, request, _response, pk):
        """Implement deletion of the instance.
        """
        @require_permission('%s.delete_%s' % (
                self.model.app, self.model.name.lower()))
        def do_delete(_cls, _request):
            """Apply the permission check to this inner function.
            """
            instance = self.model.model.objects.get(pk=pk)
            instance.delete()
        return do_delete(self, request)

    def _get_instance_data(self, _request, response, instance):
        """Return the base field data for the instance.
        """
        return instance_data(response, self.model, instance)

    def _get_dataset(self, request, response, instance, dataset):
        """Return one page of the array data.
        """
        root = get_slumber_root()
        response['instance'] = self(instance, dataset)

        try:
            query = getattr(instance, dataset + '_set')
        except AttributeError:
            query = getattr(instance, dataset)
        query = query.order_by('-pk')
        if request.GET.has_key('start_after'):
            query = query.filter(pk__lt=request.GET['start_after'])

        response['page'] = []
        for obj in query[:10]:
            model = type(obj).slumber_model
            response['page'].append(dict(
                    type=root + model.path,
                    pk=obj.pk, display=unicode(obj),
                    data=model.operations['data'](obj)))

        if query.count() > len(response['page']):
            response['next_page'] = self(instance, dataset,
                start_after=response['page'][-1]['pk'])

