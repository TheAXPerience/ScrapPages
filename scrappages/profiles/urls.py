from django.urls import path
from profiles import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.user_profiles_view, name='user_profiles'),
    path('<str:username>', views.specific_user_profile_view,
         name='specific_user_profile'),
    path('<str:username>/scraps', views.specific_user_scraps_view,
         name='specific_user_scraps'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
