from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from .models import Message
import logging

# Set up logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Message)
def message_post_save(sender, instance, created, **kwargs):
    """Signal handler for when a message is saved"""
    if created:
        logger.info(f"New {instance.role} message created: {instance.content[:50]}...")
        
        # Update cache with latest message count
        cache_key = f"message_count_{instance.role}"
        current_count = cache.get(cache_key, 0)
        cache.set(cache_key, current_count + 1, 3600)  # Cache for 1 hour
        
        # Update total message count
        total_count = cache.get("total_message_count", 0)
        cache.set("total_message_count", total_count + 1, 3600)
        
        # Log conversation statistics
        user_messages = Message.objects.filter(role='user').count()
        assistant_messages = Message.objects.filter(role='assistant').count()
        
        logger.info(f"Conversation stats - User: {user_messages}, Assistant: {assistant_messages}")

@receiver(pre_save, sender=Message)
def message_pre_save(sender, instance, **kwargs):
    """Signal handler for before a message is saved"""
    # Ensure content is not empty
    if not instance.content or instance.content.strip() == "":
        raise ValueError("Message content cannot be empty")
    
    # Truncate content if too long
    if len(instance.content) > 5000:
        instance.content = instance.content[:4997] + "..."
        logger.warning(f"Message content truncated for message ID {instance.id}")

@receiver(post_delete, sender=Message)
def message_post_delete(sender, instance, **kwargs):
    """Signal handler for when a message is deleted"""
    logger.info(f"Message deleted: {instance.role} - {instance.content[:50]}...")
    
    # Update cache counts
    cache_key = f"message_count_{instance.role}"
    current_count = cache.get(cache_key, 0)
    if current_count > 0:
        cache.set(cache_key, current_count - 1, 3600)
    
    total_count = cache.get("total_message_count", 0)
    if total_count > 0:
        cache.set("total_message_count", total_count - 1, 3600)

# Custom signal for conversation events
from django.dispatch import Signal

conversation_started = Signal()
conversation_ended = Signal()
error_occurred = Signal()

@receiver(conversation_started)
def handle_conversation_started(sender, user_message, **kwargs):
    """Handle conversation start events"""
    logger.info(f"New conversation started with message: {user_message[:50]}...")
    
    # You could add analytics tracking here
    # For example, track conversation start times, user behavior, etc.

@receiver(conversation_ended)
def handle_conversation_ended(sender, conversation_length, **kwargs):
    """Handle conversation end events"""
    logger.info(f"Conversation ended with {conversation_length} messages")
    
    # Track conversation metrics
    cache_key = "avg_conversation_length"
    current_avg = cache.get(cache_key, 0)
    total_conversations = cache.get("total_conversations", 0)
    
    if total_conversations > 0:
        new_avg = ((current_avg * total_conversations) + conversation_length) / (total_conversations + 1)
    else:
        new_avg = conversation_length
    
    cache.set(cache_key, new_avg, 3600)
    cache.set("total_conversations", total_conversations + 1, 3600)

@receiver(error_occurred)
def handle_error_occurred(sender, error_type, error_message, **kwargs):
    """Handle error events"""
    logger.error(f"Error occurred - Type: {error_type}, Message: {error_message}")
    
    # Track error statistics
    error_count = cache.get(f"error_count_{error_type}", 0)
    cache.set(f"error_count_{error_type}", error_count + 1, 3600)
