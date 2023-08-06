"""
Get Lucky.

Usage:
  gl
  gl lucky [options]
  gl mood (<mood>) [-h | -l]
  gl genre (<genre>) [-h | -l]
  gl activity (<activity>) [-h|-l]

  

Options:
  -h  --help                Show this screen.

  -l  --list                list playlists available in a particular category so you can select a specifc playlist.

  -s, --smooth              You've somehow managed to coat everything in velour so everything is as smooth as you are. 
                            Exorbitantly expensive? Absolutely. But dammit you're worth it.

  -f, --fiesty              You throw in a tad more zest than the average person. Which usually means roaring like the
                            powerful jungle cat you are. Which usually doesn't go over well. 
                            Don't worry you'll find someone to call you El Tigre.
                            
  -x, --extreme             Christian Gray, Schmistian Gray. You know more knots than an Eagle Scout, 
                            have more leather than your local hell's angels chapter, and know that consent is key.
"""

from docopt import docopt
from collections import Iterable
from bs4 import BeautifulSoup
from string import maketrans 
from string import punctuation
import config
import subprocess as sub
import platform
import sys,os
import ConfigParser
import requests
import random
import string




class Playlister(object):

  def __init__(self):
    pass

  @staticmethod
  def getPlaylists(urls,idName,value,tagtype=True):
    """
    Returns a soup tag object that has data that allows us to accsess a playlist 
    from a url by using the identifier from the kwargs.
    
    For example the songza mood pages have  list items that look like this:

    <h3 class="browse-playlist-title"> Today's Americana </h3>

    In this case:
      tagtype = 'h3'
      idName = "class"
      value = "browse-playlist-title"

    We will return the li tag object so we can then use the station data-sz-station-id to play
    the playlist.

    We're returning a soup tag object instead of just directly playing from here so we can 
    extend functionality to diffrent services like Pandora. 

    """
    playlists = []
    for url in urls:      ## so we can pick a random from multiple categories
      html_page = requests.get(url,timeout=2)

      if html_page.status_code != requests.codes.ok:  
        print  "Unable to load webpage. Did you spell all your arguments correctly?"
        sys.exit(0)

      soup = BeautifulSoup(html_page.text)
      identifier={idName:value}
      playlists += soup.find_all(tagtype,attrs=identifier)
    return playlists


  @classmethod
  def randomPlaylist(cls, urls,idName,value,tagtype=True):
    return random.choice(cls.getPlaylists(urls,idName,value,tagtype))


class AbstractService(object):

  def __init__(self):
    self.proc = None

  def playRandom(self):
    abstract

  def openUrl(self,url):
    system = platform.system()
    if system=='Linux':      
      proc=sub.Popen(['xdg-open',url],stdout = sub.PIPE)
    elif system=='Darwin':
      proc=sub.Popen(['open',url],stdout = sub.PIPE)
    elif system=='Windows':
      proc = sub.Popen(['start',url],stdout = sub.PIPE,shell = True)
    else:
      raise Exception('OS not recognized.\nWhat does the python function platform.system() return?')


class Songza(AbstractService):

  def __init__(self,shortcuts):
    super(Songza,self).__init__()
    self.baseUrl = "http://songza.com"
    self.moods = self.baseUrl+"/discover/moods/"
    self.genres = self.baseUrl+"/discover/genres/"
    self.activity = self.baseUrl+"/discover/activities/"
    self.listen = self.baseUrl+"/listen/"
    self.calls = {'mood':self.moods,'genre':self.genres,'activity':self.activity}
    self.shortcuts = shortcuts


  def getUrls(self,categories):
    if not isinstance(categories, list):  categories = [categories]
    urls = [self.getCalls(category) for category in categories]
    return urls

  def getCalls(self, category):
    return self.calls[category[0]]+category[1]


  def openPlaylist(self, playlistTag):
    playlist = playlistTag.a.get('href')
    self.openUrl(self.baseUrl+playlist)

  def playlistTitle(self, playlistTag):
    return playlistTag.find('h3',class_='browse-playlist-title').text


  def playRandom(self,categories):

    """ 
      Plays random playlist from category

      args:
        categories list of tuples  denoting catageory and category type:
          ex: to play a playlist from the Seductive mood or the  makeout activities:
            categories = [('mood','Seductive'),('activities','makeout')]

      returns: nothing
    """
    
    urls = self.getUrls(categories)
    playlistTag = Playlister.randomPlaylist(urls,'class','browse-playlist playable',tagtype='li')
    self.openPlaylist(playlistTag)


  def validateSelection(self, selection, playlistsCount):
    validSelection = False

    getInput = lambda message: raw_input(message).strip()
    while not validSelection:

      if not selection.isdigit():
        selection = getInput('Selection must be an integer between {} and {}. '.format(1,playlistsCount))
        continue
      selection = int(selection)
      if not selection-1 in range(playlistsCount):
        message = 'Selection not valid. Pick a playlist from {} to {}. '.format(1, playlistsCount)
        selection = getInput(message)
        continue

      validSelection = True

    return selection



  def playSpecifc(self, categories):
    urls = self.getUrls(categories)
    playlists = Playlister.getPlaylists(urls,'class','browse-playlist playable',tagtype='li')

    for i, playlist in enumerate(playlists):
      print '{}: {}'.format(i+1, self.playlistTitle(playlist))


    getInput = lambda message: raw_input(message).strip()
    playlistsCount = len(playlists)
    selection = getInput('Select a playlist. ')
    selection = self.validateSelection(selection,playlistsCount)
    self.openPlaylist(playlists[selection-1])









def isValidArg(arg, signifer, input_dict):
  return signifer in  arg and input_dict[arg]

def getCmd(input_dict):
  return [cmd for cmd in input_dict if '-' not in cmd and '<' not in cmd and input_dict[cmd] ][0]

def getOptions(input_dict):
  return [ opt.replace('-','') for opt in input_dict if isValidArg(opt,'-', input_dict)] #get option name w/o -

def getArgs(input_dict):
  trans_tab =  maketrans('','')
  return {arg.translate(trans_tab, '<>'):input_dict[arg].lower() for arg in input_dict if isValidArg(arg,'<',input_dict)}

def sanitize(string,delimiter="_"):
  """ Makes arguments url friendly"""

  clean = string.translate(None, punctuation).replace(" ",delimiter)
  return clean

def handleInput(service, input_dict):
  getCategory = lambda option: service.shortcuts.get(option)
  cmd = getCmd(input_dict)
  options = getOptions(input_dict)
  args = getArgs(input_dict)
  listPlaylists = 'l' in options

  if listPlaylists:
    options.remove('l')
    playFn = service.playSpecifc
  else:
    playFn = service.playRandom



  if cmd == 'lucky':
    
    if options:
      categories = [getCategory(option) for option in options]

    else:
      categories=('activity','getting_lucky')

  else:
      value = args[cmd]
      categories = (cmd, sanitize(value))
      if value in service.shortcuts: #For custom genre/mood/ shortcuts.
        categories = getCategory(value)
        print "Using custom argument {}".format(value)

      

  playFn(categories)


 
def main():
    arguments = docopt(__doc__, version='Get Lucky 1.0')

    songza_shortcuts = config.Songza_Shortcuts
    if any(arguments[arg] for arg in arguments):
      s = Songza(songza_shortcuts)
      handleInput(s,arguments)
    else:
      print __doc__


if __name__ == '__main__':
  main()

    

