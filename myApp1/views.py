from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Type, Item, Customer
from http.client import HTTPSConnection as Connect
from django.contrib import messages
import json
import random
from .forms import CreateUserForm, CustomerForm
from dotenv import load_dotenv
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# load_dotenv()
MOVIE_API_KEY = 'c3660ed96c3beaf6808809efaa5e31d7'


def index(request):
    response = HttpResponse()
    heading1 = '<p>' + 'This is the main page of group#4 "Movies Django project"' + '</p>'
    contributions = '<p>' + 'Contributors: Abhay, Rahul, Sarab, Shruti' + '</p>'
    response.write(heading1)
    response.write(contributions)
    all_href = '<a href="{}">{}</a>'.format(build_uri(request, '/movies/'), 'Show All Movies')
    response.write(all_href)
    # return response
    return render(request, 'index.html')


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('myApp1:index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect('myApp1:loginPage')
            else:
                messages.error(request, 'Username or password is incorrect')
        context = {}
        return render(request, 'login.html', context)
    # return HttpResponse('This is the about page')
    # return render(request, 'login.html')


def logoutUser(request):
    logout(request)
    return redirect('myApp1:loginPage')


def signup(request):
    if request.user.is_authenticated:
        return redirect('myApp1:index')
    else:
        registerForm = CreateUserForm()
        if request.method == 'POST':
            registerForm = CreateUserForm(request.POST)
            if registerForm.is_valid():
                phone = registerForm.cleaned_data.get('phone')
                username = registerForm.cleaned_data.get('username')
                email = registerForm.cleaned_data.get('email')
                user_saved = registerForm.save()
                messages.success(request, 'Hello ' + email + ', your account has been created successfully! 🚀')
                Customer(user=user_saved, email=email, phone=phone, name=username).save()
                return redirect('myApp1:loginPage')

        context = {'registerForm': registerForm}
        return render(request, 'signup.html', context)


def about(request):
    # return HttpResponse('This is the about page')
    return render(request, 'myApp1/about.html')


def movieDetail(request, movie_id):
    movie_json = fetch_movie_detail(movie_id)
    context = {
        'voting_5_star_scale': movie_json.get('vote_average', 0) // 2,
        'movie': movie_json,
        'providers': fetch_movie_providers(movie_id)
    }
    return render(request, 'movieDetail.html', context)


def showMovie(request):
    # return HttpResponse('This is the about page')
    return render(request, 'showMovie.html')


# will return list of limited 5 random elements from the _list
def get_random_elements(_list, limit=100):
    return random.sample(_list, min(limit, len(_list)))


def movieList(request):
    top_rated_movies = [convert_movieJSONToClass(movie) for movie in fetch_movies(request)]
    popular_movies = [convert_movieJSONToClass(movie) for movie in fetch_movies(request, 'popular')]
    upcoming_movies = [convert_movieJSONToClass(movie) for movie in fetch_movies(request, 'upcoming')]
    context = {
        'movie': get_random_elements(top_rated_movies, 1)[0],
        'top_rated_movies': get_random_elements(top_rated_movies),
        'popular_movies': get_random_elements(popular_movies),
        'upcoming_movies': get_random_elements(upcoming_movies)
    }
    return render(request, 'movieList.html', context)


def detail(request, type_no):
    type_with_id = get_object_or_404(Type, pk=type_no)
    # type_with_id = Type.objects.get(id=type_no)
    items_with_type = Item.objects.filter(type=type_with_id)
    response = HttpResponse()
    heading1 = '<p>' + 'Different Items with type: ' + str(type_with_id) + '</p>'
    response.write(heading1)
    for item in items_with_type:
        para = '<p>' + str(item.price) + ': ' + str(item) + '</p>'
        response.write(para)
    return response


def build_uri(request, uri_endpoint):
    return request.build_absolute_uri(uri_endpoint)


def convert_movieJSONToClass(movie):
    cmovie = Movie()
    cmovie.id = str(movie['id'])
    cmovie.name = movie['name']
    cmovie.url = movie['url']
    cmovie.poster_path = 'https://image.tmdb.org/t/p/w500' + movie['poster_path']
    return cmovie


# will return list of movie names
def fetch_movies(request, endpoint_type='top_rated') -> [str]:
    top_movies = list()
    dummy_movie = {
        'id': '550',
        'name': 'Fight Club',
        'url': build_uri(request, '/movies/550'),
        'poster_path': '/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg'}
    connection = Connect("api.themoviedb.org")
    json_data = dict()
    try:
        api_key = '?api_key=' + MOVIE_API_KEY
        top_movies_endpoint = '/3/movie/' + endpoint_type + api_key
        connection.request("GET", top_movies_endpoint)
        res = connection.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
        for movie in json_data['results']:
            movie_url = build_uri(request, '/movies/' + str(movie['id']))
            movie_json = {
                'id': movie['id'],
                'name': movie['title'],
                'url': movie_url,
                'poster_path': movie['poster_path']}
            top_movies.append(movie_json)
        print('Movies fetched from API:', len(top_movies))
    except TypeError as error:
        json_data['error'] = error
    if 'status_code' in json_data and json_data['status_code'] == 34:
        json_data['title'] = 'No such movie found'
        json_data['overview'] = 'Try other movies from below URL'
        json_data['vote_average'] = 0.0
        json_data['vote_count'] = 0
    top_movies.append(dummy_movie)
    return top_movies


def fetch_similar_movies(request, movie_id) -> [str]:
    similar = list()
    similar.append({'name': 'Based on', 'url': build_uri(request, '/movies/' + movie_id)})
    connection = Connect("api.themoviedb.org")
    json_data = dict()
    try:
        api_key = '?api_key=' + MOVIE_API_KEY
        similar_movies_endpoint = '/3/movie/{}/similar{}'.format(movie_id, api_key)
        connection.request("GET", similar_movies_endpoint)
        res = connection.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
        print(json_data)
        for movie in json_data['results']:
            movie_url = build_uri(request, '/movies/' + str(movie['id']))
            movie_json = {'name': movie['title'], 'url': movie_url}
            similar.append(movie_json)
        print('Movies fetched from API:', len(similar))
    except TypeError as error:
        json_data['error'] = error
    except KeyError as error:
        similar.append({'name': 'No similar movies', 'url': build_uri(request, '/movies')})
    if 'status_code' in json_data and json_data['status_code'] == 34:
        json_data['title'] = 'No such movie found'
        json_data['overview'] = 'Try other movies from below URL'
        json_data['vote_average'] = 0.0
        json_data['vote_count'] = 0
    return similar


def fetch_movie_detail(movie_id: str) -> dict:
    connection = Connect("api.themoviedb.org")
    headers = {}
    payload = ''
    json_data = dict()
    try:
        print(MOVIE_API_KEY)
        api_key = '?api_key=' + MOVIE_API_KEY
        movie_id_endpoint = "/3/movie/" + movie_id + api_key
        connection.request("GET", movie_id_endpoint, payload, headers)
        res = connection.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
    except TypeError as error:
        json_data['error'] = error
    if 'status_code' in json_data and json_data['status_code'] == 34:
        json_data['title'] = 'No such movie found'
        json_data['overview'] = 'Try other movies from below URL'
        json_data['vote_average'] = 0.0
        json_data['vote_count'] = 0
        json_data['id'] = movie_id
    return json_data


def movies(request):
    response = HttpResponse()
    heading1 = '<p>' + 'Top movies fetched dynamically: ' + '</p>'
    response.write(heading1)
    list_items = ''
    for movie in fetch_movies(request):
        href = '<a href="{}">{}</a>'.format(movie['url'], movie['name'])
        list_items += '<li>' + href + '</li>'
    ul = '<ul>{}</ul>'.format(list_items)
    response.write(ul)
    return response


def get_movie_detail_in_html(request, movie_details):
    t = movie_details['title']
    va = str(movie_details["vote_average"])
    vc = str(movie_details["vote_count"])
    movie_id = str(movie_details['id'])
    top_movies_page = build_uri(request, '/movies/')
    similar_movies_page = build_uri(request, '/movies/{}/similar'.format(movie_id))
    all_href = '<a href="{}">{}</a>'.format(top_movies_page, 'Show Top Movies')
    similar_href = '<a href="{}">{}</a>'.format(similar_movies_page, 'Show Similar Movies')
    movie_details_html = '<p>' + 'Title:<strong> </br>' + t + '</strong></p>' \
                         + '<p>' + 'Overview: </br>' + movie_details['overview'] + '</p>' \
                         + '<p> Vote Average:</br>' + va + '</p>' \
                         + '<p> Vote Count:</br>' + vc + '</p>' \
                         + similar_href + '</br></br>' \
                         + all_href + '</br></br>'
    return movie_details_html


def parse_ordered_list_of_providers(providers):
    list_items = ''
    for provider in providers:
        list_items += '<li>' + provider.get('provider_name', 'NA') + '</li>'
    return '<ol>{}</ol>'.format(list_items)


def get_movie_providers_in_html(request, movie_providers):
    link = movie_providers.get('link', build_uri(request, '/movies'))
    renters = movie_providers.get('rent', [{'provider_name': 'NA'}])
    flat_raters = movie_providers.get('flatrate', [{'provider_name': 'NA'}])
    sellers = movie_providers.get('buy', [{'provider_name': 'NA'}])
    watch_link = '<a href="{}">{}</a>'.format(link, 'Watch')
    api_credits = '<p>Powered by TMDB and JustWatch</p>'
    movie_details_html = '</br>Rent:' + parse_ordered_list_of_providers(renters) \
                         + 'Flat:' + parse_ordered_list_of_providers(flat_raters) \
                         + 'Buy:' + parse_ordered_list_of_providers(sellers) \
                         + watch_link \
                         + api_credits
    return movie_details_html


def movie_detail(request, movie_id):
    response = HttpResponse()
    heading1 = '<p>' + 'Movie details: ' + '</p>'
    response.write(heading1)
    movie_details = fetch_movie_detail(movie_id)
    movie_providers = fetch_movie_providers(movie_id)
    response.write(get_movie_detail_in_html(request, movie_details))
    response.write(get_movie_providers_in_html(request, movie_providers))
    return response


def fetch_movie_providers(movie_id):
    connection = Connect("api.themoviedb.org")
    json_data = dict()
    try:
        endpoint_parse = '/3/movie/{}/watch/providers?api_key={}'
        endpoint = endpoint_parse.format(movie_id, MOVIE_API_KEY)
        connection.request("GET", endpoint)
        data = connection.getresponse().read().decode("utf-8")
        default_provider_data = {}
        json_data = json.loads(data).get('results', {}).get('CA', default_provider_data)
    except TypeError as error:
        json_data['error'] = error
    if 'status_code' in json_data and json_data['status_code'] == 34:
        json_data['title'] = 'No such movie found'
        json_data['overview'] = 'Try other movies from below URL'
        json_data['vote_average'] = 0.0
        json_data['vote_count'] = 0
        json_data['id'] = movie_id
    return json_data


def similar_movies(request, movie_id):
    response = HttpResponse()
    heading = '<p>' + 'Similar movies: ' + '</p>'
    response.write(heading)
    list_items = ''
    for movie in fetch_similar_movies(request, movie_id):
        href = '<a href="{}">{}</a>'.format(movie['url'], movie['name'])
        list_items += '<li>' + href + '</li>'
    ul = '<ul>{}</ul>'.format(list_items)
    response.write(ul)
    return response


class Movie:
    id: str
    name: str
    url: str
    poster_path: str


class MovieDetails:
    id: str
    title: str

    poster_path: str


@login_required(login_url='myApp1:loginPage')
# @allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    # if not request.user.is_authenticated:
    #     return redirect('myApp1:loginPage')
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'user_profile.html', context)
