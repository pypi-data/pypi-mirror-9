# Overview 

An extremely simple django app that renders templates based on URL path.

Kenny provides a single view, `SongBirdView` which takes the path url kwarg
and appends .html to it and serves it. It also rstrips any `/`s. It can also
take an optional `prefix` kwarg that will be prepended to the redered
template's path.

`SongBirdView` is a subclass of `django.views.generic.base.TemplateView`, so
all of it's documentation except for the `template_name` parameter apply.

So basically, to serve the mockups of your website under the `/mockup/` URL
you can do the following:

```
urlpatterns += (
    url(r'^mockup/(?P<path>.*)$', SongBirdView.as_view(prefix='mockup/'))
)
```

This way, if you go to `localhost:8000/mockup/foo/`, your `mockup/foo.html`
template will be served.

# Installation

As easy as

```
pip install django-kenny
```
