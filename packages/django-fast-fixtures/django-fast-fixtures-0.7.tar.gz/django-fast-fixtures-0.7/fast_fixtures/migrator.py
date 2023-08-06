
"""
This module attempts to migrate the whole app towards
A fixture's schema state when it was created.

Because doing this can loose data, we will throw a warning and
this warning will act as our first feature.
"""

import sys

from django.apps import apps

from django.db import connections
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.executor import MigrationExecutor

class MigrationsNeeded(ValueError):
    pass


def get_apps(*labels):
    if not labels:
        labels = [ app.label for app in apps.get_app_configs() ]
    for label in labels:
        yield apps.get_app_config(label.split('.',1)[0])


def get_app_state(app_labels, database='default'):
    connection = connections[database]
    loader = MigrationLoader(connection, ignore_no_migrations=True)
    graph = loader.graph

    migrations = list(loader.applied_migrations)[::-1]
    app_state = {}

    # Returns the stamp for the latest migration in these apps
    for app in get_apps(*app_labels):
        for migration in migrations:
            if migration[0] == app.label:
                index, rest = migration[1].split('_', 1)
                if app_state.get(app.label, '0000').split('_', 1)[0] < index:
                    app_state[app.label] = migration[1]
    return app_state


def migrate_to(apps_state, database='default'):
    connection = connections[database]
    executor = MigrationExecutor(connection, _callback)

    targets = []
    for (label, migration_name) in apps_state.items():
        try:
            migration = executor.loader.get_migration_by_prefix(label, migration_name)
        except KeyError:
            raise KeyError("Migration %s.%s can't be found, is it from the future?" % (label, migration_name))
        else:
            targets.append( (label, migration.name) )

    plan = executor.migration_plan(targets)
    if not plan:
        return
    print "\nFixture needs Migrations:\n"
    for migration, backwards in plan:
        print " [%s] %s %s" % ('+-'[backwards], migration.app_label, migration.name)

    answer = (raw_input("""\nDo you want to migrate?

 * [y]es  - Perform the migrations and load fixture
 * [N]o   - Quit now without migration or load data
 * [S]kip - Skip migration and attempt to load fixture without it.

  : """) or 'n').lower()

    if answer == 'n':
        raise MigrationsNeeded("Migrations needed but not being performed!")
    elif answer == 's':
        print "Performing load-data without migration!"
        return

    print "Migrating as planned:"
    executor.migrate(targets, plan, fake=False)
    print "\n"

def _callback(action, migration, fake=False):
    if action == 'apply_success':
        print " + %s" % migration
    if action == 'unapply_success':
        print " - %s" % migration

