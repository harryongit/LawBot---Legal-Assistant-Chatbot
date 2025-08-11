from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000, min_length=1)

class ChatResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    message_id = serializers.IntegerField()

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()
    error_type = serializers.CharField(required=False)
