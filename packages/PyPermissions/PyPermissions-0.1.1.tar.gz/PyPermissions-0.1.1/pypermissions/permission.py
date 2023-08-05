class Permission(object):
    """This class represents the most basic permission possible. It has any number of segments, but is fully defined by
    it's name. It may have wildcards, allowing for easily giving multiple permissions of the same form to users,
    especially when the number of permissions is large, infinite, or undetermined. Note: Permissions with different
    delimiters and wildcards are treated as the same, so don't use multiple delimiters or wildcards unless you know
    completely what you're doing.
    """

    def __init__(self, name, description=None, delimiter=".", wildcard="*"):
        """Create a Permission object with the specified name and optional description.

        :param name: The string representing the name of the permission. This indicates what the permission grants.
        :param description: A human-readable string describing the abilities this permission grants.
        :param delimiter: The character to be used as the delimiter for segments. Default: "."
        :param wildcard: The character to be used as the wildcard. Default: "*"
        :rtype: :py:class`Permission` representing the supplied values.
        """

        self.delimiter = delimiter
        self.segments = name.split(self.delimiter)
        self.description = description
        self.wildcard = wildcard

    @property
    def is_wildcard(self):
        """Determines whether the permission is a wildcard permission or a simple permission.

        :rtype: True or False
        """

        return self.wildcard in self.segments

    @property
    def is_end_wildcard(self):
        """Returns whether this permission ends in a wildcard. Terminating wildcards are treated differently from other
        wildcards, as they may represent an infinite number of segments rather than just the typical single segment.

        :rtype: True or False
        """

        return self.segments[len(self.segments)-1] == self.wildcard

    def grants_permission(self, other_permission):
        """Checks whether this permission grants the supplied permission.

        :param other_permission: The permission that we're checking
        :type other_permission: :py:class:`Permission` or :py:class:`basestring`
        :rtype: True or False
        """

        if isinstance(other_permission, basestring):
            other_permission = Permission(name=other_permission)

        if len(self.segments) < len(other_permission.segments) and not self.is_end_wildcard:
            return False

        if len(self.segments) > len(other_permission.segments):
            return False

        for s, o in zip(self.segments, other_permission.segments):
            if s != o and s != self.wildcard:
                return False

        return True

    def grants_any_permission(self, permission_set):
        """Checks whether this permission grants access to any permission in the supplied set.

        :param permission_set: The set of Permissions that we are checking
        :rtype: True or False
        """

        return any(self.grants_permission(perm) for perm in permission_set)

    @property
    def name(self):
        """Returns the name of this permission.

        :rtype: :py:class`str`
        """

        return self.delimiter.join(self.segments)

    def __eq__(self, other):
        if not hasattr(other, "name"):
            return False
        if not self.description:
            return self.name == other.name
        if not hasattr(other, "description"):
            return False
        return self.name == other.name and self.description == other.description

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "{cls}({name}, {desc})".format(cls=self.__class__.__name__, name=self.name, desc=self.description)

    def __hash__(self):
        return 17 * self.name.__hash__() + 19 * self.description.__hash__()

    @staticmethod
    def meets_requirements(permission, **kwargs):
        if permission:
            return True
        return False


class DynamicPermission(Permission):
    """Dynamic permissions are used for cases where you want to grant permissions that require state. These permissions
    require additional information in order to be evaluated (such as access to a database). This class serves as the
    base for dynamic permissions."""

    # The list of templates that this dynamic permission uses to match other permissions.
    templates = []

    def grants_permission(self, other_permission):
        """Checks whether this permission grants the supplied permission.

        :param other_permission: The permission that we're checking
        :type other_permission: :py:class:`Permission` or :py:class:`basestring`
        :rtype: True or False
        """

        for template in self.templates:
            matches, m = template.matches_format(other_permission)
            if matches:
                return self._grants_permission(m, template)

        return False

    def _grants_permission(self, components, template):
        """This method is where you define the stateful logic of your dynamic permission. Only permissions that match
        the formats you specified with your templates will reach this code, and only the wildcard portion of the
        template is returned. The template is supplied so that you know how to parse the components.

        :param components: A :py:class:`list` containing the portions of the other permission tht matched the template
        :param template: The :py:class:`PermissionTemplate` that matched the permission.
        :rtype: True or False
        """

        raise NotImplementedError()


class PermissionSet(set):

    def grants_permission(self, other_permission):
        """Checks whether this permission set has a permission that grants the supplied permission.

        :param other_permission: The permission that we're checking
        :type other_permission: :py:class:`Permission` or :py:class:`basestring`
        :rtype: True or False
        """
        return any(perm.grants_permission(other_permission) for perm in self)

    def grants_any_permission(self, permission_set):
        """Checks whether this permission set has any permission that grants access to any permission in the supplied
        set.

        :param permission_set: The set of Permissions that we are checking
        :rtype: True or False
        """

        """O(n^2) :( Can be done faster."""
        return any(self.grants_permission(perm) for perm in permission_set)

    def has_any_permission(self, other_permission):
        """Checks whether any permission in this permission set is of the form other_permission. Strictly speaking, this
        checks whether any permission in the set is granted by other_permission.

        :param other_permission: The permission whose form we're checking for
        :rtype: True or False
        """

        if isinstance(other_permission, basestring):
            other_permission = Permission(name=other_permission)

        return other_permission.grants_any_permission(self)

    def __getattr__(self, item):
        ret = getattr(super(PermissionSet, self), item)
        return PermissionSet(ret) if isinstance(ret, set) else ret


