from django.contrib.auth import user_logged_in

# Create your views here.
from django.http import HttpRequest
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from jwtauth.models import RefreshToken
from jwtauth.utils import *

from accounts.models import User
from accounts.serializer import UserSerializer
from profilesettings.models import ProfileSettings, Avatar
from profilesettings.serializer import ProfileSettingsSerializer
from statistic.models import UserStatistics, Followers
from statistic.serializer import UserStatisticsSerializer


@api_view(['GET', 'POST'])
def profile(request: Request):
    """взаоимоддействие с профилем пользователя"""
    if request.method == 'POST':
        user_id = request.data.get('id')
        print('POST')
    else:
        access_token = request.headers.get('Access-Token')
        user_id = get_user_id_from_payload(access_token)

    profile_settings = ProfileSettings.objects.get(id=user_id)
    avatar = Avatar.objects.get(id=profile_settings)
    user_statistics = UserStatistics.objects.get(id=user_id)

    profile_settings_serializer = ProfileSettingsSerializer(profile_settings)
    user_statistics_serializer = UserStatisticsSerializer(user_statistics)

    profile_data = {
        'profile_settings': profile_settings_serializer.data,
        'avatar_url': avatar.url,
        'user_statistics': user_statistics_serializer.data
    }

    return Response(profile_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def follow(request: Request):
    """Оформление подпискаи"""
    to_follow_id = request.data.get('id')
    access_token = request.headers.get('Access-Token')

    to_follow_user = User.objects.get(id=to_follow_id)
    follower = get_user_id_from_payload(access_token)
    follower_user = User.objects.get(id=follower)

    chain = Followers(user_id=to_follow_user, follower_id=follower_user)
    chain.save()

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def register(request: Request):
    """Регистрация пользовтеля"""
    user = request.data.get('user')
    serializer = UserSerializer(data=user)
    if serializer.is_valid():
        saved_user: User = serializer.save()
        UserStatistics.objects.create(id=saved_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response('User already register!', status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request: Request):
    """Метод для аутентификация пользователя"""
    try:
        login = request.data.get('login')
        password = request.data.get('password')
        user = User.objects.get(login=login, password=password)
        if user:
            user_details = set_tokens_to_response(user)
            data = {'id': user.id}
            return Response(data, headers=user_details, status=status.HTTP_200_OK)
        else:
            res = {'error': 'can not authenticate with the given credentials or the account has been deactivated'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'error': 'please provide a email and a password'}
        return Response(res)
