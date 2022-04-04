from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'myApp1'
urlpatterns = [
                  path('', views.index, name='index'),
                  path('login/', views.loginPage, name='loginPage'),
                  path('logout/', views.logoutUser, name='logoutUser'),
                  path('signup/', views.signup, name='signup'),
                  path('about/', views.about, name='about'),
                  path('showMovie/', views.showMovie, name='showMovie'),
                  path('movieDetail/<str:movie_id>', views.movieDetail, name='movieDetail'),
                  path('orderMovie/<str:movie_id>', views.orderMovie, name='orderMovie'),
                  path('movieList/', views.movieList, name='movieList'),
                  path('fetchOrderedMovies/', views.fetchOrderedMovies, name='fetchOrderedMovies'),
                  path('movies/', views.movies, name='movies'),
                  path('movies/<str:movie_id>', views.movie_detail, name='movie_detail'),
                  path('movies/<str:movie_id>/similar', views.similar_movies, name='similar_movies'),
                  path('profile/', views.accountSettings, name='account_settings'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
