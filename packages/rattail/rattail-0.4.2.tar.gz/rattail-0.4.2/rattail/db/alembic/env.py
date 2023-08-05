# -*- coding: utf-8 -*-
"""
Alembic Environment Script
"""

from __future__ import unicode_literals

from alembic import context

import edbob

from rattail.db import model
from rattail.db.util import get_default_engine
from rattail.db.batches.util import batch_pattern


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
alembic_config = context.config

# Initialize edbob with whichever config file alembic is using.
edbob.init('rattail', alembic_config.config_file_name)
rattail_config = edbob.config

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = model.Base.metadata


def include_object(object, name, type, reflected, compare_to):
    """
    Custom inclusion callable, used to prevent autogenerate from attempting to
    drop all the old-style batch tables.
    """
    if type == 'table':
        return not bool(batch_pattern.match(name))
    return True


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    engine = get_default_engine(rattail_config)
    context.configure(
        url=engine.url,
        target_metadata=target_metadata,
        include_object=include_object)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = get_default_engine(rattail_config)
    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object)

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
