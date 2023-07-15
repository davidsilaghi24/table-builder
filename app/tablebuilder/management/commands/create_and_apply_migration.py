import os
import re
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.migrations import Migration
from django.db.migrations.writer import MigrationWriter
from django.db import migrations
from django.db.migrations.loader import MigrationLoader
from tablebuilder.models import DynamicTable
from tablebuilder.dynamic_models import generate_model


class Command(BaseCommand):
    help = 'Create and apply migration for a specific DynamicTable'

    def add_arguments(self, parser):
        parser.add_argument('table_id', type=int)

    def handle(self, *args, **options):
        table_id = options['table_id']
        try:
            # Fetch the table and generate the model
            table = DynamicTable.objects.get(id=table_id)
            dynamic_model = generate_model(table_id)

            # Load all migrations
            loader = MigrationLoader(None, ignore_no_migrations=True)
            # Get the last migration for the tablebuilder app
            last_migration = loader.graph.leaf_nodes('tablebuilder')

            # Create a new migration operation for this model
            operation = migrations.CreateModel(
                name=dynamic_model.__name__,
                fields=[(f.name, f) for f in dynamic_model._meta.local_fields],
                options={"app_label": "tablebuilder"},
            )

            # Create the Migration object with the dependency to the last migration or the initial migration
            migration = Migration("create_table_%s" %
                                  dynamic_model.__name__, "tablebuilder")

            # Check if an initial migration file exists
            migration_files = os.listdir('tablebuilder/migrations')
            initial_migration_files = [
                file for file in migration_files if re.search(r'_initial\.py$', file)
            ]
            if initial_migration_files:
                initial_migration_files.sort(reverse=True)
                initial_migration_name = os.path.splitext(
                    initial_migration_files[0])[0]
                migration.dependencies.append(
                    ("tablebuilder", initial_migration_name))
            elif last_migration:
                last_migration_name = last_migration[0] if isinstance(
                    last_migration[0], str) else last_migration[0][0]
                migration.dependencies.append(
                    ("tablebuilder", last_migration_name))

            migration.operations.append(operation)

            # Write the migration file
            migration_string = MigrationWriter(migration).as_string()
            migration_file_path = os.path.join(
                "tablebuilder/migrations", f"create_table_{dynamic_model.__name__}.py")
            with open(migration_file_path, "w") as migration_file:
                migration_file.write(migration_string)

            # Apply the migration
            call_command('migrate', 'tablebuilder')

        except DynamicTable.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                f"Table with id {table_id} does not exist"))
