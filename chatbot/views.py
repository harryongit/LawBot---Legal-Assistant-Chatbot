import os, requests
from django.shortcuts import render, redirect
from .models import Message
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .serializers import (
    MessageSerializer, 
    ChatRequestSerializer, 
    ChatResponseSerializer, 
    ErrorResponseSerializer
)
from .signals import conversation_started, conversation_ended, error_occurred
import json


OPENAI_API_KEY = settings.OPENAI_API_KEY

class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model with full CRUD operations"""
    queryset = Message.objects.all().order_by('created_at')
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter messages by role if specified"""
        queryset = Message.objects.all().order_by('created_at')
        role = self.request.query_params.get('role', None)
        if role is not None:
            queryset = queryset.filter(role=role)
        return queryset

def chat_view(request):
    """Main chat view for the web interface"""
    if request.method == "POST":
        user_input = request.POST.get("message", "").strip()
        if user_input:
            # Save user message
            user_message = Message.objects.create(role="user", content=user_input)

            # Check if API key is configured
            if not OPENAI_API_KEY:
                error_msg = "OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable."
                Message.objects.create(role="assistant", content=error_msg)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': error_msg})
                return redirect("chat")

            # Get AI response with external APIs only
            ai_response = get_ai_response_external_only(user_input)
            
            if ai_response.get('success'):
                # Save assistant message
                assistant_message = Message.objects.create(
                    role="assistant", 
                    content=ai_response['response']
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'response': ai_response['response'],
                        'message_id': assistant_message.id
                    })
            else:
                # Save error message
                error_message = Message.objects.create(
                    role="assistant", 
                    content=ai_response['error']
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': ai_response['error'],
                        'error_type': ai_response.get('error_type', 'api_error')
                    })

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'No message provided'})
        return redirect("chat")

    messages = Message.objects.all().order_by('created_at')
    return render(request, "index.html", {"messages": messages})

def api_docs_view(request):
    """API documentation view"""
    return render(request, "api_docs.html")

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_api(request):
    """REST API endpoint for chat functionality"""
    # Validate request data
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        error_serializer = ErrorResponseSerializer({
            'error': 'Invalid request data',
            'error_type': 'validation_error'
        })
        return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
    
    user_input = serializer.validated_data['message']
    
    # Check if API key is configured
    if not OPENAI_API_KEY:
        error_serializer = ErrorResponseSerializer({
            'error': 'OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable.',
            'error_type': 'configuration_error'
        })
        return Response(error_serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Save user message
    user_message = Message.objects.create(role="user", content=user_input)
    
    # Get AI response with external APIs only
    ai_response = get_ai_response_external_only(user_input)
    
    if ai_response.get('success'):
        # Save assistant message
        assistant_message = Message.objects.create(
            role="assistant", 
            content=ai_response['response']
        )
        
        # Return success response
        response_serializer = ChatResponseSerializer({
            'response': ai_response['response'],
            'message_id': assistant_message.id
        })
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    else:
        # Save error message
        error_message = Message.objects.create(
            role="assistant", 
            content=ai_response['error']
        )
        
        # Return error response
        error_serializer = ErrorResponseSerializer({
            'error': ai_response['error'],
            'error_type': ai_response.get('error_type', 'api_error')
        })
        return Response(error_serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def messages_api(request):
    """REST API endpoint to get all messages"""
    messages = Message.objects.all().order_by('created_at')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def get_ai_response_external_only(user_input):
    """Get AI response using only external APIs"""
    
    # Try OpenAI API first
    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith('sk-or-'):
        response = try_openai_api(user_input)
        if response.get('success'):
            return response
    
    # Try OpenRouter API second
    if OPENAI_API_KEY and OPENAI_API_KEY.startswith('sk-or-'):
        response = try_openrouter_api(user_input)
        if response.get('success'):
            return response
    
    # Try alternative OpenAI models
    if OPENAI_API_KEY:
        response = try_alternative_openai_api(user_input)
        if response.get('success'):
            return response
    
    # All external APIs failed
    error_msg = "All external AI services are currently unavailable. Please check your API key configuration or try again later."
    error_occurred.send(
        sender=get_ai_response_external_only,
        error_type='all_apis_failed',
        error_message=error_msg
    )
    return {
        'success': False, 
        'error': error_msg,
        'error_type': 'all_apis_failed'
    }

def try_openai_api(user_input):
    """Try OpenAI API"""
    try:
        # Build conversation
        messages_for_gpt = [{"role": m.role, "content": m.content} for m in Message.objects.all()]

        # Add system prompt
        system_prompt = {
            "role": "system",
            "content": (
                "You are a legal assistant. Provide general legal information, "
                "but always say: 'This is not legal advice.'"
            ),
        }
        messages_for_gpt.insert(0, system_prompt)

        # Call OpenAI API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages_for_gpt,
            "max_tokens": 500,
            "temperature": 0.2
        }
        
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions", 
            headers=headers, 
            json=payload, 
            timeout=30
        )
        
        if resp.status_code == 200:
            reply_text = resp.json()["choices"][0]["message"]["content"]
            return {'success': True, 'response': reply_text}
        elif resp.status_code == 401:
            error_msg = "Invalid OpenAI API key. Please check your API key configuration."
            error_occurred.send(
                sender=try_openai_api,
                error_type='auth_error',
                error_message=error_msg
            )
            return {'success': False, 'error': error_msg, 'error_type': 'auth_error'}
        elif resp.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."
            error_occurred.send(
                sender=try_openai_api,
                error_type='rate_limit',
                error_message=error_msg
            )
            return {'success': False, 'error': error_msg, 'error_type': 'rate_limit'}
        else:
            error_msg = f"OpenAI API Error (Status {resp.status_code}): {resp.text}"
            error_occurred.send(
                sender=try_openai_api,
                error_type='api_error',
                error_message=error_msg
            )
            return {'success': False, 'error': error_msg, 'error_type': 'api_error'}
            
    except requests.exceptions.Timeout:
        error_msg = "OpenAI API request timed out. Please try again."
        return {'success': False, 'error': error_msg, 'error_type': 'timeout'}
    except requests.exceptions.RequestException as e:
        error_msg = f"OpenAI API network error: {str(e)}"
        return {'success': False, 'error': error_msg, 'error_type': 'network_error'}
    except Exception as e:
        error_msg = f"OpenAI API error: {str(e)}"
        return {'success': False, 'error': error_msg, 'error_type': 'api_error'}

def try_openrouter_api(user_input):
    """Try OpenRouter API"""
    try:
        # Build conversation
        messages_for_gpt = [{"role": m.role, "content": m.content} for m in Message.objects.all()]

        # Add system prompt
        system_prompt = {
            "role": "system",
            "content": (
                "You are a legal assistant. Provide general legal information, "
                "but always say: 'This is not legal advice.'"
            ),
        }
        messages_for_gpt.insert(0, system_prompt)

        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:9000",
            "X-Title": "LawBot"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages_for_gpt,
            "max_tokens": 500,
            "temperature": 0.2
        }
        
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", 
            headers=headers, 
            json=payload, 
            timeout=30
        )
        
        if resp.status_code == 200:
            reply_text = resp.json()["choices"][0]["message"]["content"]
            return {'success': True, 'response': reply_text}
        elif resp.status_code == 401:
            error_msg = "Invalid OpenRouter API key. Please check your API key configuration."
            error_occurred.send(
                sender=try_openrouter_api,
                error_type='auth_error',
                error_message=error_msg
            )
            return {'success': False, 'error': error_msg, 'error_type': 'auth_error'}
        elif resp.status_code == 429:
            error_msg = "OpenRouter rate limit exceeded. Please try again later."
            error_occurred.send(
                sender=try_openrouter_api,
                error_type='rate_limit',
                error_message=error_msg
            )
            return {'success': False, 'error': error_msg, 'error_type': 'rate_limit'}
        else:
            error_msg = f"OpenRouter API Error (Status {resp.status_code}): {resp.text}"
            error_occurred.send(
                sender=try_openrouter_api,
                error_type='api_error',
                error_message=error_msg
            )
            return {'success': False, 'error': error_msg, 'error_type': 'api_error'}
            
    except requests.exceptions.Timeout:
        error_msg = "OpenRouter API request timed out. Please try again."
        return {'success': False, 'error': error_msg, 'error_type': 'timeout'}
    except requests.exceptions.RequestException as e:
        error_msg = f"OpenRouter API network error: {str(e)}"
        return {'success': False, 'error': error_msg, 'error_type': 'network_error'}
    except Exception as e:
        error_msg = f"OpenRouter API error: {str(e)}"
        return {'success': False, 'error': error_msg, 'error_type': 'api_error'}

def try_alternative_openai_api(user_input):
    """Try alternative OpenAI models"""
    try:
        # Build conversation
        messages_for_gpt = [{"role": m.role, "content": m.content} for m in Message.objects.all()]

        # Add system prompt
        system_prompt = {
            "role": "system",
            "content": (
                "You are a legal assistant. Provide general legal information, "
                "but always say: 'This is not legal advice.'"
            ),
        }
        messages_for_gpt.insert(0, system_prompt)

        # Try different models
        models_to_try = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        for model in models_to_try:
            try:
                payload = {
                    "model": model,
                    "messages": messages_for_gpt,
                    "max_tokens": 500,
                    "temperature": 0.2
                }
                
                resp = requests.post(
                    "https://api.openai.com/v1/chat/completions", 
                    headers=headers, 
                    json=payload, 
                    timeout=30
                )
                
                if resp.status_code == 200:
                    reply_text = resp.json()["choices"][0]["message"]["content"]
                    return {'success': True, 'response': reply_text}
                elif resp.status_code == 401:
                    continue  # Try next model
                elif resp.status_code == 429:
                    continue  # Try next model
                    
            except Exception:
                continue  # Try next model
                
        return {'success': False, 'error': "All OpenAI models failed"}
        
    except Exception as e:
        return {'success': False, 'error': f"Alternative OpenAI Error: {str(e)}"}

# Keep the old function for backward compatibility
def get_ai_response(user_input):
    """Legacy function - now uses external APIs only"""
    return get_ai_response_external_only(user_input)
