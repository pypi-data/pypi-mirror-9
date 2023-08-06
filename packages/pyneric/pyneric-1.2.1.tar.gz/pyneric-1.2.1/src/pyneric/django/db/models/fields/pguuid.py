# -*- coding: utf-8 -*-
"""UUID Django `~django:django.db.models.fields` for
`PostgreSQL <http://www.postgresql.org/>`_ backends.

Loading this module patches `~django:django.db.models.ForeignKey` so that it
can refer to an `AutoPgUuidField` without assuming that it is an
`~django:django.db.models.IntegerField`.

"""

# Support Python 2 & 3.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyneric.future import *

from functools import wraps

from django.db.models.fields import AutoField, Field
from django.db.models.fields.related import ForeignKey
from django_extensions.db.fields import PostgreSQLUUIDField

from pyneric.util import add_to_all


__all__ = []


# Monkey patch ForeignKey.db_type to fix the assumption that an AutoField is an
# IntegerField.
if hasattr(ForeignKey.db_type,
           '_pyneric_autopguuidfield_patch'):  # pragma: no cover
    pass
else:
    _foreign_key_db_type_original = ForeignKey.db_type

    @wraps(ForeignKey.db_type)
    def _foreign_key_db_type(self, connection):
        rel_field = self.related_field
        if isinstance(rel_field, AutoPgUuidField):
            return rel_field.db_type(connection=connection)
        return _foreign_key_db_type_original(self, connection)
    _foreign_key_db_type._pyneric_autopguuidfield_patch = True
    ForeignKey.db_type = _foreign_key_db_type


@add_to_all
class AutoPgUuidField(PostgreSQLUUIDField, AutoField):

    """A `PostgreSQLUUIDField` that is also an
    `~django:django.db.models.AutoField`.

    The generation of the UUID value in the database must be set up manually
    (via a migration or another mechanism).  Django 1.7 migration example::

        migrations.RunSQL(
            "ALTER TABLE autopguuid ALTER uuid_field"
            " SET DEFAULT uuid_generate_v4();",
            "ALTER TABLE autopguuid ALTER uuid_field DROP DEFAULT;"
        ),

    Setting the database default automatically may be added in a future
    version.

    """

    def get_prep_value(self, value):
        """Override to bypass `~django:django.db.models.AutoField`\'s integer
        value assumption."""
        value = Field.get_prep_value(self, value)
        return self.to_python(value)
