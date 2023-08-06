[![Latest Version](https://pypip.in/version/django-smart-proxy/badge.svg)](https://pypi.python.org/pypi/django-smart-proxy/)
[![Downloads](https://pypip.in/download/django-smart-proxy/badge.svg)](https://pypi.python.org/pypi/django-smart-proxy/)

Django Smart Proxy
==================
Django Smart Proxy is a plug-and-play solution for implementing pass-through proxies in
a Django-based environment.

**Extensibility**<br/>
Django Smart Proxy exposes a *request_decorators* parameter that makes it easily
extensible, allowing access to the request "pipeline" before being sent to the host.

**Common Use Cases**
- Handling OAuth on the server-side to avoid exposing secret keys to the client.
- As an alternative to CORS for making cross-domain AJAX requests.
- Anything else...?


Installation
============
**Requires**
- Python >= 2.6 (supports up to 3.4)
- Django >= 1.4 (Python 2 support up to 1.6.x)

*For all requirements, see <a href="https://github.com/celerityweb/django-smart-proxy/blob/master/setup.py" target="_blank">setup.py</a>.*

**Installing**
```
pip install django-smart-proxy
```

Usage
=====
1. Add ```smart_proxy``` to ```INSTALLED_APPS``` in your ```settings.py```.
   
   **Example**
   ```python
   INSTALLED_APPS = (
       ...,
       'smart_proxy',
       ...,
   )
   ```

2. Add a ```SMART_PROXIES``` dictionary to ```settings.py``` to configure an arbitrary number of proxies.
   
   **Example**
   ```python
   SMART_PROXIES = {
       'instagram': {
           'host_endpoint': 'https://api.instagram.com/v1/',
           'allowed_methods': ('get', 'put', 'post', 'delete',),
           'timeout': 60.0,
       },
       'twitter': {
           'host_endpoint': 'https://api.twitter.com/1.1/',
           'allowed_methods': ('get', 'put', 'post', 'delete',),
           'timeout': 60.0,
           'request_decorators': (
               'channel.apps.twitter_auth.utils.append_authorization_header',
           ),
       },
   }
   ```
3. Edit your ```urls.py``` to configure a root URL mapping for the proxies.
   
   **Example**
   ```python
   urlpatterns = patterns(
       ...,
       url(r'^proxy/', include('smart_proxy.urls')),
       ...,
   )
   ```
4. If applicable, provide an implementation for your request decorators.

   **Example**
   ```python
   from django.conf import settings
   from requests_oauthlib import OAuth1
    
   def append_authorization_header(request, session):
       """
       This function decorates requests to the Twitter proxy with a
       signed oauth-compliant Authorization header.
       """
    
       client_key = getattr(settings, 'SOCIAL_AUTH_TWITTER_KEY', None)
       client_secret = getattr(settings, 'SOCIAL_AUTH_TWITTER_SECRET', None)
    
       if client_key and client_secret:
           request.auth = OAuth1(
               client_key,
               client_secret=client_secret,
               resource_owner_key=session.get('twitter_oauth_token'),
               resource_owner_secret=session.get('twitter_oauth_token_secret'))
    
       return request
   ```
5. You're Done!

In this example, your proxies will be available at ```/proxy/instagram/``` and ```/proxy/twitter/``` respectively.
