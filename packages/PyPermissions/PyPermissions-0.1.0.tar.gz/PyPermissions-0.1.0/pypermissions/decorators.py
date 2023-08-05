from pypermissions.permission import PermissionSet


def _prepare_runtime_permission(self, perm=None, runkw=None, args=None, kwargs=None):
    """This function parses the provided string arguments to decorators into the actual values for use when the
    decorator is being evaluated. This allows for permissions to be created that rely on arguments that are provided to
    the function.

    :param perm: The permission string to parse
    :param runkw: The run-time components to be inserted into the permission
    :param args: The arguments provided to the decorated function
    :param kwargs: The keyword arguments provided to the decorated function
    :rtype: :py:class:`str`
    """

    permission = perm
            
    if not permission:
        return False

    for key, value in runkw.iteritems():
        val_split = value.split('.')
        for attr in val_split:
            if attr == "self":
                value = self
                continue
            elif attr in kwargs:
                value = kwargs.get(attr)
                continue
            value = getattr(value, attr)
                    
        permission = permission.replace('{'+key+'}', value)

    return permission


def set_has_permission(perm=None, perm_set=None, on_failure=None, perm_check=None, **runkw):
    """This decorator checks if the provided permission set has the permission specified. It allows for the permission
    to rely on runtime information via runkw; which be used to modify perm based on arguments provided to the decorated
    function. For many use cases, this can be extended by decorating it with a custom decorator that will capture the
    current user making the function call, and providing their permissions as the perm_set. The function provided for
    use when the check fails will be called with the decorated functions arguments.

    :param perm: The permission to be checked. May contain {} tags to be replaced at run time.
    :param perm_set: The permission set being checked for the permission.
    :param on_failure: A function that gets called instead of the decorated function when perm_set does not have the
        specified permission.
    :param perm_check: The PermissionSet function to be used when evaluating for perm.
    :param runkw: The mappings to be used to create the actual permission at run time.
    """
        
    def decorator(function):

        def check_permission(self, *args, **kwargs):
            permission = _prepare_runtime_permission(self, perm, runkw, args, kwargs)

            # No permission provided, so everyone has permission.
            if not permission:
                return function(self, *args, **kwargs)

            if not perm_set:
                return on_failure(self, *args, **kwargs)

            if not perm_check(perm_set, permission):
                return on_failure(self, *args, **kwargs)
            
            return function(self, *args, **kwargs)
            
        return check_permission
    
    return decorator


def set_grants_permission(perm=None, perm_set=None, on_failure=None, **runkw):
    """This decorator checks if the provided permission set has the permission specified. It allows for the permission
    to rely on runtime information via runkw; which be used to modify perm based on arguments provided to the decorated
    function. For many use cases, this can be extended by decorating it with a custom decorator that will capture the
    current user making the function call, and providing their permissions as the perm_set. The function provided for
    use when the check fails will be called with the decorated functions arguments.

    :param perm: The permission to be checked. May contain {} tags to be replaced at run time.
    :param perm_set: The permission set being checked for the permission.
    :param on_failure: A function that gets called instead of the decorated function when perm_set does not have the
        specified permission.
    :param runkw: The mappings to be used to create the actual permission at run time.
    """

    return set_has_permission(perm, perm_set, on_failure, perm_check=PermissionSet.grants_permission, **runkw)


def set_has_any_permission(perm=None, perm_set=None, on_failure=None, **runkw):
    """This decorator checks if the provided permission set has a permission of the form specified. It allows for the
    permission to rely on runtime information via runkw; which be used to modify perm based on arguments provided to the
    decorated function. For many use cases, this can be extended by decorating it with a custom decorator that will
    capture the current user making the function call, and providing their permissions as the perm_set. The function
    provided for use when the check fails will be called with the decorated functions arguments.

    :param perm: The permission to be checked. May contain {} tags to be replaced at run time.
    :param perm_set: The permission set being checked for the permission.
    :param on_failure: A function that gets called instead of the decorated function when perm_set does not have the
        specified permission.
    :param runkw: The mappings to be used to create the actual permission at run time.
    """

    return set_has_permission(perm, perm_set, on_failure, perm_check=PermissionSet.has_any_permission, **runkw)
