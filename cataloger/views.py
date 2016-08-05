from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import *
from django.contrib.admin.views.decorators import staff_member_required
import requests
import cataloger.services as cataloger_services
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

def searchBooks(request):
  return render(request, "book_search.html")

def getTags(request):
  print("hello")
  print(request.POST['query'])
  query = request.POST['query']
  tagSet = m.Tag.objects.filter(title__contains=query)
  responseTags = {}
  for tag in tagSet:
    print("found "+tag.title)
    responseTags["tag_" + str(tag.pk)] = tag.title

  tagGroupSet = m.TagGroup.objects.filter(title__contains=query)
  for tagGroup in tagGroupSet:
    print("found "+tagGroup.title)
    responseTags["taggroup_"+ str(tagGroup.pk)] = tagGroup.title

  return JsonResponse(responseTags)

def getBooksWithTags(request):
  print("getting books")
  print(request.POST)
  tagIdPrefix = "tag_"
  tagIds = []
  # get all tagIds in request
  for field in request.POST:
    fieldName = field
    tagIdPrefixPosition = fieldName.find(tagIdPrefix)
    if(tagIdPrefixPosition >= 0 ):
      # extract ID
      tagIds.append(fieldName[(tagIdPrefixPosition+len(tagIdPrefix)):])
  # Get the books
  books = cataloger_services.findBooksWithTags(tagIds)
  titles = {}
  for book in books:
    titles[book.title] = " "

  return JsonResponse(titles)

@staff_member_required
def getBookDetails(request):
  isbn = request.POST['isbn']
  info = cataloger_services.getGoodReadsBookInfo(isbn)

  # hell yeah, get the content:
  book_info = {'isbn' : isbn}
  book_info.update(info)
  book_info["pub_date"] = book_info["publication_day"] + "/" + book_info["publication_month"] + "/" + book_info["publication_year"]
  # Load the tags in perhaps the worst way ever
  book_info["tags"] = m.Tag.objects.all()
  return render(request, "create_book.html", book_info)

@staff_member_required
def saveNewBook(request):
  title = request.POST['title']
  isbn = request.POST['isbn']
  
  date_parts = request.POST['pub_date'].rsplit("/")
  pub_date = datetime.date(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))

  page_count = request.POST['page_count']
  
  authors = []
  author_count = 1

  while request.POST.get('author'+str(author_count)) is not None:
    #Find author if exists:
    authorFullName = request.POST['author'+str(author_count)].split()

    author = m.Author.objects.filter(first_name__contains=authorFullName[0], 
      last_name__contains=authorFullName[-1])

    if len(author.values()) > 0:
      authors.extend(author)
    else:
      authors.append(m.Author.objects.create(first_name=authorFullName[0],last_name=authorFullName[-1]))
    author_count = author_count + 1

  theWholePost = request.POST.keys()
  tags = []
  for postAttr in theWholePost:
    print("postattr: "+postAttr)
    if "tag_" not in postAttr:
      continue
    tags.append(postAttr.replace("tag_", ""))


  book = m.Book.objects.create(title=title, isbn=isbn, pub_date=pub_date, page_count=page_count)
  for author in authors:
    book.author.add(author.pk)
  if request.POST['image_url'] is not "":
    book.image_url = request.POST['image_url']
  for tag in tags:
    book.tags.add(tag)

  book.save()
  return searchISBN(request)

