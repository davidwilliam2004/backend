from django.shortcuts import render
import requests
import uuid
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from groq import Groq
from django.conf import settings
import os
from django.contrib.auth import authenticate
from .models import Message
from .serializers import MessageSerializer, UserSerializer
from .translation import  translate_to_tamil,clean_text
import json

GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/v1/chat/completions"


@api_view(["POST"])
def signup(request):
    username = request.data.get("username")
    email = request.data.get("email")
    if User.objects.filter(username=username).exists():
        return Response(
            {"message": "Username already exists!"}, status=status.HTTP_400_BAD_REQUEST
        )
    if User.objects.filter(email=email).exists():
        return Response(
            {"message": "Email already exists!"}, status=status.HTTP_400_BAD_REQUEST
        )
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data["password"])  # Hash password
        user.save()
        token = Token.objects.create(user=user)
        return Response(
            {
                "message": "Account created!",
                "token": token.key,
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = authenticate(username=username, password=password)  # Authenticate properly
    if user is None:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )
    token, _ = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response(
        {"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat_with_ai(request):

    user_message = request.data.get("message")
    language = request.data.get("language", "en")
    if not user_message:
        return JsonResponse({"error": "Message is required"}, status=400)
    system_prompt = f"""
                    You are a multilingual AI guide for Tamil Nadu's heritage sites.
                    Respond only to heritage-related queries. Provide accurate, engaging responses.
                    Your name is ARV-GPT
                    you have developed by David William.
                    **Guidelines:**
                    1. **Simplify complex history** into easy-to-understand language.
                    2. **Format Responses:** Use **bold** for key points and bullet lists for clarity.
                    3. **Engage with stories & myths** where relevant.
                    4. **Get maximum 300 characters** do not give too much.
                    5. **Response relevant query only** if query have other than your role response as a **No idea about the query**
                    6. ** if query asked in tamil reply in english**
                    7. ** if any vulger question asked in tamil or english ** give this angry emoji
                    \n
                    user query : {user_message}
                """

    client = Groq(api_key="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")
                #    8. ** you want give response only in the format of json**
                #     output format : {{"response":"your-full-response","hastag":"get-important-keywords"}}
    try:
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": system_prompt}],
            model="llama-3.1-8b-instant",
        )
        ai_response = chat_completion.choices[0].message.content
        # unique_id = uuid.uuid4().hex
        # english_audio_filename = f"english_{unique_id}.mp3"
        # tamil_audio_filename = f"tamil_{unique_id}.mp3"
        if language == "ta":
            tamil_text = translate_to_tamil(ai_response)
            # audio_path = text_to_speech(tamil_text, lang="ta", filename=tamil_audio_filename)
            return JsonResponse({"response": tamil_text})
        else:
            # audio_path = text_to_speech(clean_english, lang="en", filename=english_audio_filename)
            return JsonResponse({"response": ai_response})

    except Exception as e:
        return JsonResponse({"error": f"Groq API Error: {str(e)}"}, status=500)
