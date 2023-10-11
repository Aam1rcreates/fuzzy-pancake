from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from .serializers import UserSerializer
from .serializers import TaskSerializer
from .models import Task
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            # serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return Response({'message': 'User registered successfully.', 'username': user.username, 'access_token': access_token})
            
            return Response({'message': 'Something went wrong!'})
        except Exception as e:
            print(e)
            Response({ 'Error': e })

class LoginView(APIView):
    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']
            user = User.objects.filter(username=username).first()
            if user is None or not user.check_password(password):
                return Response({'error': 'Invalid credentials'})
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({'message': 'User logged in successfully.', 'access_token': access_token})
        except Exception as e:
            print(e)
            Response({ 'Error': e })

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
class TaskList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'status', 'due_date']
    ordering_fields = ['title','due_date']
    search_fields = ['title', 'description', 'due_date']

    def post(self, request):
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetail(APIView):
    """
    Retrieve, update or delete a task.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        task = self.get_object(pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = self.get_object(pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_object(pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)