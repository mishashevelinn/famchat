from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Message, Category, Status, Task


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name', 'description']


class TaskSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all()
    )
    status = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Status.objects.all()
    )

    class Meta:
        model = Task
        fields = [
            'id', 'user', 'title', 'description', 'category', 'status',
            'time_estimation', 'cost_estimation', 'proposed_location',
            'date_created', 'date_updated'
        ]
