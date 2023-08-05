import requests
import re
import json
from csv import reader
from time import sleep
from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):

    #RSC scraping implementation
    def handle_starttag(self, tag, attrs):
      if tag == 'a' and ('id', 'pdfLink') in attrs:
        for attr in attrs:
          if attr[0] == 'href':
            self.download_link = attr[1]

class ArticleDownloader:

  def __init__(self, api_key):
    self.headers = {'X-ELS-APIKEY': api_key}
    self.piis = []
    self.dois = []
    self.xmls = []
    self.queries = []
    self.api_key = api_key

  def get_piis_dois_from_search(self, query, mode):
    if mode == 'elsevier':
      url = 'http://api.elsevier.com/content/search/scidir?query=' + query
    elif mode == 'rsc':
      url = 'http://search.crossref.org/dois?q=' + query
    elif mode == 'nature':
      url = 'http://api.nature.com/content/opensearch/request?query=' + query + '&api_key=' + self.api_key
    elif mode == 'springer':
      url = 'http://api.springer.com/metadata/pam?q=' + query + '&api_key=' + self.api_key
    else:
      print 'Valid mode required! Failed to get PIIs/DOIs from search.'
      return -1
    try:
      self.headers['Accept'] = 'application/json'
      response = requests.get(url, headers=self.headers).content
      json_response = json.loads(response)

      if mode == 'elsevier':
        for article in json_response['search-results']['entry']:
          if article['pii'] not in self.piis:
            self.piis.append(article['pii'])

        self.piis = list(set(self.piis)) #Guarantee uniqueness of IDs
        return len(self.piis)

      elif mode == 'rsc':
        for article in json_response:
          doi = article['doi']
          if doi.find('10.1039') > 0: #RSC DOI code
            doi = doi.replace('http://dx.doi.org/10.1039/', '')
            if doi not in self.dois:
              self.dois.append(doi)
        self.dois = list(set(self.dois)) #Guarantee uniqueness of IDs
        return len(self.dois)

    except requests.exceptions.ConnectionError:
      print '***API search limit exceeded!***'
      print 'Waiting 1000 seconds before trying again'
      sleep(1000) #API request limit exceeeded; wait and try again
      return -1
    except KeyError:
      print 'Failed search query!'
      return -1


  def get_piis_from_file(self, file):
    with open(file) as f:
      for pii in f:
        pii = re.sub('[\-\(\)]', '', pii)
        if pii not in self.piis:
          self.piis.append(pii)

  def get_xml_from_pii(self, pii):
    try:
      xml_url='http://api.elsevier.com/content/article/PII:' + pii + '?view=FULL'
      xml_response = requests.get(xml_url, headers=self.headers).content
      self.xmls.append(xml_response)
    except requests.exceptions.ConnectionError:
      print '***API download limit exceeded!***'
      print 'Waiting 1000 seconds before trying again'
      sleep(1000) #API request limit exceeded; wait and try again

  def get_pdf_from_pii(self, pii, directory):
    try:
      name = re.sub('[\(\)]', '', pii)
      name = re.sub('\s+', '', name)
      self.article_path = directory + name
      self.article_path += '.pdf'

      pdf_url='http://api.elsevier.com/content/article/PII:' + pii + '?view=FULL'
      self.headers['Accept'] = 'application/pdf'

      r = requests.get(pdf_url, stream=True, headers=self.headers)
      if r.status_code == 200:
        with open(self.article_path, 'wb') as f:
          for chunk in r.iter_content(2048):
              f.write(chunk)
          print 'Downloaded file successfully!'
    except requests.exceptions.ConnectionError:
      print '***API download limit exceeded!***'
      print 'Waiting 1000 seconds before trying again'
      sleep(1000) #API request limit exceeded; wait and try again

  def scrape_article(self,  mode, directory, pii=None, doi=None, regex=True):
    try:
      if mode == 'elsevier':
        url = 'http://www.sciencedirect.com/science/article/pii/' + pii + '/'
      elif mode == 'rsc':
        url = 'http://pubs.rsc.org/en/content/articlepdf/1/cc/' + doi
      resp = requests.get(url, headers=self.headers)
      html = resp.content
    except:
      print "Couldn't locate download URL!"
      return

    print
    print
    print 'Downloading from: ' + url

    if doi is None:
      name = re.sub('[\(\)]', '', pii)
    else:
      name = doi

    self.article_path = directory + name
    self.article_path += '.pdf'

    if regex:
      htmlparse = MyHTMLParser()
      htmlparse.download_link = None
      htmlparse.feed(html)

      if htmlparse.download_link is not None:
        download_url = htmlparse.download_link
    else:
      download_url = url

    r = requests.get(download_url, stream=True, headers=self.headers)
    if r.status_code == 200:
      with open(self.article_path, 'wb') as f:
        for chunk in r.iter_content(2048):
            f.write(chunk)
        print 'Downloaded file successfully!'

  def save_xml_data(self, xml, path):
    print 'Saved XML to: ' + path
    with open(path, 'wb') as f:
      f.write(xml)

  def load_queries_from_csv(self, csvf, limit=500, start=0, count=1):
    with open(csvf, 'rU') as f:
      csvreader = reader(f, delimiter=',')
      for i, line in enumerate(csvreader):
        if i > limit:
          break

        if i >= start:
          #Build search query (assume 1st column is article titles)
          title = re.sub('\[\]\=\,\.0-9\>\<\:]', '', line[0])
          title = re.sub('\(.*?\)', '', title)
          title = re.sub('\/', '\s', title)
          title = title.split()

          #filter out short words and long words
          title = [word for word in title if 3 < len(word) < 15]
          title = '+'.join(title)

          query = title

          if 0 < count < 100:
            query += '&count=' + str(count)
            self.queries.append(query)
          elif count > 100:
            for j in range(0, count, 100):
              split_query = query + '&count=100&start=' + str(j)
              self.queries.append(split_query)
