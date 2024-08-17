from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Clothes,Saved,Experiment,History,Feedback,Category

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username','email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            validated_data.pop('password')
        return super().update(instance, validated_data)


class ClothesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Clothes 
        fields = '__all__' 


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category 
        fields = '__all__' 


class SavedSerializer(serializers.ModelSerializer):
    
    user=UserSerializer(read_only=True)
    Clothes=ClothesSerializer(read_only=True)

    class Meta:
        model=Saved
        fields='__all__' 


class BugReportSerializer(serializers.Serializer):
    report = serializers.CharField(max_length=1000)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        validate_password(data['new_password'], self.instance)
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct."})
        return value
    
   
class ExperimentSerializer(serializers.ModelSerializer):

    models_photo_path=serializers.ImageField(read_only=True)

    class Meta:
        model=Experiment
        fields=['id','user_photo_path',"clothes_photo_path",'models_photo_path']

    
class HistorySerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    experiment=ExperimentSerializer(read_only=True)
    class Meta:
        model=History
        fields=["id","user","experiment","Created_at"]


class FeedbackSerializer(serializers.ModelSerializer):
    experiment = serializers.PrimaryKeyRelatedField(queryset=Clothes.objects.all())
    def validate(self, data):
        if data['rate'] > 5 or data['rate'] < 0 :
            raise serializers.ValidationError({"rate": "invalid data"})
        return data

    class Meta:
        model=Feedback
        fields=['id','experiment','rate','description']


