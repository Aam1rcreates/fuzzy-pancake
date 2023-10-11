from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from .views import TaskDetail

# Create your tests here.



class TaskDetailTestCase(TestCase):
    def setUp(self):
        self.task = Task.objects.create(title="Test Task")
        self.factory = APIRequestFactory()
        self.view = TaskDetail.as_view()

    def test_get_existing_task(self):
        request = self.factory.get(f'/tasks/{self.task.pk}/')
        response = self.view(request, pk=self.task.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, TaskSerializer(self.task).data)

    def test_get_nonexistent_task(self):
        non_existent_pk = 9999
        request = self.factory.get(f'/tasks/{non_existent_pk}/')
        response = self.view(request, pk=non_existent_pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_existing_task(self):
        updated_data = {"title": "Updated Task Title"}
        request = self.factory.put(f'/tasks/{self.task.pk}/', updated_data, format='json')
        response = self.view(request, pk=self.task.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()  # Refresh the task from the database
        self.assertEqual(self.task.title, updated_data["title"])

    def test_update_nonexistent_task(self):
        non_existent_pk = 9999
        updated_data = {"title": "Updated Task Title"}
        request = self.factory.put(f'/tasks/{non_existent_pk}/', updated_data, format='json')
        response = self.view(request, pk=non_existent_pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_with_invalid_data(self):
        invalid_data = {"title": ""}  # An empty title is invalid
        request = self.factory.put(f'/tasks/{self.task.pk}/', invalid_data, format='json')
        response = self.view(request, pk=self.task.pk)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_task(self):
        request = self.factory.delete(f'/tasks/{self.task.pk}/')
        response = self.view(request, pk=self.task.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Ensure the task has been deleted from the database
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(pk=self.task.pk)

    def test_delete_nonexistent_task(self):
        non_existent_pk = 9999
        request = self.factory.delete(f'/tasks/{non_existent_pk}/')
        response = self.view(request, pk=non_existent_pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

