from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Client, Project
from .serializers import ClientSerializer, AssignedProjectSerializer, ProjectSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def client_list_create(request):
    if request.method == 'GET':
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'GET':
        serializer = ClientSerializer(client)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project_for_client(request, pk):
    try:
        client = Client.objects.get(pk=pk)  
    except Client.DoesNotExist:
        return Response({'detail': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

    project_name = request.data.get('project_name')
    users_data = request.data.get('users', [])

    project = Project.objects.create(project_name=project_name, client=client, created_by=request.user)

    user_ids = [user['id'] for user in users_data] 
    users = User.objects.filter(id__in=user_ids) 
    project.users.set(users) 
    project.save()

    return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_assigned_projects(request):
    projects = Project.objects.all()
    serializer = AssignedProjectSerializer(projects, many=True)
    return Response(serializer.data)
