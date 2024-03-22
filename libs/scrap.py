import requests
from bs4 import BeautifulSoup
import urllib.request as ur
from collections import Counter
from string import punctuation
import os
from urllib.parse import urljoin
from log import *
import httpx

list_pdf_links=set()
# For extracting specific tags from webpage
def getTags(url,tag):
  s = ur.urlopen(url)
  soup = BeautifulSoup(s.read(),'lxml')
  return soup.findAll(tag)

# For extracting all h1-h6 heading tags from webpage
def headingTags(url,headingtags):
  h = ur.urlopen(url)
  soup = BeautifulSoup(h.read())
  print("List of headings from headingtags function h1, h2, h3, h4, h5, h6 :")
  for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
    print(heading.name + ' ' + heading.text.strip())

def alt_tag(url_input):
  url =  ur.urlopen(url_input)
  htmlSource = url.read()
  url.close()
  soup = BeautifulSoup(htmlSource)
  print('\n The alt tag along with the text in the web page')
  print(soup.find_all('img',alt= True))

def counting_words(url_input):
    
    # Getting content from web page
    r = requests.get(url_input)
    soup = BeautifulSoup(r.content,features="lxml")
    # For getting words within paragrphs
    text_paragraph = (''.join(s.findAll(text=True))for s in soup.findAll('p'))
    count_paragraph = Counter((x.rstrip(punctuation).lower() for y in text_paragraph for x in y.split()))

    # For getting words inside div tags
    text_div = (''.join(s.findAll(text=True))for s in soup.findAll('div'))
    count_div = Counter((x.rstrip(punctuation).lower() for y in text_div for x in y.split()))

    # Adding two counters for getting a list with words count (from most to less common)
    total = count_div + count_paragraph
    list_most_common_words = total.most_common() 

# For extracting specific title & meta description from webpage
def titleandmetaTags(url):
    s = ur.urlopen(url)
    soup = BeautifulSoup(s.read(),'lxml')
    #----- Extracting Title from website ------#
    title = soup.title.string
    print ('Website Title is :', title)
    #-----  Extracting Meta description from website ------#
    meta_description = soup.find_all('meta')
    for tag in meta_description:
        if 'name' in tag.attrs.keys() and tag.attrs['name'].strip().lower() in ['description', 'keywords']:
            #print ('NAME    :',tag.attrs['name'].lower())
            print ('CONTENT :',tag.attrs['content'])

def broken_page(url):
    # For making request to get the URL
    user_req_page = requests.get(url)

    # For getting the response code of given URL
    response_code = str(user_req_page.status_code)

    # For displaying the text of the URL in str
    data =user_req_page.text

    # For using BeautifulSoup to access the built-in methods
    soup = BeautifulSoup(data)

    # Iterate over all links on the given URL with the response code next to it i.e 404 for PAGE NOT FOUND, 200 if website is functional/available
    for link in soup.find_all('a'):
        print(f"Url: {link.get('href')} " + f"| Status Code: {response_code}")

def get_images(url,urlbase):
    
    read = requests.get(url, timeout=5)
    if read.status_code == 200:
        # full html content 
        html_content = read.content
        # Parse the html content 
        soup = BeautifulSoup(html_content, "html.parser")
        img_tags = soup.find_all("img")
        for img in img_tags:
            try:
                img_url = urlbase + img.get("src")
                print(img_url)
                local_file_path=img_url.split('/')[-1]
                local_file_path='./libs/imgs/{}'.format(local_file_path)
                print(local_file_path)
                ur.urlretrieve(img_url, local_file_path)    
            except Exception:
                print('error')
def get_pdfs(url,nama,level=0):
    try:
        folder_location = r'./pdfs/{}/'.format(nama)
        if not os.path.exists(folder_location):os.mkdir(folder_location)
    except Exception as e:
        error(e)

    list_of_links=set()
    # get the url from requests get method
    try:
        matches=['twitter','facebook']
        is_exist= any(x in url for x in matches)
        if is_exist: return 
        read = requests.get(url, timeout=5)
        if read.status_code == 200:
            # full html content 
            html_content = read.content
            # Parse the html content 
            soup = BeautifulSoup(html_content, "html.parser")

            # created an empty list for putting the pdfs 
            #list_of_pdf = set()
            # accessed the first p tag in the html 
            #l = soup.find('p') 
            
            # accessed all the anchors tag from given p tag
            p = soup.find_all('a') 
            # iterate through p for getting all the href links
            for link in p: 
                # original html links
                current_link = link.get('href')
                print("links: ", current_link)
                #info(current_link.lower())
                #key of searching criteria
                matches=['financial','finansial','laporan','keuangan']
                is_exist=current_link and any(x in current_link.lower() for x in matches)
                if not is_exist: continue
                try:
                    matches=['laporan','keuangan']
                    is_exist=current_link and any(x in current_link.lower() for x in matches) 
                    #info(is_exist)
                    if  is_exist and current_link.endswith('pdf'):
                        if len(list_pdf_links)>0:
                            if not current_link in list_pdf_links: 
                                list_pdf_links.add(current_link)
                            else:
                                continue
                        else:
                            list_pdf_links.add(current_link)

                        print('Tengo un pdf: ' + current_link)
                        pdf_links="{}{}".format(url,current_link)
                        filename = os.path.join(folder_location,current_link.split('/')[-1])
                        with open(filename, 'wb') as f:
                            f.write(requests.get(urljoin(url,link['href'])).content)
                            # added all the pdf links to set
                            #list_of_pdf.add(pdf_links)
                    else:
                        #print("links: ", current_link)
                        #info(current_link)
                        list_of_links.add(current_link)
                except Exception as e:
                        error(e)
        else:
            print('response:{}-{}-{}'.format(nama,url,read.status_code))
            list_of_links.clear()
    except Exception as e:
        error(e)
    
    return list_of_links
'''
def info(pdf_path):
 
    # used get method to get the pdf file
    response = requests.get(pdf_path)
 
    # response.content generate binary code for
    # string function
    with io.BytesIO(response.content) as f:
 
        # initialized the pdf
        pdf = PdfFileReader(f)
 
        # all info about pdf
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
 
    txt = f"""
    Information about {pdf_path}: 
     
    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    """
    print(txt)
     
    return information
'''