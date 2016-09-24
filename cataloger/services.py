# cataloger services
import requests
import xml.parsers.expat as expat
import cataloger.models as m

def getGoodReadsBookInfo(isbn):
  # Utility:
  openTags = []
  bookInfo = {}
  def startElement(name, attrs):
    openTags.append(name)
  def endElement(name):
    if name=="authors":
    # First occurance of this tag is all we're interested in
      bookInfo["done_authors"] = 1
    openTags.pop()
  def insideTag(data):
    # Check what tag we're in
    if len(openTags) == 0:
      return
    currentTag = openTags[len(openTags)-1]
    tagList = ["title", "publication_day", "publication_month", "publication_year", "num_pages", "image_url"]
    if currentTag in tagList and bookInfo.get(currentTag) is None:
      bookInfo[currentTag] = data
    # if we find a name and we're inside the authors tag
    # then we're looking at an author
    if currentTag == "name" and "authors" in openTags:
      if bookInfo.get("authors") is None:
        bookInfo["authors"] = []
      if bookInfo.get("done_authors") is None:
        print("author: "+data)
        bookInfo["authors"].append(data)
    if currentTag == "image_url":
      # Get the large image URL
      bookInfo[currentTag] = bookInfo[currentTag].replace("m/", "l/").replace(".col", ".com")

  # Actual function start:
  r = requests.get("https://goodreads.com/book/isbn?format=xml&key=jDPRQ54TVJY13j7gjEUw&isbn="+isbn)

  parser = expat.ParserCreate("UTF-8")
  parser.StartElementHandler = startElement
  parser.EndElementHandler = endElement
  parser.CharacterDataHandler = insideTag
  ascii_text = r.text.encode("UTF-8")
  parser.Parse(ascii_text, 1)

  return bookInfo

def findBooksWithTagProfile(tagProfile):
  """
  Finds all books with the provided tag profile, and returns a list of models.
   Parameters:
    tagProfile: a collection of tag ids, as either single id values, or lists of id values. 
      The former should represent a precise tag the caller is searching for, whereas the 
      list of id values should represent an unpacked tag group.
  Returns: list of book objects that match the tag profile.
    "Matches the tag profile" is defined as a book that, for each entry in the tag profile,
    the book has at least one tag in the list described by that tag profile entry.
  """
  books = m.Book.objects.all()
  for tag in tagProfile:
    currentTagList = []
    if not isinstance(tag, list):
      currentTagList.append(tag)
    else:
      currentTagList = tag
    books = filterBooksForAnyTagInSet(books, currentTagList)
  return books

def findBooksWithAllTags(tagIds):
  query = m.Book.objects.all()
  if(len(tagIds) is 0):
    query = {}
  for tag in tagIds:
    tagSet = []
    tagObject = m.Tag.objects.get(pk=tag)
    tagSet.append(tag)
    query = query.filter(tags__in=tagSet)
  return query

def filterBooksForAnyTagInSet(books, tagIds):
  """
  Filters the books collection for any books containing the tags provided.
  Parameters:
    tagIds: list of tag ids
    books: the Book model objects
  Returns: a subset of 'books' wherein each book has at least one tag from tagIds.
  """
  return books.filter(tags__in=tagIds)


def findAllTagsInGroup(groupId):
  group = m.TagGroup.objects.get(pk=groupId)
  tagObjects = []
  tagIds = []
  innerTagGroups = []
  innerTagGroups.append(group)
  iterations = 0
  while len(innerTagGroups) > 0 and iterations < 10000:
    currentGroup = innerTagGroups.pop()
    tagObjects.extend(currentGroup.tag_set.all())
    innerTagGroups.extend(currentGroup.taggroup_set.all())
    iterations = iterations + 1
  for tagObject in tagObjects:
    tagIds.append(tagObject.pk)
  return tagIds



