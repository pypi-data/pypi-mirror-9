from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v2_0.objects import PathItem, Operation, Schema, Swagger
from ...spec.v2_0.parser import PathItemContext
from ...utils import jp_split, scope_split


class PatchObject(object):
    """ 
    - produces/consumes in Operation object should override those in Swagger object.
    - parameters in Operation object should override those in PathItem object.
    - fulfill Operation.method, which is a pyswagger-only field.
    """

    class Disp(Dispatcher): pass

    @Disp.register([Operation])
    def _operation(self, path, obj, app):
        """
        """
        if isinstance(app.root, Swagger):
            # produces/consumes
            obj.update_field('produces', app.root.produces if len(obj.produces) == 0 else obj.produces)
            obj.update_field('consumes', app.root.consumes if len(obj.consumes) == 0 else obj.consumes)

        # combine parameters from PathItem
        if obj._parent_:
            for p in obj._parent_.parameters:
                for pp in obj.parameters:
                    if p.name == pp.name:
                        break
                else:
                    obj.parameters.append(p)

        # schemes
        obj.update_field('schemes', app.schemes if len(obj.schemes) == 0 else obj.schemes)

    @Disp.register([PathItem])
    def _path_item(self, path, obj, app):
        """
        """
        k = jp_split(path)[-1] # key to the dict containing PathItem(s)
        if isinstance(app.root, Swagger):
            url = app.root.host + (app.root.basePath or '') + k
            base_path = app.root.basePath
        else:
            url = None
            base_path = None

        for c in PathItemContext.__swagger_child__:
            o = getattr(obj, c[0])
            if isinstance(o, Operation):
                # base path
                o.update_field('base_path', base_path)
                # path
                o.update_field('path', k)
                # url
                o.update_field('url', url)
                # http method
                o.update_field('method', c[0]) 

    @Disp.register([Schema])
    def _schema(self, path, obj, app):
        """ fulfill 'name' field for objects under
        '#/definitions' and with 'properties'
        """
        if path.startswith('#/definitions'):
            last_token = jp_split(path)[-1]
            if app.version == '1.2':
                obj.update_field('name', scope_split(last_token)[-1])
            else:
                obj.update_field('name', last_token)

