# django-favit

A simple reusable app for django that makes it easy to deal with faving
and unfaving any object from any application.

## Installation

* Install django-favit in your vilrtual env:

```
pip install django-favit
```

* Add the app to your settings.py

```python
INSTALLED_APPS = [
  ...
  "favit",
  ...
]
```

* Add favit urls to your project's `urls.py` file:

```python
urlpatterns = patterns('',
  ...
  (r'^favit/', include('favit.urls')),
  ...
)
```

* Sync your database:

```
python manage.py syncdb
```

* Make sure you have jQuery ajax CSRF configuration right

See https://docs.djangoproject.com/en/1.7/ref/contrib/csrf/#ajax

## Usage:


### Template tags:

* Get the favorited objects for a given user:

```python
{% with user_favorites <user> "app_label.model" as favorite_list %}
    {% for fav_obj in favorite_list %}
        {# do something with fav_obj #}
    {% endfor %}
{% endwith %}
```


* Given an object `obj` you may show it fav count like this:

```python
<p>Favorite Count {{ obj|favorites_count }}</p>
```


* Get Favorite instance for an object (obj) and a user (user)

```python
{% with obj|get_favorite_for:user as fav_object %}
    ...
{% endwith %}
```

* Favorite Button for an object `my_obj`:

```python
{% favorite_button my_obj %}
```


### Favorites Manager

* Create a Favorite instance for a user and object:

```python
>>> from django.contrib.auth.models import User
>>> from music.models import Song
>>> user = User.objects.get(username='jdoe')
>>> song = Song.objects.get(pk=1)
>>> fav = Favorite.objects.create(user, song)
```

    or:

```python
>>> fav = Favorite.objects.create(user, 1, Song)
```

    or:

```python
>>> fav = Favorite.objects.create(user, 1, "music.Song")
```

 * Get the objects favorited by a given user:

```python
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='jdoe')
>>> Favorite.objects.for_user(user)
>>> [<Favorite: Favorite object 1>, <Favorite: Favorite object 2>, <Favorite: Favorite object 3>]
```

* Now, get user favorited objects belonging to a given model:

```python
>>> from django.contrib.auth.models import User
>>> from music.models import Song
>>> user = User.objects.get(username='jdoe')
>>> Favorite.objects.for_user(user, model=Song)
>>> [<Favorite: Favorite object 1>, <Favorite: Favorite object 2>, <Favorite: Favorite object 3>]
```

* Get the favorited object instances of a given model favorited by any user:

```python
>>> from music.models import Song
>>> Favorite.objects.for_model(Song)
>>> [<Favorite: Favorite object 1>, <Favorite: Favorite object 2>, <Favorite: Favorite object 3>]
```

* Get a Favorite instance for a given object and user:

```python
>>> from django.contrib.auth.models import User
>>> from music.models import Song
>>> user = User.objects.get(username='jdoe')
>>> song = Song.objects.get(pk=1)
>>> fav = Favorite.objects.get_favorite(user, song)
```

* Get all Favorite instances for a given object

```python
>>> from music.models import Song
>>> song = Song.objects.get(pk=1)
>>> fav = Favorite.objects.for_object(song)
```


