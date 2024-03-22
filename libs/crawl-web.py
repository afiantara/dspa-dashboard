import pandas as pd
import requests
from bs4 import BeautifulSoup
from scrap import *

def crawl_me(url,url_base):
    print(url)
    get_images(url,url_base)
    #print(list_of_links)
    #is_exist = len(list_of_links)>0

    '''
    if list_of_links and is_exist:
        list_of_links=list(dict.fromkeys(list_of_links)) # remove duplicate key links
        list_all_links=[]
        last_of_pages=False
        while not last_of_pages:
            print('he..he.{}'.format(url))
            for lnk in list_of_links:
                if not 'http' in lnk:
                    _url="{}{}".format(url,lnk)
                else:
                    _url=lnk
                
                msg="second level: {}".format(_url)
                info(msg)
                #print(msg)
                lst=get_pdfs(_url,nama,1)
                if lst and len(lst)>0:
                    lst=list(dict.fromkeys(lst)) #remove duplicate.. 
                    if len(list_all_links)>0:
                        list_all_links.extend(lst)
                    else:
                        list_all_links=lst

                    list_all_links=list(dict.fromkeys(list_all_links)) # remove duplicate key links

            if len(list_all_links)>0:
                #should be check is already call in 2 putaran?
                comparelist=findarrayset(list_of_links,list_all_links)
                if len(comparelist)==0:
                    last_of_pages=True
                else:
                    list_of_links = list_all_links
                    list_all_links=set()

                #msg=f"third level:",list_of_links
                #print(msg)
                #list_all_links.clear()
                #print(len(list_of_links))
            else:
                last_of_pages=True
    '''
if __name__=="__main__":
    url = "https://www.aaji.or.id/Perusahaan"
    url_base="https://www.aaji.or.id"
    crawl_me(url,url_base)