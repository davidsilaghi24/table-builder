from django.db import models

# Define a dictionary to map user input to Django model fields
FIELD_TYPE_MAP = {
    'string': lambda: models.CharField(max_length=255),
    'number': lambda: models.IntegerField(),
    'boolean': lambda: models.BooleanField(),
}


FIELD_TYPE_CHOICES = (
    ('string', 'String'),
    ('number', 'Number'),
    ('boolean', 'Boolean'),
)


class DynamicTableModelManager(models.Manager):
    def create_with_fields(self, table_name, fields):
        """
        fields is a list of tuples where each tuple is (field_name, field_type)
        """
        # Create the DynamicTable instance
        dynamic_table = self.create(name=table_name)

        # Create the DynamicField instances
        for field_name, field_type in fields:
            DynamicField.objects.create(
                name=field_name, type=field_type, table=dynamic_table)

        return dynamic_table


class DynamicTable(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = DynamicTableModelManager()

    def __str__(self):
        return self.name


class DynamicField(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=7, choices=FIELD_TYPE_CHOICES)
    table = models.ForeignKey(
        DynamicTable, related_name='fields', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.table.name} - {self.name} ({self.get_type_display()})'
