from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<book_id>[0-9]+)/$', views.viewBook, name='viewBook'),
    url(r'^go/$', views.loginUser, name="loginUser"),
    url(r'^create/$', views.searchISBN, name="searchISBN"),
    url(r'^save_book/$', views.getBookDetails, name="getBookDetails"),
    url(r'^submit/book$', views.saveNewBook, name="saveNewBook")
]