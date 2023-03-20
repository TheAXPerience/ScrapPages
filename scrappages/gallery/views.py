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
import json
from .models import Scrap, Comment, Tag

# Create your views here.
@api_view(["GET", "POST"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def scraps_view(request):
    if request.method == "GET":
        """
        returns a list of Scraps
        - Scrap id
        - title
        - description
        - file URL
        - file type
        - time posted
        - time updated
        - number of likes
        - number of Comments
        - list of Tags
        """
        context = []

        scraps = Scrap.objects.annotate(
            num_comments=Count('comments'), num_likes=Count('likers')).order_by("time_updated")
        for scrap in scraps:
            ans = scrap.serialize()
            ans["file_url"] = request.build_absolute_uri(ans["file_url"])
            ans["num_comments"] = scrap.num_comments
            ans["num_likes"] = scrap.num_likes
            context.append(ans)

        return Response(data=context)

    elif request.method == "POST":
        """
        creates a new Scrap
        - title (required)
        - description (defaults to empty)
        - uploaded file (required) (validated) (get file type from either file extension or header)
        - list of Tags
        """
        # request.data should contain JSON data
        if "title" not in request.data or "file" not in request.data:
            return Response("Required: post title and a file to upload",
                            status=status.HTTP_400_BAD_REQUEST)

        title = request.data["title"]
        file = request.data["file"]

        # validate title (just based on length)
        if len(title) < 1:
            return Response("Title too short; minimum length = 1",
                            status=status.HTTP_400_BAD_REQUEST)
        elif len(title) > 100:
            return Response("Username too long; maximum length = 100",
                            status=status.HTTP_400_BAD_REQUEST)

        # TODO: validate file (currently just using the content_type header)
        file_type = "text"
        if file.content_type in ["image/jpg", "image/png", "image/gif", "image/jpeg"]:
            try:
                im = Image.open(file)
                im.verify()
            except:
                return Response("Invalid image file",
                                status=status.HTTP_400_BAD_REQUEST)
            file_type = "image"
        elif file.content_type == "text/plain":
            # just force it to be a txt file
            file.name = file.name.split(".")[0] + ".txt"
        else:
            return Response("Invalid file type uploaded: only accepts TXT, PNG, JPG, JPEG and GIF",
                            status=status.HTTP_400_BAD_REQUEST)

        # get other fields
        description = ""
        if "description" in request.data:
            description = request.data["description"]

        # make new Scrap
        scrap= Scrap(
            user=request.user,
            title=title,
            description=description,
            file=file,
            file_type=file_type
        )
        scrap.save()

        if "tags" in request.data:
            alltags = json.loads(request.data["tags"])
            for tname in alltags:
                tname = tname[:64]
                prevtag = Tag.objects.filter(name=tname, scrap__id=scrap.id)
                if not prevtag:
                    tag = Tag(name=tname, scrap=scrap)
                    tag.save()

        context = scrap.serialize()
        context["file_url"] = request.build_absolute_uri(context["file_url"])
        return Response(context)

@api_view(["GET", "PUT", "DELETE"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def specific_scrap_view(request, sid):
    scrap = get_object_or_404(Scrap, id=sid)

    if request.method == "GET":
        """
        returns a specific Scrap
        - Scrap id
        - title
        - description
        - file URL
        - file type
        - time posted
        - time updated
        - number of likes
        - number of Comments
        - list of Tags
        """
        context = scrap.serialize()
        context["file_url"] = request.build_absolute_uri(context["file_url"])
        context["num_comments"] = scrap.comments.count()
        context["num_likes"] = scrap.likers.count()

        return Response(data=context)

    elif request.method == "PUT":
        """
        updates a Scrap
        - title
        - description
        - automatically updates time updated
        - list of Tags to upload???
        - list of Tags to remove???

        "what if I want to upload a new file?" make a new post it's free
        """
        pass

    elif request.method == "DELETE":
        """
        deletes a Scrap
        """
        pass

@api_view(["GET", "POST"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def scrap_comments_view(request, sid):
    scrap = get_object_or_404(Scrap, id=sid)

    if request.method == "GET":
        """
        returns list of Comments on a given Scrap
        - Comment id
        - content
        - username of User
        - display name of User's Profile
        - title of Scrap
        - time posted
        - id of Comment this one is a reply to (omitted if NULL)
        - number of likes
        """
        context = []

        comments = scrap.comments.annotate(
            num_likes=Count('likers')).order_by("time_updated")
        for comment in comments:
            ans = comment.serialize()
            ans["num_likes"] = comment.num_likes
            context.append(ans)

        return Response(data=context)

    elif request.method == "POST":
        """
        create new Comment
        - content
        - id of Comment to reply to
        - pulls Scrap info from sid
        - pulls User info from authentication system
        """
        # request.data should contain JSON data
        if "content" not in request.data:
            return Response("Required: comment content",
                            status=status.HTTP_400_BAD_REQUEST)

        content = request.data["content"]

        # make new Scrap
        comment = Comment(
            user=request.user,
            content=content,
            scrap=scrap,
            reply_to=None
        )
        comment.save()

        return Response(comment.serialize())

@api_view(["GET", "POST", "PUT", "DELETE"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def specific_scrap_comment_view(request, sid, cid):
    scrap = get_object_or_404(Scrap, id=sid)
    comment = get_object_or_404(Comment, id=cid)
    if comment.scrap != scrap:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        """
        returns Comment
        - Comment id
        - content
        - username of User
        - display name of User's Profile
        - title of Scrap
        - time posted
        - id of Comment this one is a reply to (omitted if NULL)
        - number of likes
        """
        context = comment.serialize()
        context["num_likes"] = comment.likers.count()

        return Response(data=context)

    elif request.method == "POST":
        """
        create new Comment, but as reply to this comment
        """
        # request.data should contain JSON data
        if "content" not in request.data:
            return Response("Required: comment content",
                            status=status.HTTP_400_BAD_REQUEST)

        content = request.data["content"]

        # make new Scrap
        new_comment = Comment(
            user=request.user,
            content=content,
            scrap=scrap,
            reply_to=comment
        )
        new_comment.save()

        return Response(new_comment.serialize())

    elif request.method == "PUT":
        """
        edits Comment
        - content (that's it)
        """
        pass

    elif request.method == "DELETE":
        """
        deletes a Comment
        """
        pass

@api_view(["POST", "DELETE"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def scrap_like_view(request, sid):
    if request.method == "POST":
        """
        adds a like
        """
        pass

    elif request.method == "DELETE":
        """
        removes a like
        """
        pass

@api_view(["POST", "DELETE"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def comment_like_view(request, sid, cid):
    if request.method == "POST":
        """
        adds a like
        """
        pass

    elif request.method == "DELETE":
        """
        removes a like
        """
        pass

@api_view(["GET", "POST", "DELETE"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def scrap_tags_view(request, sid):
    scrap = get_object_or_404(Scrap, id=sid)

    if request.method == "GET":
        """
        returns a list of Tags
        - list of Tags
        """
        return Response(data=scrap.get_tags())

    elif request.method == "POST":
        """
        adds a new Tag to the Scrap
        - tag name
        """
        if "tag" not in request.data:
            return Response("Invalid: need tag",
                            status=status.HTTP_400_BAD_REQUEST)
        elif scrap.user.username != request.user.username:
            return Response("Invalid: cannot alter tags of another user's post")

        tname = request.data["tag"][:64]
        prevtag = Tag.objects.filter(name=tname).filter(scrap__id=scrap.id)
        if prevtag:
            return Response("Tag already exists")
        else:
            tag = Tag(name=tname, scrap=scrap)
            tag.save()
            return Response(tag.serialize())
        

    elif request.method == "DELETE":
        """
        removes a Tag from the Scrap
        - tag name
        """
        pass

@api_view(["GET"])
@csrf_exempt
@renderer_classes([JSONRenderer])
def tagged_scraps_view(request, tname):
    """
    returns a list of Scraps with a given Tag
    - Scrap id
    - title
    - description
    - file URL
    - file type
    - time posted
    - time updated
    - number of likes
    - number of Comments
    - list of Tags
    """
    scraps = Scrap.objects.all().filter(tags__name=tname).annotate(
        num_comments=Count('comments'),
        num_likes=Count('likers')).order_by('time_updated')

    context = []

    for scrap in scraps:
        ans = scrap.serialize()
        ans["file_url"] = request.build_absolute_uri(ans["file_url"])
        ans["num_comments"] = scrap.num_comments
        ans["num_likes"] = scrap.num_likes
        context.append(ans)

    return Response(data=context)