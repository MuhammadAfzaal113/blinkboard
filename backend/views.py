import datetime
import json
import time
import uuid

from django.contrib.auth import authenticate, login
from django.forms import model_to_dict
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import User, Friends

import json
from datetime import datetime


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def get_user_attribute(user, friend, attribute):
    return getattr(friend.from_user if friend.from_user != user else friend.to_user, attribute)


def get_all_friends(user):
    # Retrieve friends where the user is the sender (from_user) and the request is accepted
    sent_and_accepted = Friends.objects.filter(from_user=user, status='Accepted')

    # Retrieve friends where the user is the receiver (to_user) and the request is accepted
    received_and_accepted = Friends.objects.filter(to_user=user, status='Accepted')
    # Combine both sets of friends
    all_friends = sent_and_accepted | received_and_accepted

    return all_friends


def get_friends(user):
    # Retrieve friends where the user is the sender (from_user) and the request is accepted
    sent_and_accepted = Friends.objects.filter(from_user=user)

    # Retrieve friends where the user is the receiver (to_user) and the request is accepted
    received_and_accepted = Friends.objects.filter(to_user=user)

    # Combine both sets of friends
    all_friends = sent_and_accepted | received_and_accepted

    return all_friends


@csrf_exempt
@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    elif request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            context = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'location': user.location,
                    'bio': user.bio,
                    'quote': user.quote,
                    'avatar': user.avatar if user.avatar else None,
                    'blink_board': user.blink_board,
                    'blink_board_image': user.blink_board_image,
                    'updated_at': user.updated_at

                },
                'access_token': access_token,
            }

            # return Response(context)
            # session_id = str(user.id)

            # Render the desired template, for example 'homeProfile.html'
            response = render(request, 'homeProfile.html', context)
            # response.set_cookie('access_token', access_token)
            response.set_cookie('access_token', access_token)
            response.set_cookie(f'user_id_{user.id}', user.id)

            return response
        else:
            return render(request, 'loginFailed.html')


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def sign_up(request):
    if request.method == 'GET':
        return render(request, 'signup.html')

    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(email=email).exists():
            return HttpResponseBadRequest('Email already exists. Please choose a different Email.')

        if User.objects.filter(username=username).exists():
            return HttpResponseBadRequest('Username already exists. Please choose a different Username.')
        User.objects.create_user(email=email, username=username, password=password)
        return render(request, 'NewUserLogin.html')


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def update_user(request):
    # if request.method == 'GET':
    #     try:
    #         user = request.user
    #         return render(request, 'homeProfile.html', {'user': user})
    #     except Exception as e:
    #         return render(request, 'login.html')

    if request.method == 'POST':
        try:
            user = request.user
            if user.is_authenticated:
                location = request.data.get("location", None)

                bio = request.data.get("bio", None)
                quote = request.data.get("quote", None)
                if location and len(location) > 0:
                    user.location = location

                if bio and len(bio) > 0:
                    user.bio = bio
                if quote and len(quote) > 0:
                    user.quote = quote

                avatar_file = request.FILES.get('avatar')
                if avatar_file:
                    if avatar_file.size > 0:
                        user.avatar.save(avatar_file.name, avatar_file, save=True)
                    else:
                        print("Uploaded file is empty.")

                blink_board = request.data.get('blink_board', None)
                if blink_board and len(blink_board) > 0:
                    user.blink_board = blink_board
                    user.updated_at = datetime.now()

                avatar_file = request.FILES.get('blink_board_image')
                if avatar_file:
                    if avatar_file.size > 0:
                        user.blink_board_image.save(avatar_file.name, avatar_file, save=True)
                    else:
                        print("Uploaded file is empty.")
                user.save()
                user = model_to_dict(user)
                return JsonResponse({'user': user, 'success': True})
                # return render(request, 'homeProfile.html', context={'user': user})
            else:
                print("User not authenticated!")
                return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        except Exception as e:
            return render(request, 'login.html')


def get_neighbourhood_context(user):
    pending_request = Friends.objects.filter(to_user=user, status='Pending')
    # accepted_request = get_all_friends(user)
    sent_and_accepted = Friends.objects.filter(from_user=user, status='Accepted')

    # Retrieve friends where the user is the receiver (to_user) and the request is accepted
    received_and_accepted = Friends.objects.filter(to_user=user, status='Accepted')

    neighbour_list = [{'username': neighbour.to_user.username,
                       'avatar': neighbour.to_user.avatar.url if neighbour.to_user.avatar else None,
                       'blink_board': neighbour.to_user.blink_board,
                       'blink_board_image': neighbour.to_user.blink_board_image.url if neighbour.to_user.blink_board_image else None,
                       'updated_at': neighbour.to_user.updated_at,
                       'location': neighbour.to_user.location if neighbour.to_user.location else "",
                       'bio': neighbour.to_user.bio if neighbour.to_user.bio else "",
                       'quote': neighbour.to_user.quote if neighbour.to_user.quote else ""} for neighbour in
                      sent_and_accepted]

    neighbour_list.extend([{'username': neighbour.from_user.username,
                            'avatar': neighbour.from_user.avatar.url if neighbour.from_user.avatar else None,
                            'blink_board': neighbour.from_user.blink_board,
                            'blink_board_image': neighbour.from_user.blink_board_image.url if neighbour.from_user.blink_board_image else None,
                            'updated_at': neighbour.from_user.updated_at,
                            'location': neighbour.from_user.location if neighbour.from_user.location else "",
                            'bio': neighbour.from_user.bio if neighbour.from_user.bio else "",
                            'quote': neighbour.from_user.quote if neighbour.from_user.quote else ""} for neighbour in
                           received_and_accepted])

    pending_list = [{'username': neighbour.from_user.username,
                     'avatar': neighbour.from_user.avatar.url if neighbour.from_user.avatar else None,
                     'blink_board': neighbour.from_user.blink_board,
                     'blink_board_image': neighbour.from_user.blink_board_image.url if neighbour.from_user.blink_board_image else None,
                     'updated_at': neighbour.from_user.updated_at} for neighbour in
                    pending_request]

    context = {
        'accepted_neighbourhoods': neighbour_list,
        'pending_neighbourhoods': pending_list,
        'neighbours': json.dumps(neighbour_list, cls=CustomJSONEncoder)
    }
    return context


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def neighbourhood(request):
    if request.method == 'GET':
        try:
            access_token = request.GET.get('access_token')
            # decoded_token = AccessToken(access_token)

            user = User.objects.filter(id=access_token).first()
            context = get_neighbourhood_context(user)
            context['user'] = user
            return render(request, 'neighbourhood.html', context)
        except Exception as e:
            return render(request, 'login.html')

    if request.method == 'POST':
        try:
            user_id = request.GET.get('user_id', None)
            if user_id:
                user = User.objects.filter(id=user_id).first()
            else:
                access_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
                user = request.user
            username = request.data.get('username', None)
            if username:
                neighbour = Friends.objects.filter(from_user__username=username, to_user=user).first()
                neighbour.status = 'Accepted'
                neighbour.save()
                context = get_neighbourhood_context(user)
                return redirect(reverse('backend:neighbourhood') + f'?access_token={access_token}')
            else:
                context = get_neighbourhood_context(user)
                return render(request, 'neighbourhood.html', context)
        except Exception as e:
            return render(request, 'login.html')


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def findfriend(request):
    if request.method == 'GET':
        user_id = request.GET.get('access_token')
        user = User.objects.filter(id=user_id).first()
        if user:

           return render(request, 'findfriend.html', context={'user': user})
        else:
            return render(request, 'login.html')



@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def blinkboard(request):
    if request.method == 'GET':
        try:
            access_token = request.GET.get('access_token')
            # decoded_token = AccessToken(access_token)

            user = User.objects.filter(id=access_token).first()

            # neighbours = User.objects.filter(location__icontains=user.location).order_by('-updated_at').exclude(username=user.username)
            neighbours = get_all_friends(user)
            neighbour_list = [{
                'username': get_user_attribute(user, neighbour, 'username'),
                'avatar': get_user_attribute(user, neighbour, 'avatar').url if get_user_attribute(user, neighbour,
                                                                                                  'avatar') else None,
                'blink_board': get_user_attribute(user, neighbour, 'blink_board'),
                'blink_board_image': get_user_attribute(user, neighbour, 'blink_board_image').url if get_user_attribute(
                    user, neighbour, 'blink_board_image') else None,
                'updated_at': get_user_attribute(user, neighbour, 'updated_at')
            } for neighbour in
                neighbours]
            context = {
                'user':user,
                'neighbours': neighbour_list
            }
            return render(request, 'blinkboard.html', context)
        except Exception as e:
            return render(request, 'login.html')


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def filter_friend(request):
    if request.method == 'GET':
        try:
            user_name = request.GET.get('username')
            user = request.user
            friends = get_friends(user)
            usernames = []
            users = None
            for friend in friends:
                if friend.from_user == user:
                    usernames.append(friend.to_user.username)
                else:
                    usernames.append(friend.from_user.username)
            if user_name:
                users = User.objects.filter(username__icontains=user_name).exclude(username=request.user.username)
            user_list = []
            if users:
                for user in users:
                    if user.username not in usernames:
                        user_data = {'username': user.username}

                        # Check if the avatar field has a file associated with it
                        if user.avatar and user.avatar.file:
                            user_data['avatar'] = user.avatar.url
                        else:
                            user_data['avatar'] = None  # Or any default value you prefer
                        user_list.append(user_data)

            return JsonResponse({'success': True, 'users': user_list, 'friends': usernames})
        except Exception as e:
            return render(request, 'login.html')

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    if request.method == 'POST':
        try:
            requested_username = request.data.get('username')
            user_name = request.user

            user = User.objects.get(username=requested_username)
            if not Friends.objects.filter(from_user=user_name, to_user=user).exists():
                Friends.objects.create(from_user=user_name, to_user=user)

                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'already_friends'})
        except Exception as e:
            return render(request, 'login.html')

    else:
        return JsonResponse(500)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def delete_friend(request):
    if request.method == 'POST':
        try:
            user_id = request.GET.get('user_id', None)
            if user_id:
                user_name = User.objects.filter(id=user_id).first()
            else:
                access_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
                user_name = request.user

            requested_username = request.data.get('username')

            user = User.objects.get(username=requested_username)
            if Friends.objects.filter(from_user=user_name, to_user=user).exists():
                friendship = Friends.objects.filter(from_user=user_name, to_user=user).first()
                friendship.delete()
                return redirect(reverse('backend:neighbourhood') + f'?access_token={access_token}')
            elif Friends.objects.filter(to_user=user_name, from_user=user).exists():
                friendship = Friends.objects.filter(to_user=user_name, from_user=user).first()
                friendship.delete()
                return redirect(reverse('backend:neighbourhood') + f'?access_token={access_token}')

            else:
                return JsonResponse({'status': 'already_removed'})
        except Exception as e:
            return render(request, 'login.html')



@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def homeProfile(request):
    if request.method == 'GET':
        try:
            access_token = request.GET.get('access_token')
            if access_token:
                # decoded_token = AccessToken(access_token)

                user = User.objects.filter(id=access_token).first()
            else:
                user = request.user

            if user:
                context = {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'location': user.location,
                        'bio': user.bio,
                        'quote': user.quote,
                        'avatar': user.avatar if user.avatar else None,
                        'blink_board': user.blink_board,
                        'blink_board_image': user.blink_board_image,
                        'updated_at': user.updated_at

                    },
                    'access_token': access_token,
                }

                # return Response(context)

                # Render the desired template, for example 'homeProfile.html'

                return render(request, 'homeProfile.html', context)
            else:
                return JsonResponse("No User Found")
        except Exception as e:
            return render(request, 'login.html')
