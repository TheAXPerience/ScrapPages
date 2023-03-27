from django.db.models import Count
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes, renderer_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from PIL import Image
from .models import Profile


def validate_username(username):
    import re
    return bool(re.match("^[A-Za-z0-9_-]*$", username))


# Create your views here.
@api_view(["GET", "POST"])
@csrf_exempt
@parser_classes([JSONParser])
@renderer_classes([JSONRenderer])
def user_profiles_view(request, format=None):
    if request.method == "GET":
        context = []

        users = User.objects.annotate(
            num_scraps=Count('scraps')).order_by("username")
        for user in users:
            ans = user.profile.serialize()
            ans["profile_picture_url"] = request.build_absolute_uri(
                ans["profile_picture_url"])
            ans["num_scraps"] = user.num_scraps
            context.append(ans)

        return Response(data=context)

    elif request.method == "POST":
        # request.data should contain JSON data
        if "username" not in request.data or "password" not in request.data:
            return Response("Required: username and password",
                            status=status.HTTP_400_BAD_REQUEST)

        username = request.data["username"].lower()
        password = request.data["password"]

        # check if user exists
        try:
            user = User.objects.get(username=username)
            return Response("Username already exists",
                            status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            # this is what we want to happen
            pass

        # validate username and password (just based on lengths)
        if len(username) < 5:
            return Response("Username too short; minimum length = 5",
                            status=status.HTTP_400_BAD_REQUEST)
        elif len(username) > 50:
            return Response("Username too long; maximum length = 50",
                            status=status.HTTP_400_BAD_REQUEST)
        elif len(password) < 8:
            return Response("Password too short; minimum length = 8",
                            status=status.HTTP_400_BAD_REQUEST)
        elif len(password) > 70:
            return Response("Password too long; maximum length = 70",
                            status=status.HTTP_400_BAD_REQUEST)
        elif not validate_username(username):
            return Response("Username invalid; alphanumeric characters only",
                            status=status.HTTP_400_BAD_REQUEST)

        # get other fields
        email = ""
        if "email" in request.data:
            email = request.data["email"]

        first_name = ""
        if "first_name" in request.data:
            first_name = request.data["first_name"]

        last_name = ""
        if "last_name" in request.data:
            last_name = request.data["last_name"]

        # make new user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        return Response(user.profile.serialize())


@api_view(["GET", "PUT", "DELETE"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def specific_user_profile_view(request, username, format=None):
    username = username.lower()
    user = get_object_or_404(User, username=username)

    if request.method == "GET":
        context = user.profile.serialize()

        context["profile_picture_url"] = request.build_absolute_uri(
            context["profile_picture_url"])
        context["num_scraps"] = user.scraps.count()

        return Response(data=context)

    elif request.method == "PUT":
        """
        edits the profile information of a user
        - display name
        - description
        - profile picture
        """
        if username != request.user.username:
            return Response("You do not have permission to alter another user's profile",
                            status=status.HTTP_400_BAD_REQUEST)

        profile = user.profile
        if "display_name" in request.data:
            disname = request.data["display_name"]
            if len(disname) < 5:
                return Response("Display name invalid; minimum length = 5",
                                status=status.HTTP_400_BAD_REQUEST)
            elif len(disname) > 50:
                return Response("Display name invalid; maximum length = 50",
                                status=status.HTTP_400_BAD_REQUEST)
            elif not validate_username(disname):
                return Response("Display name invalid; alphanumeric characters only",
                                status=status.HTTP_400_BAD_REQUEST)
            profile.display_name = disname

        if "description" in request.data:
            profile.description = request.data["description"]

        if "profile_picture" in request.data:
            # validate picture via Pillow
            if request.data['profile_picture'].content_type not in ['image/png', 'image/jpg', 'image/jpeg']:
                return Response("Invalid file type; only accepts PNG and JPG",
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                im = Image.open(request.data["profile_picture"])
                im.verify()
            except:
                return Response("Invalid image file",
                                status=status.HTTP_400_BAD_REQUEST)

            profile.profile_picture = request.data["profile_picture"]

        user.save()

        context = profile.serialize()
        context["profile_picture_url"] = request.build_absolute_uri(
            context["profile_picture_url"])
        context["num_scraps"] = user.scraps.count()
        return Response(data=context)

    elif request.method == "DELETE":
        if username != request.user.username:
            return Response("You do not have permission to alter another user's profile",
                            status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response(True)


@api_view(["GET"])
@csrf_exempt  # do I need this?
@renderer_classes([JSONRenderer])
def specific_user_scraps_view(request, username, format=None):
    """
    return a list of Scraps that have been posted by the given user
    - Scrap id
    - title
    - description
    - file type
    - URL to file (text or image)
    - time posted
    - time updated
    - number of likes
    - number of Comments
    - list of Tags
    """
    user = get_object_or_404(User, username=username)
    scraps = user.scraps.annotate(
        num_comments=Count('comments', distinct=True),
        num_likes=Count('likers', distinct=True)).order_by('-time_updated')

    context = []
    for scrap in scraps:
        ans = scrap.serialize()
        ans["file_url"] = request.build_absolute_uri(ans["file_url"])
        ans["num_comments"] = scrap.num_comments
        ans["num_likes"] = scrap.num_likes
        context.append(ans)

    return Response(data=context)
