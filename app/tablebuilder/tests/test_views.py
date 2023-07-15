from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from tablebuilder.models import DynamicTable, DynamicField


class TableViewTestCase(APITestCase):
    def setUp(self):
        self.table_endpoint = reverse('table')

    @patch('tablebuilder.views.call_command')
    def test_new_table_creation(self, mock_call_command):
        """
        Verify if a new table can be created.
        """
        payload = {"name": "Table1", "fields": [
            {"name": "field1", "type": "string"}, {"name": "field2", "type": "number"}]}
        response = self.client.post(
            self.table_endpoint, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DynamicTable.objects.count(), 1)
        self.assertEqual(DynamicTable.objects.get().name, 'Table1')
        for field in response.data['fields']:
            self.assertIsInstance(DynamicField.objects.get(
                name=field['name']), DynamicField)
        mock_call_command.assert_called_once()

    @patch('tablebuilder.views.call_command')
    def test_table_creation_without_name(self, mock_call_command):
        """
        Check if table creation fails when name is not provided.
        """
        payload = {"fields": [{"name": "field1", "type": "string"}, {
            "name": "field2", "type": "number"}]}
        response = self.client.post(
            self.table_endpoint, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_call_command.assert_not_called()

    @patch('tablebuilder.views.call_command')
    def test_table_creation_with_duplicate_name(self, mock_call_command):
        """
        Check if table creation fails when a duplicate name is provided.
        """
        payload = {"name": "Table1", "fields": [
            {"name": "field1", "type": "string"}, {"name": "field2", "type": "number"}]}
        response1 = self.client.post(
            self.table_endpoint, payload, format='json')
        response2 = self.client.post(
            self.table_endpoint, payload, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        mock_call_command.assert_called_once()

    @patch('tablebuilder.views.call_command')
    def test_existing_table_update(self, mock_call_command):
        """
        Verify if an existing table can be updated.
        """
        # Initial table creation
        payload = {"name": "Table1", "fields": [
            {"name": "field1", "type": "string"}, {"name": "field2", "type": "number"}]}
        response = self.client.post(
            self.table_endpoint, payload, format='json')
        table_id = response.data['id']

        # Updating the created table
        updated_payload = {"name": "Table1_updated", "fields": [
            {"name": "field1", "type": "string"}, {"name": "field3", "type": "boolean"}]}
        response = self.client.put(reverse('table_detail', kwargs={
            'id': table_id}), updated_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        table = DynamicTable.objects.get()
        self.assertEqual(table.name, 'Table1_updated')
        fields = {field.name: field.type for field in table.fields.all()}
        expected_fields = {"field1": "string", "field3": "boolean"}
        self.assertEqual(fields, expected_fields)
        mock_call_command.assert_called()

    @patch('tablebuilder.views.call_command')
    def test_nonexistent_table_update(self, mock_call_command):
        """
        Verify if updating a nonexistent table fails.
        """
        updated_payload = {"name": "Table1_updated", "fields": [
            {"name": "field1", "type": "string"}, {"name": "field3", "type": "boolean"}]}
        response = self.client.put(reverse('table_detail', kwargs={
            'id': 9999}), updated_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_call_command.assert_not_called()


class RowViewTestCase(APITestCase):
    def setUp(self):
        self.table_payload = {"name": "Table1", "fields": [
            {"name": "field1", "type": "string"}, {"name": "field2", "type": "number"}]}
        self.table_response = self.client.post(
            reverse('table'), self.table_payload, format='json')
        self.table_id = self.table_response.data['id']
        self.row_endpoint = reverse('table_row', kwargs={'id': self.table_id})

    def test_add_row_to_existing_table(self):
        """
        Verify if a row can be added to an existing table.
        """
        row_payload = {"field1": "hello", "field2": 42}
        response = self.client.post(
            self.row_endpoint, row_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
