from django.db import models
from django.contrib.auth.models import User
from django.db import models
import llm
from core.serializers import TaskSerializer


class Category(models.Model):
    # groceries, home maintenance, medical, etc...
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Status(models.Model):
    # pending, in progress, completed, cancelled...
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    # Use ForeignKey to the Status table
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)

    time_estimation = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    cost_estimation = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    proposed_location = models.CharField(max_length=255, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status.name if self.status else 'No Status'}"


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed_content = models.JSONField(null=True, blank=True)  # Use JSONField for processed content
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)

    def process_message(self):
        # Assuming you have a function `process_with_llm()` that processes
        # the message content and returns a JSON object
        processed_data = llm.process_with_llm(self.content)

        # Save the processed JSON in the `processed_content` field
        self.processed_content = processed_data
        self.save()

        # Create a Task using a serializer
        self.create_task_from_processed_data(processed_data)

    def create_task_from_processed_data(self, data):
        # Prepare data for task creation with user and processed data
        task_data = {
            'user': self.user.id,
            'title': data.get('title', 'Untitled Task'),
            'description': data.get('description', ''),
            'category': data.get('category'),
            'status': data.get('status'),
            'time_estimation': data.get('time_estimation'),
            'cost_estimation': data.get('cost_estimation'),
            'proposed_location': data.get('proposed_location', '')
        }

        task_serializer = TaskSerializer(data=task_data)

        if task_serializer.is_valid():
            task_serializer.save()
        else:
            # Handle errors or log them
            print(task_serializer.errors)


class ProcessedMessageLog(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_parsed_successfully = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    quality_label = models.IntegerField(null=True, blank=True)  # Example label field
    created_at = models.DateTimeField(auto_now_add=True)
