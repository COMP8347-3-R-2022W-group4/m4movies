from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'myApp1'
urlpatterns = [
                  path('', views.index, name='index'),
                  path('login/', views.login, name='login'),
                  path('signup/', views.signup, name='signup'),
                  path('about/', views.about, name='about'),
                  path('showMovie/', views.showMovie, name='showMovie'),
                  path('movieDetail/<str:movie_id>', views.movieDetail, name='movieDetail'),
                  path('movieList/', views.movieList, name='movieList'),
                  path('profileList/', views.profileList, name='profileList'),
                  path('profileCreate/', views.profileCreate, name='profileCreate'),
                  path('detail/<int:type_no>', views.detail, name='detail'),
                  path('movies/', views.movies, name='movies'),
                  path('movies/<str:movie_id>', views.movie_detail, name='movie_detail'),
                  path('movies/<str:movie_id>/similar', views.similar_movies, name='similar_movies'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
