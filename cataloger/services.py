# cataloger services
import requests
import xml.parsers.expat as expat

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