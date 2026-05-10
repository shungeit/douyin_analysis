from rest_framework import serializers

from video.models import CommentData, User, VideoData


class VideoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoData
        fields = '__all__'


class CommentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentData
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'createTime']
