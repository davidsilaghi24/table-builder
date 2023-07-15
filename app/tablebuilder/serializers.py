from rest_framework import serializers
from .models import DynamicField, DynamicTable


class DynamicFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicField
        fields = '__all__'
        extra_kwargs = {'table': {'required': False}}


class DynamicTableSerializer(serializers.ModelSerializer):
    fields = DynamicFieldSerializer(many=True)

    class Meta:
        model = DynamicTable
        fields = ['id', 'name', 'fields']

    def create(self, validated_data):
        fields_data = validated_data.pop('fields')
        table = DynamicTable.objects.create(**validated_data)
        for field_data in fields_data:
            DynamicField.objects.create(table=table, **field_data)
        return table

    def update(self, instance, validated_data):
        """
        This method is overridden to handle the updating of nested fields.
        """

        # Handle the fields separately
        fields_data = validated_data.pop('fields')

        # Update the table's name
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Keep track of existing ids to find out which ones have been removed
        existing_ids = set(field.id for field in instance.fields.all())

        # Update or create each field
        for field_data in fields_data:
            field_id = field_data.get('id')
            if field_id and DynamicField.objects.filter(id=field_id, table=instance).exists():
                # The field already exists, update it
                DynamicField.objects.filter(id=field_id).update(**field_data)
                existing_ids.remove(field_id)
            else:
                # The field does not exist, create it
                DynamicField.objects.create(table=instance, **field_data)

        # The ids that are still in existing_ids have been removed from the data, delete them
        DynamicField.objects.filter(id__in=existing_ids).delete()

        return instance


def dynamic_model_serializer(dynamic_model):
    """
    Create a ModelSerializer class for a given model.
    """
    class DynamicModelSerializer(serializers.ModelSerializer):
        class Meta:
            model = dynamic_model
            fields = '__all__'
    return DynamicModelSerializer
