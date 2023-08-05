import collections


class CrAdminInstanceRegistry(object):
    """
    We want the _current_ CrAdmin instance to be available
    without having to add it to all the views within the
    instance (we want to add it in a middleware and in a template context).

    At the same time, we want to be able to have multiple instances of CrAdmin
    running on the same site (imagine one site for employees and one for
    customers with a completely different look and feel).

    The solution is simple: If we have only a single instance, we do not
    need to do anything except adding it to this registry. If we have
    multiple instances, each of them must implement
    :meth:`django_cradmin.crinstance.BaseCrAdminInstance.matches_urlpath`.

    Example::

        from django_cradmin.crinstance import BaseCrAdminInstance
        from django_cradmin.registry import cradmin_instance_registry

        class MyCrAadminInstance(BaseCrAdminInstance):
            # ...

        cradmin_instance_registry.add(MyCrAadminInstance)
    """

    def __init__(self):
        self._registry = collections.OrderedDict()

    def get_instanceclass_by_id(self, id):
        """
        Get a CrAdmin instance class by ID (by :obj:`django_cradmin.crinstance.BaseCrAdminInstance.id`).
        """
        return self._registry[id]

    def get_instance_by_id(self, id, request):
        """
        Shortcut for ``get_instanceclass_by_id(id)(request)``.
        """
        return self.get_instanceclass_by_id(id)(request)

    def get_current_instance(self, request):
        """
        Get the current CrAdmin instance.

        Params:
            request (HttpRequest): The http request to the instance for.

        Returns:
            BaseCrAdminInstance: The CrAdmin instance for the given request,
                or ``None`` if no instance matching ``request.path`` is found.
        """
        if len(self._registry) == 1:
            return self._registry.values()[0](request)
        else:
            for instanceclass in self._registry.itervalues():
                if instanceclass.matches_urlpath(request.path):
                    return instanceclass(request)
            return None

    def add(self, cradmin_instance_class):
        """
        Add a CrAdmin instance to the registry.

        Parameters:
            cradmin_instance_class: A subclass of :class:`django_cradmin.crinstance.BaseCrAdminInstance`.
        """
        if cradmin_instance_class.id not in self._registry:
            self._registry[cradmin_instance_class.id] = cradmin_instance_class


cradmin_instance_registry = CrAdminInstanceRegistry()
