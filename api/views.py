import json
import smtplib
import ssl
import certifi
from rest_framework.views import APIView
from rest_framework import viewsets , status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db import IntegrityError
from email.message import EmailMessage
from .serializers import UserSerializer,ClothesSerializer,SavedSerializer,ExperimentSerializer,FeedbackSerializer,HistorySerializer,BugReportSerializer,ChangePasswordSerializer,CategorySerializer
from .models import Clothes , Saved , Experiment ,History, Feedback,Category
from django.http import FileResponse, Http404


class AuthView(APIView):

    def post(self, request, *args, **kwargs):
        if 'register' in request.path:
            return self.register(request)
        elif 'logout' in request.path:
            return self.logout(request)

    def register (self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "user": serializer.data,
                "refresh_token": str(refresh),
                "access_token": access_token
            }, status=status.HTTP_201_CREATED)
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def logout(self, request):  
        permission_classes = [IsAuthenticated]
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request) 
            return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
        except KeyError:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet (viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ClothesListView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        item_id = request.query_params.get('id')  
        if item_id:
            return self.get_item(request, item_id)

        clothes = Clothes.objects.all()
        serializer = ClothesSerializer(clothes, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        serializer = ClothesSerializer(data = request.data)

        if serializer.is_valid() :
            serializer.save()
            return Response (data=serializer.data, status=status.HTTP_200_OK)
        return Response (serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def get_item(self, request, pk):
        try:
            item = Clothes.objects.get(pk=pk)
        except Clothes.DoesNotExist:
            raise Http404
        
        serializer = ClothesSerializer(item)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
        

class SavedViewSet(viewsets.ModelViewSet):
    serializer_class=SavedSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):

        queryset = Saved.objects.all()
        user = self.request.user
        return queryset.filter(user=user)

    def create(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({"detail": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        
        clothes_id = data["clothes"]
        user = self.request.user

        if not clothes_id:
            return Response({"detail": "cloth_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            clothes=Clothes.objects.get(id=clothes_id)
            save = Saved.objects.create(clothes=clothes, user=user)
            return Response(self.serializer_class(save).data, status=status.HTTP_201_CREATED)
        except Clothes.DoesNotExist:
            return Response({"detail": "Clothes with the given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({"detail": "A saved item with this cloth_id already exists for the user."}, status=status.HTTP_400_BAD_REQUEST)

    def unsave(self, request, *args, **kwargs):

        clothes_id = kwargs.get('pk')
        user = self.request.user
        
        try:
            saved_item = Saved.objects.get(clothes_id=clothes_id, user=user)
            saved_item.delete()
            return Response({"detail": "Item unsaved successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Saved.DoesNotExist:
            return Response({"detail": "Saved item does not exist for the current user."}, status=status.HTTP_404_NOT_FOUND)


class BugReportView(APIView):

    serializer_class=BugReportSerializer
    permission_classes = [IsAuthenticated]

    def post (self, request):
        serializer = self.serializer_class(data=request.data) 
        if serializer.is_valid():
            report = serializer.validated_data['report']
            user_email = request.user.email

            try:
             
                msg = EmailMessage()
                msg.set_content(report)
                msg['Subject'] = "Bug Report"
                msg['from'] = user_email
                msg['To'] = 'projectit2f@gmail.com'
                
                ssl_context = ssl.create_default_context(cafile=certifi.where())

                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls(context=ssl_context)
                    server.login('boustatifarah@gmail.com', 'bceh xtjd gxgd srqa')
                    server.send_message(msg)

                return Response({"message": "Bug report sent successfully!"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):

    serializer_class=ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        
        user = request.user
        
        serializer = self.serializer_class(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({"message": "password changed successfully!"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExperimentViewSet(viewsets.ModelViewSet):
    queryset=Experiment.objects.all()
    serializer_class=ExperimentSerializer
    permission_classes=[IsAuthenticated]


class HistoryView(APIView):
    serializer_class=HistorySerializer
    permission_classes=[IsAuthenticated]

    def get(self,request):
        queryset =History.objects.all()
        user = self.request.user
        queryset = queryset.filter(user=user)
        return Response(queryset, status=status.HTTP_201_CREATED)


class FeedBackViewSet(viewsets.ModelViewSet):
    queryset=Feedback.objects.all()
    serializer_class=FeedbackSerializer
    permission_classes=[IsAuthenticated] 


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAuthenticated] 

    @action(detail=True, methods=['get'], url_path='clothes')
    def clothes_by_category(self, request, pk):
        category = self.get_object()  
        clothes = Clothes.objects.filter(category=category)  
        serializer = ClothesSerializer(clothes, many=True)  
        return Response(serializer.data,status=status.HTTP_201_CREATED) 


class DownloadView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, pk):
        try:
            experiment = Experiment.objects.get(pk=pk)
    
            image_file = open(experiment.image_url.path, 'rb')

            return FileResponse(image_file, as_attachment=True, filename=f"{experiment.name}.jpg")

        except Clothes.DoesNotExist:
            raise Http404("Clothing item not found.")

        except Exception as e:
            return Response({"error": str(e)}, status=500)

