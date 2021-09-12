import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from Tik_Tok import settings
from accounts.models import User
from jwtauth.utils import get_user_id_from_payload
from profilesettings.models import ProfileSettings
from statistic.models import VideoStatistics, VideoComments, Hashtags, HashtagsOnVideo
from video.models import Audio, Video
from rest_framework import viewsets

from video.serializer import VideoSerializer

class VideoViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = VideoSerializer
    queryset = Video.objects.all()
    lookup_field = 'id'
    model = Video

    def get_permissions(self):
        if self.action in ('like_video', 'add_comments', 'like_comments'):
            self.permission_classes = [permissions.IsAuthenticated, ]
        return super().get_permissions()


    @action(methods=['POST'])
    def like_video(request: Request):
        video_id = request.data.get('video_id')
        video_statistics = VideoStatistics.objects.get(id=video_id)
        video_statistics.likes += 1
        video_statistics.save()

        return Response({'likes': video_statistics.likes}, status=status.HTTP_200_OK)

    #
    @action(methods=['POST'])
    def get_audio(request: Request):
        video = Video.objects.get(video_id=request.data.get('video_id'))
        audio = Audio.objects.get(audio_id=video.audio_id.audio_id)
        print(audio)
        data = {}
        data[0] = {
            'author_name': audio.author_name,
            'audio_name': audio.name
        }

        audio = Audio.objects.filter(name=audio.name)
        j = 1
        for i in audio:
            print(i.audio_id)
            video_db = Video.objects.get(audio_id=i.audio_id)
            video = {
                'url': video_db.url,
                'id': video_db.video_id,
            }
            data[j] = video
            j+=1

        print(data)

        return Response(data, status=status.HTTP_200_OK)

    # встраивание переменной
    @action(methods=['POST'])
    def add_comments(request: Request):
        # video_id = request.data.get('id')
        access_token = request.headers.get('Access-Token')
        user_id = get_user_id_from_payload(access_token)
        comment = request.data.get('comment')
        username = ProfileSettings.objects.get(id=user_id).username
        video = Video.objects.get(video_id=request.data.get('id'))
        comment_instance = VideoComments(video_id=video, username=username, comment=comment)
        comment_instance.save()
        return Response(status=status.HTTP_200_OK)


    @action(methods=['POST'])
    def get_video_with_hashtags(request: Request):
        hashtag = request.data.get('hashtags')
        video_ids = HashtagsOnVideo.objects.filter(hashtag=hashtag)
        data = {}
        for i in range(video_ids.__len__()):

            video = {
                'url': Video.objects.get(video_id=video_ids[i].video_id.id.video_id).url,
                'id': Video.objects.get(video_id=video_ids[i].video_id.id.video_id).video_id
            }

            data[i] = video
        print(data)
        return Response(data, status=status.HTTP_200_OK)


    # встраивание переменной
    # мертвый код
    @action(methods=['POST'])
    def get_comments(request: Request):
        # video_id = request.data.get('id')
        data = {}
        comments = VideoComments.objects.filter(video_id=request.data.get('id'))
        j = 0
        for i in comments:
            comment = {
                'username': i.username,
                'date_of_published': i.date_of_published,
                'likes': i.likes,
                'comments': i.comment,
                'id': i.id
            }
            data[j] = comment
            j += 1

        return Response(data, status=status.HTTP_200_OK)

    @action(['PUT'])
    def like_comments(request: Request):
        comment_id = request.data.get('id')
        comment = VideoComments.objects.get(id=comment_id)
        comment.likes += 1
        comment.save()
        return Response(status=status.HTTP_200_OK)