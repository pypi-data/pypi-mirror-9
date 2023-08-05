from pypermissions.permission import Permission


class PermissionTemplate(object):
    """This class is used for defining a way to classify Permissions based on their format. This is used in factories to
        determine which Permission type to make the permission, as well as what description to give the new permission.
    """

    def __init__(self, form="", delimiter=".", wildcard="*", match="!", description="", cls=Permission):
        """Create a Permission Template.
        :param form: The format of the template to use when matching permissions.
        :param delimiter: The character to be used as the permission delimiter. Default: "."
        :param wildcard: The character to be used as the permission wildcard. Default: "*"
        :param match: The character to be used as the template wildcard. Default: "!"
        :param description: The description to create permissions that match this template with. Should be provided as a
            string. Can include references to the matched segments of the permission by using the standard tuple format
            from :py:func:`str.format`.
        """

        self.form = form
        self.delimiter = delimiter
        self.wildcard = wildcard
        self.description = description
        self.match = match
        self.cls = cls
        self.segments = self.form.split(self.delimiter)

    def matches_format(self, permission):
        """Checks if the provided permission matches the format for this template.

        :param permission: The permission to be checked.
        :rtype: A tuple containing True or False and a list of the matched segments if matched, and an empty list
            otherwise.
        """

        matches = list()

        if isinstance(permission, basestring):
            permission = Permission(name=permission, delimiter=self.delimiter, wildcard=self.wildcard)

        if permission.delimiter != self.delimiter:
            return False, []

        if permission.wildcard != self.wildcard:
            return False, []

        if len(self.segments) != len(permission.segments):
            return False, []

        for s, p in zip(self.segments, permission.segments):
            if s == self.match:
                matches.append(p)
                continue

            if s != p:
                return False, []

        return True, matches

    def create_permission(self, permission):
        """Creates a permission object of the type specified for this template iff permission matches the template.
        Returns False if the permission is not applicable for this template.

        :param permission: the :py:class:`str` representing the name for the desired permission
        :rtype: A Permission (or subclass) object representing the provided permission
        """

        matches, segments = self.matches_format(permission)

        if not matches:
            return False

        return self.cls(name=permission, description=self.description.format(*tuple(segments)), delimiter=self.delimiter,
                        wildcard=self.wildcard)


