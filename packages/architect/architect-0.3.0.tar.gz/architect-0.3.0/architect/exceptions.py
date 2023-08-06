"""
Architect tries it's best to provide human readable errors in all situations.
This is a list of all exceptions that Architect can throw.
"""


class BaseArchitectError(Exception):
    """
    Base exception class. All Architect exceptions should inherit from it.
    """
    def __init__(self, message, **kw):
        super(BaseArchitectError, self).__init__(
            message.format(current=kw.get('current', ''), allowed=', '.join(list(kw.get('allowed', [])))))


class CommandNotProvidedError(BaseArchitectError):
    """
    Command not provided.
    """
    def __init__(self, **kw):
        super(CommandNotProvidedError, self).__init__('Command not provided, available commands are: {allowed}', **kw)


class CommandError(BaseArchitectError):
    """
    Unrecognized command.
    """
    def __init__(self, **kw):
        super(CommandError, self).__init__('Unknown command "{current}", available commands are: {allowed}', **kw)


class CommandArgumentError(BaseArchitectError):
    """
    Unrecognized command argument.
    """
    def __init__(self, **kw):
        super(CommandArgumentError, self).__init__(
            'Argument(s) "{current}" not recognized, available arguments are: {allowed}', **kw)


class ImportProblemError(BaseArchitectError):
    """
    Wrapper for ImportError.
    """
    def __init__(self, message, **kw):
        super(ImportProblemError, self).__init__(message, **kw)


class BaseDatabaseError(BaseArchitectError):
    """
    Base exception class for all database exceptions.
    """
    def __init__(self, message, **kw):
        super(BaseDatabaseError, self).__init__(
            message.format(model=kw.get('model', ''), dialect=kw.get('dialect', '')), **kw)


class ORMError(BaseDatabaseError):
    """
    Unsupported ORM.
    """
    def __init__(self, **kw):
        super(ORMError, self).__init__(
            'Unsupported ORM "{{current}}" requested for model "{model}", available ORMs are: {{allowed}}', **kw)


class FeatureInstallError(BaseDatabaseError):
    """
    Unsupported feature.
    """
    def __init__(self, **kw):
        super(FeatureInstallError, self).__init__(
            'Unsupported feature "{{current}}" for model "{model}", supported features are: {{allowed}}', **kw)


class FeatureUninstallError(BaseDatabaseError):
    """
    Can't uninstall feature that isn't installed.
    """
    def __init__(self, **kw):
        super(FeatureUninstallError, self).__init__(
            'Can\'t uninstall feature "{{current}}" from model "{model}" because it\'s '
            'not even installed, valid installed features are: {{allowed}}', **kw)


class MethodAutoDecorateError(BaseDatabaseError):
    """
    Unable to autodecorate method.
    """
    def __init__(self, **kw):
        super(MethodAutoDecorateError, self).__init__(
            'Unable to autodecorate method "{{current}}" in model "{model}", method not found', **kw)


class DatabaseError(BaseDatabaseError):
    """
    Unsupported database.
    """
    def __init__(self, **kw):
        super(DatabaseError, self).__init__(
            'Unsupported database "{{current}}", supported databases are: {{allowed}}', **kw)


class OptionNotSetError(BaseDatabaseError):
    """
    Option not set.
    """
    def __init__(self, **kw):
        kw['current'] = str(kw.get('current', '')).replace("'", '')
        super(OptionNotSetError, self).__init__('Option "{{current}}" isn\'t set for model "{model}"', **kw)


class DsnParseError(BaseDatabaseError):
    """
    Unable to parse given Data Source Name.
    """
    def __init__(self, **kw):
        super(DsnParseError, self).__init__('Invalid DSN "{{current}}" provided for model "{model}"', **kw)


class PartitionColumnError(BaseDatabaseError):
    """
    Unrecognized partition column.
    """
    def __init__(self, **kw):
        super(PartitionColumnError, self).__init__(
            'Partition column "{{current}}" wasn\'t found in model "{model}", available columns are: {{allowed}}', **kw)


class PartitionTypeError(BaseDatabaseError):
    """
    Unsupported partition type.
    """
    def __init__(self, **kw):
        super(PartitionTypeError, self).__init__(
            'Unsupported partition type "{{current}}" in model "{model}", '
            'supported types for "{dialect}" database are: {{allowed}}', **kw)


class PartitionRangeError(BaseDatabaseError):
    """
    Unsupported partition range.
    """
    def __init__(self, **kw):
        super(PartitionRangeError, self).__init__(
            'Unsupported partition range "{{current}}" in "{model}" model, '
            'supported partition ranges for "{dialect}" database are: {{allowed}}', **kw)


class PartitionRangeSubtypeError(BaseDatabaseError):
    """
    Unsupported partition range subtype.
    """
    def __init__(self, **kw):
        super(PartitionRangeSubtypeError, self).__init__(
            'Unsupported partition range subtype "{{current}}" in "{model}" model, '
            'supported range subtypes for "{dialect}" database are: {{allowed}}', **kw)


class PartitionFunctionError(BaseDatabaseError):
    """
    Unsupported partition function.
    """
    def __init__(self, **kw):
        super(PartitionFunctionError, self).__init__(
            'Unsupported partition function for column type "{{current}}" in "{model}" '
            'model, supported column types for "{dialect}" backend are: {{allowed}}', **kw)
