from pypermissions.permission import Permission


class PermissionFactory(object):
    """General factory for creating permissions. Will select the correct permission type for the provided string and
        return that."""

    def __init__(self, delimiter=".", wildcard="*", prefix="", templates=None):
        """Allows developers to use custom characters for the special characters in the permissions.

        :param delimiter: The character that serves as the separator for permissions. Default value: "."
        :param wildcard: The character that serves as the wildcard segment. Default: "*"
        :param prefix: The prefix to be added to all permissions created with this factory. Default: None
        """

        self.delimiter = delimiter
        self.wildcard = wildcard
        self.prefix = prefix + self.delimiter if prefix else ""
        self.templates = templates if templates else list()

    def create_permission(self, permission):
        """Create a permission from the provided string, adding prefixes as necessary.

        :param permission: String representing the permission to be returned
        :rtype: :py:class:`Permission` or one of it's subclasses
        """

        if self.prefix:
            permission = self.prefix + permission

        for template in self.templates:
            if template.matches_format(permission)[0]:
                return template.create_permission(permission)

        return Permission(name=permission, delimiter=self.delimiter, wildcard=self.wildcard)


    def create_child(self, prefix):
        """Create a PermissionFactory with a prefix that is this factory's prefix with the provided prefix added on.
        Useful for creating factories for different components of the same application.

        :param prefix: The prefix to be added to the end of this factory's prefix
        """

        return PermissionFactory(delimiter=self.delimiter, wildcard=self.wildcard, prefix=self.prefix + prefix,
                                 templates=self.templates)

    def register_template(self, template, index=None):
        """Register a new template for the factory to use when creating permissions.

        :param template: the :py:class:`PermissionTemplate` to be added
        """

        if not index:
            self.templates.append(template)
        else:
            self.templates.insert(index, template)


    def __repr__(self):
        return "{cls}({prefix}, {d}, {w})".format(cls=self.__class__.__name__, prefix=self.prefix[:-1], w=self.wildcard,
                                                  d=self.delimiter)

    def __eq__(self, other):
        return self.delimiter == other.delimiter and self.wildcard == other.wildcard and self.prefix == other.prefix

