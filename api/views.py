# from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def hello(request):
    return Response(
        {
            "message": "Hello from Django Backend!",
            "status": "API is working",
            "version": "1.0.0",
        }
    )


@api_view(["GET"])
def health(request):
    return Response({"status": "healthy", "database": "connected"})
