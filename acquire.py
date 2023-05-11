# import web scraping tools
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import re
import csv

#---------------------------------------------

def get_blog_links(url, headers):
    '''
    This will take in a url and header, and return a list of blog url links gathered
    from the blog selection pages
    '''
    # start at page 1
    page = 1
    # set our url
    page_url = f'{url}{page}'
    # get the first page results
    response = requests.get(page_url, headers=headers)
    # create an empty list to store the link urls
    link_list = []
    
    # go through every page until we get a status code other than 200
    while response.status_code == 200:
        # convert our received content into soup object
        soup = BeautifulSoup(response.content, 'html.parser')
        # have soup, will travel
        if soup:
            # get a list of items on the page with <a> tag
            article_list = soup.find_all('a', class_='entry-featured-image-url')
            # add each href url link to the link_list
            [link_list.append(article['href']) for article in article_list]
        else:
            print('page url has not returned any content')
            break
            
        # increment our page counter
        page += 1
        # set the url to the next page
        page_url = f'{url}{page}'
        # get the response for the next page
        response = requests.get(page_url, headers=headers)
        
    # return the list of blog url links
    return link_list

#---------------------------------------------

def get_blog_content(url, headers):
    '''
    This will gather the title and page content from the passed blog url
    '''
    # get the content from this blog
    response = requests.get(url, headers=headers)
    # check if we have correct response and if there is content in our response
    if response.status_code != 200: # if there is a page error
        print('page url has returned an error')
        return
        
    # convert our received content into soup object
    soup = BeautifulSoup(response.content, 'html.parser')
    if not soup: # if there is no soup
        # display an error message
        print('page has no content')
        return
    
    # have soup, will travel
    # gather the title from the <h2> tag
    title = soup.find('h1', class_='entry-title').text
    # get the blog content text, strip extra chars
    content = soup.find('div', class_='entry-content').text.strip()
    # create a regex function to search for the title, while ignoring case
    compiled = re.compile(re.escape(title), re.IGNORECASE)
    # remove the title from the content, while ignoring case
    content = compiled.sub('', content)
    
    # return the scraped title and content for this blog
    return title, content

#---------------------------------------------

def get_blog_articles(fresh=False):
    '''
    This will gather the title, url and content for every blog on the codeup website
    '''
    # assign a filename for cached data
    filename = 'codeup_blogs.csv'
    # if we dont need fresh data then check for a cached version
    if not fresh:
        # check for cached file
        if os.path.exists(filename):
            # if cached file exists, display a status message
            print(f'Opening file {filename} from local directory')
            # then open it
            with open(filename, "r") as f:
                csv_reader = csv.DictReader(f)
                content_dict = list(csv_reader)
            # return cached file, which will end the function
            return content_dict
        # if cached file not found
        else:
            # display a status message
            print(f'local file {filename} not found')
            # then download the data
    
    print('Downloading data from Codeup website')
    # set the url to the codeup blog pages
    url = 'https://codeup.com/blog/page/'
    # Some websites don't accept the pyhon-requests default user-agent
    headers = {'User-Agent': 'Codeup Data Science'}
    # display a status message
    print('Gathering blog links')
    # get a list of blog page urls
    link_list = get_blog_links(url, headers)
    # create an empty dictionary to store the results
    content_dict = []
    # display a status message
    print('Gathering blog content')
    # cycle through all the gathered blog links
    for blog in link_list:
        # gather the title and content for each page
        title, content = get_blog_content(blog, headers)
        # add a record to the dictionary with the title, url and content for the blog
        article = {'title':title, 'url':blog, 'content':content}
        content_dict.append(article)
        
    # cache the dictionary data to a csv
    pd.DataFrame(content_dict).to_csv(filename, index=False)
    # return the dictionary of blogs
    return content_dict

#---------------------------------------------

def get_news_articles(fresh=False):
    '''
    This will gather news articles from https://inshorts.com in the categories:
    business, sports, technology and entertainment. it will return the news articles
    as a dictionary
    '''
    filename = 'inshorts_news.csv'
    # check if we need fresh data
    if not fresh:
        # if we don't need fresh data, open the cached data 
        # check if data csv exists
        if os.path.exists(filename):
            # print status message
            print(f'Opening news data from local file {filename}')
            # open the local csv data
            with open(filename, "r") as f:
                csv_reader = csv.DictReader(f)
                inshorts = list(csv_reader)
            # return the dataset (ending the function)
            return inshorts
        # if the file is not found
        else:
            # print status message
            print(f'File {filename} not found in local directory')
    # download the data
    # print status message
    print('downloading news data from inshorts.com')
    # assign the url
    url = 'https://inshorts.com/en/read/'
    # request the data from the url
    response = requests.get(url)
    # check if good status code
    
    if response.status_code != 200:
        # print error status message
        print('error code from http request')
        return
    # if there is no error with the request
    # turn data into soup
    soup = BeautifulSoup(response.content, 'html.parser')
    # if we dont have soup, give an error
    if not soup:
        print('no content found on page')
        return
    # have soup, will travel
    
    # <li> is the category list
    # get rid of the all news category
    categories = [li.text.lower() for li in soup.select('li')][1:]
    # the india category link is actually 'national'
    categories[0] = 'national'
    # create an empty list to store data
    inshorts = []
    # cycle through every category
    for category in categories:
        # set the url
        url = 'https://inshorts.com/en/read/' + category
        # get the data
        response = requests.get(url)
        
        if response.status_code != 200:
            # print error status message
            print('error code from http request')
            return
        # if there is no error with the request
        # turn data into soup
        soup = BeautifulSoup(response.content, 'html.parser')
        # if we dont have soup, give an error
        if not soup:
            print('no content found on page')
            return
            
        # have soup, will travel
        # get the article titles
        titles = [span.text for span in soup.find_all('span', 
                                                  itemprop='headline')]
        # get the article content
        content = [div.text for div in soup.find_all('div', 
                                                 itemprop='articleBody')]
        # get the article url
        article_urls = [a['href'] for a in soup.find_all('a', 
                                                     class_='clickable')]
        # create a list of unique article urls while retaining the order
        urls = []
        # cycle through all the acquired article urls
        for url in article_urls:
            # if the url is not in the list
            if url not in urls:
                # add the unique urls to the list of article urls
                urls.append(url)
        # cycle through all the titles
        for i in range(len(titles)):
            # create a dictionary containing the current article
            article = {
                'title': titles[i],
                'content': content[i],
                'category': category,
                'url' : 'https://inshorts.com' + urls[i]
            }
            # add each article to our list of articles
            inshorts.append(article)
    
    # cache the dictionary data to a csv
    pd.DataFrame(inshorts).to_csv(filename, index=False)
    # return the news articles
    return inshorts