from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import *
from django.contrib.admin.views.decorators import staff_member_required
import requests
from io import StringIO
import xml.etree.ElementTree as etree
import xml.parsers.expat as expat
import cataloger.models as m
import datetime


#utility
openTags = []
bookInfo = {}
def startElement(name, attrs):
  openTags.append(name)
def endElement(name):
  openTags.pop()
def insideTag(data):
  # Check what tag we're in
  if len(openTags) == 0:
  	return
  currentTag = openTags[len(openTags)-1]
  tagList = ["title", "publication_day", "publication_month", "publication_year", "num_pages"]
  if currentTag in tagList:
  	bookInfo[currentTag] = data




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
  
  global openTags
  global bookInfo
  openTags = []
  bookInfo = {}

  parser = expat.ParserCreate("UTF-8")
  parser.StartElementHandler = startElement
  parser.EndElementHandler = endElement
  parser.CharacterDataHandler = insideTag
  ascii_text = r.text.encode("UTF-8")
  parser.Parse(ascii_text, 1)
  
  # hell yeah, get the content:
  book_info = {'isbn' : isbn}
  book_info.update(bookInfo)
  book_info["pub_date"] = book_info["publication_day"] + "/" + book_info["publication_month"] + "/" + book_info["publication_year"]
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

