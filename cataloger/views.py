from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import *
from django.contrib.admin.views.decorators import staff_member_required
import requests
from io import StringIO
import xml.etree.ElementTree as etree
import cataloger.models as m
import datetime

# Create your views here.
def index(request):
  return render(request, "garbage.html", {'user' : request.user})

def viewBook(request, book_id):
  return HttpResponse("This is book #%s" % book_id)

def loginUser(request):
  username = request.POST['username']
  password = request.POST['password']
  user = authenticate(username=username, password=password)
  if user is not None:
    login(request, user)
  return index(request)

@staff_member_required
def searchISBN(request):
  return render(request, "isbn_search.html")

@staff_member_required
def getBookDetails(request):
  # I shouldn't be doing this in a view
  # this is wrong and I am bad
  isbn = request.POST['isbn']
  r = requests.get("https://goodreads.com/book/isbn?format=xml&key=jDPRQ54TVJY13j7gjEUw&isbn="+isbn)
  # etree needs a file, so we fake one here:
  fake_file = StringIO(r.text)
  tree = etree.parse(fake_file)
  root = tree.getroot()
  book = root.find("book")
  # hell yeah, get the content:
  book_info = {'isbn' : isbn}
  book_info["title"] = book.find("title").text
  book_info["pub_date"] = book.find("publication_day").text + "/" + book.find("publication_month").text + "/" + book.find("publication_year").text
  book_info["page_count"] = book.find("num_pages").text
  return render(request, "create_book.html", book_info)

@staff_member_required
def saveNewBook(request):
  title = request.POST['title']
  isbn = request.POST['isbn']
  
  date_parts = request.POST['pub_date'].rsplit("/")
  pub_date = datetime.date(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))

  
  page_count = request.POST['page_count']
  book = m.Book.objects.create(title=title, isbn=isbn, pub_date=pub_date, page_count=page_count)
  return searchISBN(request)

