from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Message
from .signals import conversation_ended

class MessageAdmin(admin.ModelAdmin):
    """Custom admin interface for Message model"""
    
    list_display = [
        'id', 'role_badge', 'content_preview', 'created_at', 
        'message_length', 'time_ago'
    ]
    list_filter = [
        'role', 
        'created_at',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = ['content', 'role']
    readonly_fields = ['created_at', 'message_length', 'word_count']
    ordering = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Message Information', {
            'fields': ('role', 'content', 'created_at')
        }),
        ('Statistics', {
            'fields': ('message_length', 'word_count'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'export_messages', 
        'delete_old_messages', 
        'mark_as_important',
        'generate_conversation_report'
    ]
    
    def role_badge(self, obj):
        """Display role as a colored badge"""
        colors = {
            'user': '#667eea',
            'assistant': '#10b981'
        }
        color = colors.get(obj.role, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.role.title()
        )
    role_badge.short_description = 'Role'
    role_badge.admin_order_field = 'role'
    
    def content_preview(self, obj):
        """Show a preview of the message content"""
        preview = obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return format_html('<div style="max-width: 300px;">{}</div>', preview)
    content_preview.short_description = 'Content Preview'
    
    def message_length(self, obj):
        """Display message length"""
        return f"{len(obj.content)} characters"
    message_length.short_description = 'Length'
    
    def word_count(self, obj):
        """Calculate word count"""
        return len(obj.content.split())
    word_count.short_description = 'Words'
    
    def time_ago(self, obj):
        """Show how long ago the message was created"""
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    time_ago.short_description = 'Time Ago'
    time_ago.admin_order_field = 'created_at'
    
    def export_messages(self, request, queryset):
        """Export selected messages to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="messages_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Role', 'Content', 'Created At', 'Length'])
        
        for message in queryset:
            writer.writerow([
                message.id,
                message.role,
                message.content,
                message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                len(message.content)
            ])
        
        messages.success(request, f"Exported {queryset.count()} messages to CSV")
        return response
    export_messages.short_description = "Export selected messages to CSV"
    
    def delete_old_messages(self, request, queryset):
        """Delete messages older than 30 days"""
        cutoff_date = timezone.now() - timedelta(days=30)
        old_messages = queryset.filter(created_at__lt=cutoff_date)
        count = old_messages.count()
        old_messages.delete()
        
        messages.success(request, f"Deleted {count} messages older than 30 days")
    delete_old_messages.short_description = "Delete messages older than 30 days"
    
    def mark_as_important(self, request, queryset):
        """Mark messages as important (custom field would be needed)"""
        # This is a placeholder for a custom action
        messages.info(request, f"Marked {queryset.count()} messages as important")
    mark_as_important.short_description = "Mark as important"
    
    def generate_conversation_report(self, request, queryset):
        """Generate a conversation analysis report"""
        # Count messages by role
        user_count = queryset.filter(role='user').count()
        assistant_count = queryset.filter(role='assistant').count()
        
        # Calculate average message length
        avg_length = queryset.aggregate(avg_length=Count('content'))['avg_length']
        
        report = f"""
        Conversation Report:
        - Total Messages: {queryset.count()}
        - User Messages: {user_count}
        - Assistant Messages: {assistant_count}
        - Average Length: {avg_length} characters
        """
        
        messages.info(request, report)
    generate_conversation_report.short_description = "Generate conversation report"
    
    def get_queryset(self, request):
        """Custom queryset with annotations"""
        qs = super().get_queryset(request)
        return qs.select_related().annotate(
            message_length=Count('content')
        )
    
    def changelist_view(self, request, extra_context=None):
        """Custom changelist view with statistics"""
        extra_context = extra_context or {}
        
        # Get statistics
        total_messages = Message.objects.count()
        user_messages = Message.objects.filter(role='user').count()
        assistant_messages = Message.objects.filter(role='assistant').count()
        
        # Recent activity
        today = timezone.now().date()
        today_messages = Message.objects.filter(
            created_at__date=today
        ).count()
        
        # Messages by hour (last 24 hours)
        from django.db.models.functions import ExtractHour
        last_24h = timezone.now() - timedelta(hours=24)
        hourly_stats = Message.objects.filter(
            created_at__gte=last_24h
        ).annotate(
            hour=ExtractHour('created_at')
        ).values('hour').annotate(count=Count('id')).order_by('hour')
        
        # Add statistics links
        extra_context.update({
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'today_messages': today_messages,
            'hourly_stats': list(hourly_stats),
            'show_statistics_links': True,
        })
        
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        """Add custom URLs"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_site.admin_view(self.statistics_view), name='chatbot_message_statistics'),
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='chatbot_message_analytics'),
        ]
        return custom_urls + urls
    
    def statistics_view(self, request):
        """Custom statistics view"""
        from django.shortcuts import render
        
        # Get various statistics
        total_messages = Message.objects.count()
        user_messages = Message.objects.filter(role='user').count()
        assistant_messages = Message.objects.filter(role='assistant').count()
        today_messages = Message.objects.filter(
            created_at__date=timezone.now().date()
        ).count()
        
        # Calculate average message length properly
        from django.db.models import Avg
        avg_length_result = Message.objects.aggregate(
            avg_length=Avg('content')
        )
        avg_message_length = avg_length_result['avg_length'] or 0
        
        stats = {
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'today_messages': today_messages,
            'avg_message_length': round(avg_message_length, 1),
        }
        
        return render(request, 'admin/chatbot/statistics.html', {
            'stats': stats,
            'title': 'LawBot Statistics',
        })
    
    def analytics_view(self, request):
        """Custom analytics view"""
        from django.shortcuts import render
        
        # Get analytics data
        analytics = {
            'messages_by_day': self.get_messages_by_day(),
            'messages_by_hour': self.get_messages_by_hour(),
            'top_conversations': self.get_top_conversations(),
        }
        
        return render(request, 'admin/chatbot/analytics.html', {
            'analytics': analytics,
            'title': 'LawBot Analytics',
        })
    
    def get_messages_by_day(self):
        """Get message count by day for the last 30 days"""
        from django.db.models.functions import TruncDate
        
        return Message.objects.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('-date')[:30]
    
    def get_messages_by_hour(self):
        """Get message count by hour"""
        from django.db.models.functions import ExtractHour
        
        return Message.objects.annotate(
            hour=ExtractHour('created_at')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
    
    def get_top_conversations(self):
        """Get top conversations by message count"""
        # This would require a conversation model or grouping logic
        return []

# Register with standard Django admin
admin.site.register(Message, MessageAdmin)
