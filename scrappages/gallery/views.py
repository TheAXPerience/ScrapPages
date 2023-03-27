from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from PIL import Image
import json
from .models import Scrap, Comment, Tag

# enforce tags are at max 64 characters
# replace non-alphanumeric characters with underscores
def process_tag(tname):
    ret = ""
    for c in tname[:64]:
        if not c.isalnum():
            ret += '_'
        else:
            ret += c
    return ret

# Create your views here.
@api_view(["GET", "POST"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def scraps_view(request):
    if request.method == "GET":
        context = []

        scraps = Scrap.objects.annotate(
            num_comments=Count('comments', distinct=True), num_likes=Count('likers', distinct=True)).order_by("-time_updated")
        for scrap in scraps:
            ans = scrap.serialize()
            ans["file_url"] = request.build_absolute_uri(ans["file_url"])
            ans["num_comments"] = scrap.num_comments
            ans["num_likes"] = scrap.num_likes
            context.append(ans)

        return Response(data=context)

    elif request.method == "POST":
        # request.data should contain JSON data
        if "title" not in request.data or "file" not in request.data:
            return Response("Required: post title and a file to upload",
                            status=status.HTTP_400_BAD_REQUEST)

        title = request.data["title"]
        file = request.data["file"]

        # validate title (just based on length)
        if len(title) < 1:
            return Response("Invalid; Title too short; minimum length = 1",
                            status=status.HTTP_400_BAD_REQUEST)
        elif len(title) > 100:
            return Response("Invalid; Title too long; maximum length = 100",
                            status=status.HTTP_400_BAD_REQUEST)

        # TODO: validate file (currently just using the content_type header)
        file_type = "text"
        if file.content_type in ["image/jpg", "image/png", "image/gif", "image/jpeg"]:
            try:
                im = Image.open(file)
                im.verify()
            except:
                return Response("Invalid; image file could not be verified",
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
                tname = process_tag(tname)
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
        context = scrap.serialize()
        context["file_url"] = request.build_absolute_uri(context["file_url"])
        context["num_comments"] = scrap.comments.count()
        context["num_likes"] = scrap.likers.count()

        return Response(data=context)

    elif request.method == "PUT":
        if request.user != scrap.user:
            return Response("Invalid; Cannot edit another user's post", status=status.HTTP_400_BAD_REQUEST)
        
        if "title" in request.data:
            if len(request.data["title"]) < 1:
                return Response("Invalid; Title too short; minimum length = 1",
                                status=status.HTTP_400_BAD_REQUEST)
            elif len(request.data["title"]) > 100:
                return Response("Invalid; Title too long; maximum length = 100",
                                status=status.HTTP_400_BAD_REQUEST)
            scrap.title = request.data["title"]
        
        if "description" in request.data:
            scrap.description = request.data["description"]
        
        scrap.save()

        if "tags" in request.data:
            for tname in request.data["tags"]:
                tname = process_tag(tname)
                prevtag = Tag.objects.filter(name=tname, scrap__id=scrap.id)
                if not prevtag:
                    tag = Tag(name=tname, scrap=scrap)
                    tag.save()
        
        context = scrap.serialize()
        context["file_url"] = request.build_absolute_uri(context["file_url"])
        context["num_comments"] = scrap.comments.count()
        context["num_likes"] = scrap.likers.count()

        return Response(data=context)

    elif request.method == "DELETE":
        if request.user != scrap.user:
            return Response("Invalid; Cannot delete another user's post", status=status.HTTP_400_BAD_REQUEST)
        try:
            scrap.delete()
            return Response(True)
        except:
            return Response(False)

@api_view(["GET", "POST"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def scrap_comments_view(request, sid):
    scrap = get_object_or_404(Scrap, id=sid)

    if request.method == "GET":
        context = []

        comments = scrap.comments.annotate(
            num_likes=Count('likers', distinct=True),
            num_replies=Count('replies', distinct=True)
        ).order_by("-time_updated")
        for comment in comments:
            ans = comment.serialize()
            ans["num_replies"] = comment.num_replies
            ans["num_likes"] = comment.num_likes
            context.append(ans)

        return Response(data=context)

    elif request.method == "POST":
        # request.data should contain JSON data
        if "content" not in request.data:
            return Response("Invalid; Missing comment content",
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
        context = comment.serialize()
        context["num_replies"] = comment.replies.count()
        context["num_likes"] = comment.likers.count()

        return Response(data=context)

    elif request.method == "POST":
        # request.data should contain JSON data
        if "content" not in request.data:
            return Response("Invalid; Missing comment content",
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
        if request.user != comment.user:
            return Response("Invalid; Cannot edit another user's comment",
                            status=status.HTTP_400_BAD_REQUEST)
        
        if "content" in request.data:
            comment.content = request.data["content"]
            comment.save()
        
        context = comment.serialize()
        context["num_replies"] = comment.replies.count()
        context["num_likes"] = comment.likers.count()

        return Response(data=context)

    elif request.method == "DELETE":
        if request.user != comment.user:
            return Response("Invalid; Cannot delete another user's comment", 
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            comment.delete()
            return Response(True)
        except:
            return Response(False)

@api_view(["POST", "DELETE"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def scrap_like_view(request, sid):
    scrap = get_object_or_404(Scrap, id=sid)

    if request.method == "POST":
        """
        adds a like
        """
        if scrap.likers.filter(pk=request.user.pk).exists():
            return Response(False)
        
        scrap.likers.add(request.user)
        return Response(True)

    elif request.method == "DELETE":
        """
        removes a like
        """
        if not scrap.likers.filter(pk=request.user.pk).exists():
            return Response(False)
        
        scrap.likers.remove(request.user)
        return Response(True)

@api_view(["POST", "DELETE"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def comment_like_view(request, sid, cid):
    scrap = get_object_or_404(Scrap, id=sid)
    comment = get_object_or_404(Comment, id=cid)
    if comment.scrap != scrap:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "POST":
        """
        adds a like
        """
        if comment.likers.filter(pk=request.user.pk).exists():
            return Response(False)
        
        comment.likers.add(request.user)
        return Response(True)

    elif request.method == "DELETE":
        """
        removes a like
        """
        if not comment.likers.filter(pk=request.user.pk).exists():
            return Response(False)
        
        comment.likers.remove(request.user)
        return Response(True)

@api_view(["GET", "POST", "DELETE"])
@csrf_exempt
@permission_classes([IsAuthenticatedOrReadOnly])
@renderer_classes([JSONRenderer])
def scrap_tags_view(request, sid):
    scrap = get_object_or_404(Scrap, id=sid)

    if request.method == "GET":
        return Response(data=scrap.get_tags())

    elif request.method == "POST":
        if "tag" not in request.data:
            return Response("Invalid: need tag",
                            status=status.HTTP_400_BAD_REQUEST)
        elif scrap.user.username != request.user.username:
            return Response("Invalid: cannot alter tags of another user's post",
                            status=status.HTTP_400_BAD_REQUEST)

        tname = process_tag(request.data["tag"])
        prevtag = Tag.objects.filter(name=tname, scrap__id=scrap.id)
        if prevtag:
            return Response("Invalid; Tag already exists",
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            tag = Tag(name=tname, scrap=scrap)
            tag.save()
            return Response(tag.serialize())
        

    elif request.method == "DELETE":
        if request.user != scrap.user:
            return Response("Invalid; Cannot alter another user's post",
                            status=status.HTTP_400_BAD_REQUEST)
        
        if "tag" not in request.data:
            return Response("Invalid; no tag to delete identified",
                            status=status.HTTP_400_BAD_REQUEST)
        
        tag = get_object_or_404(Tag, name=request.data["tag"], scrap__id=scrap.id)
        try:
            tag.delete()
            return Response(True)
        except:
            return Response(False)

@api_view(["GET"])
@csrf_exempt
@renderer_classes([JSONRenderer])
def tagged_scraps_view(request, tname):
    scraps = Scrap.objects.all().filter(tags__name=tname).annotate(
        num_comments=Count('comments'),
        num_likes=Count('likers')
    ).order_by('-time_updated')

    context = []

    for scrap in scraps:
        ans = scrap.serialize()
        ans["file_url"] = request.build_absolute_uri(ans["file_url"])
        ans["num_comments"] = scrap.num_comments
        ans["num_likes"] = scrap.num_likes
        context.append(ans)

    return Response(data=context)