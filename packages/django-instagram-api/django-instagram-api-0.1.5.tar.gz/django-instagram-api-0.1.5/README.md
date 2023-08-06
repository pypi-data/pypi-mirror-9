# Django Instagram API

[![Build Status](https://travis-ci.org/ramusus/django-instagram-api.png?branch=master)](https://travis-ci.org/ramusus/django-instagram-api) [![Coverage Status](https://coveralls.io/repos/ramusus/django-instagram-api/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-instagram-api)

Application for interacting with Instagram API objects using Django model interface

## Installation

    pip install django-instagram-api

Add into `settings.py` lines:

    INSTALLED_APPS = (
        ...
        'm2m_history',
        'instagram_api',
    )

    INSTAGRAM_CLIENT_ID = ''

## Usage examples

### Simple API request

    >>>from instagram_api.models import User, Media
    >>>u = User.remote.fetch(237074561)
    >>>print u
    tnt_online

    >>>followers = u.fetch_followers()

    >>>medias = u.fetch_recent_media()
    >>>print medias
    [<Media: 935546412924881779_237074561>, <Media: 935398934535687014_237074561>, <Media: 935385433641536074_237074561>...]


    >>>m = Media.remote.fetch('937539904871536462_190931988')
    >>>comments = m.fetch_comments()
    >>>likes = m.fetch_likes()
