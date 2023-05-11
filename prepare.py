#standard imports
import pandas as pd
import numpy as np
import unicodedata
# we can regex for removeing special characters
import re
# import nltk. nltk is our python natural language tool kit
import nltk
import acquire as a

#---------------------------------------------------------------

def basic_clean(original_string):
    '''
    This will take in a string, make it all lowercase, normalize the characters to ascii
    and remove characters that are not letters, numbers or spaces
    '''
    # normalize the characters to ascii standart
    normalized = unicodedata.normalize('NFKD', original_string).\
        encode('ascii', 'ignore').decode('utf-8')
    # lowercase all the words in the data
    lowered = normalized.lower()
    # remove things that arent letters, numbers and spaces
    basic_cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', lowered)
    #return the cleaned string
    return basic_cleaned

#---------------------------------------------------------------

def tokenize(basic_cleaned):
    '''
    This will break up words into smaller, discrete (tokenized) units
    '''
    # grab our tokenizer from nltk
    tokenizer = nltk.tokenize.ToktokTokenizer()
    # tokenize the data
    tokenized = tokenizer.tokenize(basic_cleaned, return_str=True)
    # return the tokenized data
    return tokenized

#---------------------------------------------------------------

def stem(tokenized):
    '''
    This will cut a string of words down into their root words (PorterStemming)
    '''
    # create stemmer object
    stemmer = nltk.porter.PorterStemmer()
    # stem every word in the tokenized string
    stemmed = ' '.join([stemmer.stem(word) for word in tokenized.split()])
    # return the stemmed data
    return stemmed

#---------------------------------------------------------------

def lemmatize(tokenized):
    '''
    This will cut a string of words down into their root words (Lemmatizing)
    '''
    # create lemmatizer object
    lemmatizer = nltk.stem.WordNetLemmatizer()
    # lemmatize every word in the string
    lemmatized = ' '.join([lemmatizer.lemmatize(word) for word in tokenized.split()])
    # return the lemmatized string
    return lemmatized

#---------------------------------------------------------------

def remove_stopwords(string, extra_words=None, exclude_words=None):
    '''
    This will remove words that hold little meaning to a machine learning system
    such as: 'the' 'am', 'is', 'are',
    '''
    # get a list of the stopwords
    stopwords = nltk.corpus.stopwords.words('english')
    # add extra words to the stopwords list
    if extra_words:
        [stopwords.append(word) for word in extra_words]
    # remove the exclude words from the stopwords list if word is in the stopwords list
    if exclude_words:
        [stopwords.remove(word) for word in exclude_words 
                     if (word in stopwords)]
    # get the list of words that are not in the stopwords
    stops_removed = ' '.join([word for word in string.split() 
                              if word not in stopwords])
    # return the words not in the stopwords list
    return stops_removed

#---------------------------------------------------------------

def prepare_articles(articles, extra_words=None, exclude_words=None):
    '''
    this will take in a dictionary of articles and will convert characters
    to lowercase, ascii, and only letters, number or space characters. It
    will then tokenize each word, remove stopwords then stem and lemmatize every word
    it will the return a dataframe containing the: 
    title, original, cleaned, stemmed and lemmatized versions
    '''
    # create an empty dictionary to store the results
    cleaned_articles = {}
    
    # cycle through all the articles
    for i , article in enumerate(articles):
        # assign the article title to a title variable
        title = article['title']
        # clean the article content
        basic_cleaned = basic_clean(article['content'])
        # tokenize the words in the article
        tokenized = tokenize(basic_cleaned)
        # remove the stopwords from the article content
        cleaned = remove_stopwords(tokenized, 
                                   extra_words=extra_words, 
                                   exclude_words=exclude_words)
        # get the stemmed words from the article content
        stemmed = stem(cleaned)
        # get the lemmatized words from the article content
        lemmatized = lemmatize(cleaned)
        
        # create a dictionary containing the article title, original content
        # the cleaned version, stemmed version and lemmatized versions
        cleaned_article = {
            'title' : title,
            'original' : article['content'],
            'clean' : cleaned,
            'stemmed' : stemmed,
            'lemmatized' : lemmatized
        }
        
        # check if the passed articles have either url or category info
        # if they don't have either, then it will give a KeyError if we attempt to
        # work with the specified key
        try:
            # add url to the article dictionary if it exists in the original article
            cleaned_article['url'] = article['url']
        # accept a KeyError
        except KeyError:
            # move on with the function
            pass
        # check if the article has category info
        try:
            # add category info to the dictionary if it exists
            cleaned_article['category'] = article['category']
        # accept a KeyError if category info doesn't exist
        except KeyError:
            # move on with the function
            pass
        
        # add the cleaned article info to the dictionary of all articles
        cleaned_articles[i] = (cleaned_article)
    # return the cleaned articles info as a DataFrame with each article as a row
    return pd.DataFrame(cleaned_articles).T