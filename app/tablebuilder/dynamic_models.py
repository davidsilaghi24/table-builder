# dynamic_models.py
from django.db import connection
from django.apps import apps
import logging
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .models import DynamicTable, DynamicField, FIELD_TYPE_MAP

# Instantiate logger
logger = logging.getLogger(__name__)


def generate_model(table_id):
    """Generate a Django model dynamically from the fields of a DynamicTable"""
    # Fetch table
    table = DynamicTable.objects.get(id=table_id)

    # Fetch fields for this table
    fields = DynamicField.objects.filter(table=table)

    # Create dict of field names and types
    field_dict = {
        field.name: FIELD_TYPE_MAP[field.type]() for field in fields
    }

    # Add __module__ attribute to field_dict
    field_dict['__module__'] = __name__

    # Use Python's built-in type() function to create the model
    dynamic_model = type(table.name, (models.Model,), field_dict)

    # Register the model with Django's app registry
    apps.register_model('tablebuilder', dynamic_model)

    return dynamic_model


def update_model(table_id, new_fields):
    """Update the structure of a dynamically generated model"""
    try:
        # Fetch table
        table = DynamicTable.objects.get(id=table_id)

        # Remove all existing fields from the table
        DynamicField.objects.filter(table=table).delete()

        # Add new fields to the table
        for field_name, field_type in new_fields.items():
            DynamicField.objects.create(
                name=field_name, type=field_type, table=table)

        # Generate the updated model
        updated_model = generate_model(table_id)

        return updated_model
    except ObjectDoesNotExist:
        # Log the error
        logger.error(f'Table with id {table_id} does not exist')
        return None


def get_model(table_id):
    """Get a dynamically generated model"""
    model = generate_model(table_id)

    if model is None:
        logger.error(f'Model with id {table_id} does not exist')

    return model
