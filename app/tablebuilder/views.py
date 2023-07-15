from rest_framework import generics
from django.core.management import call_command
from .models import DynamicTable, DynamicField
from .serializers import DynamicTableSerializer, dynamic_model_serializer
from .dynamic_models import get_model


class TableListView(generics.ListCreateAPIView):
    queryset = DynamicTable.objects.all()
    serializer_class = DynamicTableSerializer

    def perform_create(self, serializer):
        table = serializer.save()
        call_command('create_and_apply_migration', table.id)


class TableDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DynamicTable.objects.all()
    serializer_class = DynamicTableSerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        table = serializer.save()
        requested_fields = {f.get('name'): f.get('type')
                            for f in self.request.data.get('fields', [])}

        # Delete fields that are not in the request data
        for field in table.fields.all():
            if field.name not in requested_fields:
                field.delete()

        # Create or update fields from request data
        for field_name, field_type in requested_fields.items():
            DynamicField.objects.update_or_create(
                name=field_name, table=table, defaults={'type': field_type})

        call_command('create_and_apply_migration', table.id)


class RowListView(generics.ListCreateAPIView):
    def get_dynamic_model(self):
        if not hasattr(self, "_dynamic_model"):
            self._dynamic_model = get_model(self.kwargs.get('id'))
        return self._dynamic_model

    def get_queryset(self):
        dynamic_model = self.get_dynamic_model()
        if not dynamic_model:
            return dynamic_model.objects.none()
        return dynamic_model.objects.all()

    def get_serializer_class(self):
        return dynamic_model_serializer(self.get_dynamic_model())

    def perform_create(self, serializer):
        serializer.save()


class RowDetailView(generics.RetrieveUpdateDestroyAPIView):
    def get_dynamic_model(self):
        if not hasattr(self, "_dynamic_model"):
            self._dynamic_model = get_model(self.kwargs.get('id'))
        return self._dynamic_model

    def get_queryset(self):
        dynamic_model = self.get_dynamic_model()
        if not dynamic_model:
            return dynamic_model.objects.none()
        return dynamic_model.objects.all()

    def get_serializer_class(self):
        return dynamic_model_serializer(self.get_dynamic_model())
