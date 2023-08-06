"""jquery_alchemy is a module to handle generating 'rules' for the
jquery validation package from sqlalchemy columns.

It is designed to work with orm-based form generation modules,
such as wtforms_alchemy, deform (colander_alchemy) or formalchemy."""

from sqlalchemy import (
    Boolean,
    Float,
    inspect,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    )

from sqlalchemy_utils import (
    EmailType,
    IPAddressType,
    URLType,
    )


def jquery_alchemy(cls):

    """Any sqlalchemy Column can have an 'info' dictionary.
    If this contains am explicit 'jquery_validate' sub-dict, use it.
    Otherwise, create the dict implicitly from Column information."""

    cls = inspect(cls)
    rules = {'rules': {}}
    for prop in cls.attrs:
        # Always a 1-item list?
        column = prop.columns[0]

        # Check for explicit rule definitions
        if 'jquery_validate' in column.info:
            rules['rules'][prop.key] = column.info['jquery_validate']
        else:
            # Create implicit rule definitions if no explicit ones set
            column.info['jquery_validate'] = {}

            # General rules which apply to all columns
            if not column.nullable:
                column.info['jquery_validate']['required'] = True

            if hasattr(column.type, 'length'):
                column.info['jquery_validate']['maxlength'] = column.type.length

            # Specific rules for particular column types
            if isinstance(column.type, EmailType):
                column.info['jquery_validate']['email'] = True

            elif isinstance(column.type, Integer):
                column.info['jquery_validate']['integer'] = True

            elif isinstance(column.type, IPAddressType):
                column.info['jquery_validate']['ipv4'] = True

            elif isinstance(column.type, Numeric):
                column.info['jquery_validate']['number'] = True

            elif isinstance(column.type, Time):
                column.info['jquery_validate']['time'] = True

            elif isinstance(column.type, URLType):
                column.info['jquery_validate']['url'] = True

            rules['rules'][prop.key] = column.info['jquery_validate']

    return rules
