from django.urls import path
from gallery import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.scraps_view,
         name='scraps'),
    path('<int:sid>', views.specific_scrap_view,
         name='specific_scrap'),
    path('<int:sid>/comments', views.scrap_comments_view,
         name='scrap_comments'),
    path('<int:sid>/comments/<int:cid>', views.specific_scrap_comment_view,
         name='specific_scrap_comment'),
    path('<int:sid>/like', views.scrap_like_view,
         name='scrap_like'),
    path('<int:sid>/comments/<int:cid>/like', views.comment_like_view,
         name='comment_like'),
    path('<int:sid>/tags', views.scrap_tags_view,
         name='scrap_tags'),
    path('tagged/<str:tname>', views.tagged_scraps_view,
         name='tagged_scraps'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
