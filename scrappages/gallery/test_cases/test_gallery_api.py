from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.test.client import encode_multipart, BOUNDARY, MULTIPART_CONTENT
from PIL import Image
import json
import os
import pytest
from gallery.models import Scrap, Comment, Tag

# scraps (GET, POST)
def test_scraps_get(client, scrap1, scrap2, scrap3):
    response = client.get(
        reverse(
            'scraps'
        )
    )
    assert response.status_code == 200

    results = json.loads(response.content.decode('utf-8'))
    assert len(results) == 3

    # it's most recent first
    assert results[0]['id'] == scrap3.id
    assert results[0]['title'] == scrap3.title
    assert results[0]['description'] == scrap3.description
    assert results[0]['file_type'] == scrap3.file_type
    assert results[0]['file_url'].endswith(scrap3.file.url)
    assert results[0]['num_comments'] == 0
    assert results[0]['num_likes'] == 0
    assert results[0]['tags'] == []

    assert results[1]['id'] == scrap2.id
    assert results[1]['title'] == scrap2.title
    assert results[1]['description'] == scrap2.description
    assert results[1]['file_type'] == scrap2.file_type
    assert results[1]['file_url'].endswith(scrap2.file.url)
    assert results[1]['num_comments'] == 0
    assert results[1]['num_likes'] == 0
    assert results[1]['tags'] == []

    assert results[2]['id'] == scrap1.id
    assert results[2]['title'] == scrap1.title
    assert results[2]['description'] == scrap1.description
    assert results[2]['file_type'] == scrap1.file_type
    assert results[2]['file_url'].endswith(scrap1.file.url)
    assert results[2]['num_comments'] == 0
    assert results[2]['num_likes'] == 0
    assert results[2]['tags'] == []

def test_scraps_get_with_comments_and_tags(client, like_scrap1, comment1, comment2, tags1):
    response = client.get(
        reverse(
            'scraps'
        )
    )
    assert response.status_code == 200

    results = json.loads(response.content.decode('utf-8'))
    assert len(results) == 1

    assert results[0]['id'] == like_scrap1.id
    assert results[0]['title'] == like_scrap1.title
    assert results[0]['description'] == like_scrap1.description
    assert results[0]['file_type'] == like_scrap1.file_type
    assert results[0]['file_url'].endswith(like_scrap1.file.url)
    assert results[0]['num_comments'] == 2
    assert results[0]['num_likes'] == 1
    assert len(results[0]['tags']) == 2
    assert {'name': 'pic','scrap_id': like_scrap1.id} in results[0]['tags']
    assert {'name': 'yellow','scrap_id': like_scrap1.id} in results[0]['tags']

def test_scraps_post(client, new_user, violet_jpg):
    logged_in = client.login(username='bison', password='calf123!')
    assert logged_in

    data = {
        'title': 'vile vio',
        'description': 'violet is violent',
        'file': violet_jpg,
        'tags': json.dumps([
            'violet', 'pic', 'helloworld'
        ])
    }

    response = client.post(
        reverse(
            'scraps'
        ),
        data=data,
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 200
    result = json.loads(response.content.decode('utf-8'))
    assert 'id' in result and result['id']
    assert 'user' in result and result['user'] == 'bison'
    assert 'title' in result and result['title'] == 'vile vio'
    assert 'description' in result and result['description'] == 'violet is violent'
    assert 'file_url' in result and result['file_url'].endswith(violet_jpg.name)
    assert 'file_type' in result and result['file_type'] == 'image'

    assert 'tags' in result and len(result['tags']) == 3
    for i in range(3):
        assert result['tags'][i]['name'] in ['violet', 'pic', 'helloworld']
        assert result['tags'][i]['scrap_id'] == result['id']

    scrap = get_object_or_404(Scrap, id=result['id'])
    os.unlink(scrap.file.path)
    

@pytest.mark.django_db
def test_scraps_post_not_logged_in(client, violet_jpg):
    assert '_auth_user_id' not in client.session

    data = {
        'title': 'vile vio',
        'description': 'violet is violent',
        'file': violet_jpg,
        'tags': json.dumps([
            'violet', 'pic', 'helloworld'
        ])
    }

    response = client.post(
        reverse(
            'scraps'
        ),
        data=data,
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 401

def test_scraps_post_invalid_title(client, new_user, violet_jpg):
    logged_in = client.login(username='bison', password='calf123!')
    assert logged_in

    data = {
        'title': '',
        'file': violet_jpg
    }

    response = client.post(
        reverse(
            'scraps'
        ),
        data=data,
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"Invalid; Title too short; minimum length = 1"'

    data = {
        'title': 'i have been told my previous post had a title that is too short so i want to make a title that is too long to get back at the savages that made this website, like let me ramble on and on and on in my title, i know theres a description, but who tf cares when the title is all people are going to see, see, i am using the most elongated versions of words ever known to mankind',
        'file': violet_jpg
    }

    response = client.post(
        reverse(
            'scraps'
        ),
        data=data,
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"Invalid; Title too long; maximum length = 100"'

    data = {
        'file': violet_jpg
    }

    response = client.post(
        reverse(
            'scraps'
        ),
        data=data,
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"Required: post title and a file to upload"'

def test_scraps_post_invalid_file(client, new_user, white_pdf, md_file):
    logged_in = client.login(username='bison', password='calf123!')
    assert logged_in

    data = {
        'title': 'take me!!!',
        'file': white_pdf
    }

    response = client.post(
        reverse(
            'scraps'
        ),
        data=data,
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"Invalid file type uploaded: only accepts TXT, PNG, JPG, JPEG and GIF"'

    data = {
        'title': 'take me!!!',
        'file': md_file
    }

    response = client.post(
        reverse(
            'scraps'
        ),
        data=data,
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"Invalid file type uploaded: only accepts TXT, PNG, JPG, JPEG and GIF"'

    data = {
        'title': 'take me!!!'
    }

    response = client.post(
        reverse(
            'scraps'
        ),
        data=data,
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"Required: post title and a file to upload"'

    data = {
        'title': 'take me!!!',
        'file': ContentFile("hello world", 'takeme.jpg')
    }

    response = client.post(
        reverse(
            'scraps'
        ),
        data=data,
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"Invalid; image file could not be verified"'

# specific_scrap (GET, PUT, DELETE)
def test_specific_scrap_get(client, user1, scrap1):
    response = client.get(
        reverse(
            'specific_scrap',
            kwargs={'sid': scrap1.id}
        )
    )

    assert response.status_code == 200
    result = json.loads(response.content.decode('utf-8'))
    assert result['id'] == scrap1.id
    assert result['title'] == scrap1.title
    assert result['description'] == scrap1.description
    assert result['file_type'] == scrap1.file_type
    assert result['file_url'].endswith(scrap1.file.url)
    assert result['num_comments'] == 0
    assert result['num_likes'] == 0
    assert result['tags'] == []

@pytest.mark.django_db
def test_specific_scrap_does_not_exist(client):
    response = client.get(
        reverse(
            'specific_scrap',
            kwargs={'sid': 100}
        )
    )
    assert response.status_code == 404

def test_specific_scrap_put(client, user1, scrap1):
    logged_in = client.login(username='pooky', password='pooky123')
    assert logged_in

    data = {
        'title': 'violet',
        'description': 'royal purple',
        'tags': [
            'purple', 'violet', 'pic'
        ]
    }

    response = client.put(
        reverse(
            'specific_scrap',
            kwargs={'sid': scrap1.id}
        ),
        data=data,
        content_type='application/json'
    )

    assert response.status_code == 200
    result = json.loads(response.content.decode('utf-8'))
    assert result['id'] == scrap1.id
    assert result['title'] == 'violet'
    assert result['description'] == 'royal purple'
    assert result['file_type'] == scrap1.file_type
    assert result['file_url'].endswith(scrap1.file.url)
    assert result['num_comments'] == 0
    assert result['num_likes'] == 0

    assert len(result['tags']) == 3
    for i in range(3):
        assert result['tags'][i]['name'] in ['purple', 'violet', 'pic']
        assert result['tags'][i]['scrap_id'] == scrap1.id

def test_specific_scrap_put_invalid_title(client, user1, scrap1):
    logged_in = client.login(username='pooky', password='pooky123')
    assert logged_in

    data = {
        'title': '',
        'description': 'royal purple'
    }

    response = client.put(
        reverse(
            'specific_scrap',
            kwargs={'sid': scrap1.id}
        ),
        data=encode_multipart(BOUNDARY, data),
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"Invalid; Title too short; minimum length = 1"'

    data = {
        'title': 'my title was rejected yet again so i must now recover my lost sense of pride and go to deviantart in order to finally get the respect that i deserve, and i cannot live with the man whom i cannot respect bc he does not like airplanes',
        'description': 'royal purple'
    }

    response = client.put(
        reverse(
            'specific_scrap',
            kwargs={'sid': scrap1.id}
        ),
        data=encode_multipart(BOUNDARY, data),
        content_type=MULTIPART_CONTENT
    )
    
    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"Invalid; Title too long; maximum length = 100"'

def test_specific_scrap_put_wrong_user(client, user1, user2, scrap1):
    logged_in = client.login(username='silver', password='silver123')
    assert logged_in

    data = {
        'title': 'violet',
        'description': 'royal purple',
        'tags': json.dumps([
            'purple', 'violet', 'pic'
        ])
    }

    response = client.put(
        reverse(
            'specific_scrap',
            kwargs={'sid': scrap1.id}
        ),
        data=encode_multipart(BOUNDARY, data),
        content_type=MULTIPART_CONTENT
    )

    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"Invalid; Cannot edit another user\'s post"'

def test_specific_scrap_delete(client, user1, scrap1):
    response = client.get(reverse('specific_scrap', kwargs={'sid': scrap1.id}))
    assert response.status_code == 200

    logged_in = client.login(username='pooky', password='pooky123')
    assert logged_in

    response = client.delete(
        reverse(
            'specific_scrap',
            kwargs={'sid': scrap1.id}
        )
    )
    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == True

def test_specific_scrap_delete_wrong_user(client, user1, user2, scrap1):
    logged_in = client.login(username='silver', password='silver123')
    assert logged_in

    response = client.delete(
        reverse(
            'specific_scrap',
            kwargs={'sid': scrap1.id}
        )
    )
    assert response.status_code == 400
    assert json.loads(response.content.decode('utf-8')) == 'Invalid; Cannot delete another user\'s post'

# scrap_comments (GET, POST)
def test_scrap_comments_get():
    pass

def test_scrap_comments_does_not_exist():
    pass

def test_scrap_comments_post():
    pass

def test_scrap_comments_post_no_content():
    pass

# specific_scrap_comment (GET, POST, PUT, DELETE)
def test_specific_scrap_comment_get():
    pass

def test_specific_scrap_comment_scrap_does_not_exist():
    pass

def test_specific_scrap_comment_comment_does_not_exist():
    pass

def test_specific_scrap_comment_comment_not_for_scrap():
    pass

def test_specific_scrap_comment_post():
    pass

def test_specific_scrap_comment_post_no_content():
    pass

def test_specific_scrap_comment_put():
    pass

def test_specific_scrap_comment_put_wrong_user():
    pass

def test_specific_scrap_comment_delete():
    pass

def test_specific_scrap_comment_delete_wrong_user():
    pass

# scrap_like (POST, DELETE)
def test_scrap_like_post(client, user1, scrap1):
    logged_in = client.login(username='pooky', password='pooky123')
    assert logged_in

    response = client.get(
        reverse(
            'specific_scrap',
            kwargs={'sid': scrap1.id}
        )
    )
    result = json.loads(response.content.decode('utf-8'))
    assert result['num_likes'] == 0

    response = client.post(
        reverse(
            'scrap_like',
            kwargs={'sid': scrap1.id}
        )
    )

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == True

    response = client.get(
        reverse(
            'specific_scrap',
            kwargs={'sid': scrap1.id}
        )
    )
    result = json.loads(response.content.decode('utf-8'))
    assert result['num_likes'] == 1

def test_scrap_like_post_already_exists(client, user1, like_scrap1):
    logged_in = client.login(username='pooky', password='pooky123')
    assert logged_in

    response = client.post(
        reverse(
            'scrap_like',
            kwargs={'sid': like_scrap1.id}
        )
    )

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == False

def test_scrap_like_post_no_user(client, scrap1):
    response = client.post(
        reverse(
            'scrap_like',
            kwargs={'sid': scrap1.id}
        )
    )

    assert response.status_code == 401

def test_scrap_like_delete(client, user1, like_scrap1):
    logged_in = client.login(username='pooky', password='pooky123')
    assert logged_in

    response = client.get(
        reverse(
            'specific_scrap',
            kwargs={'sid': like_scrap1.id}
        )
    )
    result = json.loads(response.content.decode('utf-8'))
    assert result['num_likes'] == 1

    response = client.delete(
        reverse(
            'scrap_like',
            kwargs={'sid': like_scrap1.id}
        )
    )

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == True

    response = client.get(
        reverse(
            'specific_scrap',
            kwargs={'sid': like_scrap1.id}
        )
    )
    result = json.loads(response.content.decode('utf-8'))
    assert result['num_likes'] == 0

def test_scrap_like_delete_does_not_exist(client, user1, scrap1):
    logged_in = client.login(username='pooky', password='pooky123')
    assert logged_in

    response = client.delete(
        reverse(
            'scrap_like',
            kwargs={'sid': scrap1.id}
        )
    )

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == False

def test_scrap_like_delete_no_user(client, scrap1):
    response = client.delete(
        reverse(
            'scrap_like',
            kwargs={'sid': scrap1.id}
        )
    )

    assert response.status_code == 401

# comment_like (POST, DELETE)
def test_comment_like_post():
    pass

def test_comment_like_post_already_exists():
    pass

def test_comment_like_post_no_user():
    pass

def test_comment_like_delete():
    pass

def test_comment_like_delete_does_not_exist():
    pass

def test_comment_like_delete_no_user():
    pass

# scrap_tags (GET, POST, DELETE)
def test_scrap_tags_get():
    pass

def test_scrap_tags_scrap_does_not_exist():
    pass

def test_scrap_tags_post():
    pass

def test_scrap_tags_post_invalid_tag():
    pass

def test_scrap_tags_delete():
    pass

# tagged_scraps (GET)
def test_tagged_scraps_get():
    pass

def test_tagged_scraps_tag_does_not_exist():
    pass