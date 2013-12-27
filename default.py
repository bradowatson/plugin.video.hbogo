#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import urlparse
import uuid
import socket
import cookielib
import sys
import re
import os
import json
import time
import shutil
import subprocess
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
from cookielib import CookieJar

#http://i.hbo.lv3.hbogo.com/default/HBOGO.stage.default.jpg

BASE_URL = 'http://hbogo.com'
CATALOG_URL = 'http://catalog.lv3.hbogo.com'

# Main Menu
NAV_URL = CATALOG_URL + '/apps/mediacatalog/rest/navigationBarService/HBO/navigationBar/NO_PC'
# Main category page called from main menu to load landing bar on page
LANDING_URL = CATALOG_URL + '/apps/mediacatalog/rest/landingService/HBO/landing/%s'
# Category pages to filter category page (A-Z, Genre)
QUICKLINKS_URL = CATALOG_URL + '/apps/mediacatalog/rest/quicklinkService/HBO/quicklink/%s'
# HBO uses a couple different XML layouts for pages (ex: Bundle = TV Seasons)
BUNDLE_URL = 'http://catalog.lv3.hbogo.com/apps/mediacatalog/rest/productBrowseService/HBO/bundle/%s'
CATEGORY_URL = 'http://catalog.lv3.hbogo.com/apps/mediacatalog/rest/productBrowseService/HBO/category/%s'

NAMESPACE = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

# Page used to pull up video
STREAM_URL = 'http://www.hbogo.com/#series/video&assetID=%s?videoMode=embeddedVideo?showSpecialFeatures=false&provider=%s'

# Dont show this items on the main menu
MENU_SKIP = [ 'Free', 'Home']

# Providers that we have setup.
PROVIDERS = {"Astound":"astound","AT&T U-verse":"att","Atlantic Broadband":"atlantic_broadband","ATMC":"atmc","BendBroadband":"bend","Blue Ridge Communications":"blue_ridge","Bright House Networks":"bright_house","Buckeye CableSystem":"buckeye","Burlington Telecom":"burlington","Cable ONE":"cable_one","CenturyLink Prism":"centrylink","Charter":"charter","Cincinnati Bell Fioptics":"cincinnati","Comcast XFINITY":"comcast","Cox":"cox","DIRECTV":"directv","DIRECTV PUERTO RICO":"directv_pr","DISH":"dish","Easton Cable Velocity":"easton","EPB Fiber Optics":"epb_fiber_optics","GCI":"gci","Grande Communications":"grande","GVTC Communications":"gvtc","Hawaiian Telcom":"hawaiian","HBC":"hbc","Home Telecom":"home_telecom","Home Town Cable Plus":"home_town_cable","Hotwire Communications":"hotwire","HTC Digital Cable":"htc","Insight Communications":"insight","JEA":"jea","Long Lines":"long_limes","LUS Fiber":"lus","Massillon Cable/Clear Picture":"massillon","Mediacom":"mediacom","MetroCast":"metrocast","MI-Connection":"mi_connection","Midcontinent Communications":"midcontinent","Nex-Tech":"nex_tech","OpenBand Multimedia":"openband","Optimum":"optimum","RCN":"rcn","Service Electric Broadband":"service_electric_broadband","Service Electric Cable TV":"service_electric_cable_tv","Service Electric Cablevision":"service_electric_cablevision","Suddenlink":"suddenlink","Time Warner Cable":"timewarner","Verizon FiOS":"verizon","Wave Broadband":"wave","WOW!":"wow"}

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
cj = cookielib.MozillaCookieJar()
urlMain = "http://www.hbogo.com"
osWin = xbmc.getCondVisibility('system.platform.windows')
osLinux = xbmc.getCondVisibility('system.platform.linux')
osOsx = xbmc.getCondVisibility('system.platform.osx')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
utilityPath = xbmc.translatePath('special://home/addons/'+addonID+'/resources/HBOGo_Utility.exe')
downloadScript = xbmc.translatePath('special://home/addons/'+addonID+'/download.py')
searchHistoryFolder = os.path.join(addonUserDataFolder, "history")
cacheFolder = os.path.join(addonUserDataFolder, "cache")
cacheFolderCoversTMDB = os.path.join(cacheFolder, "covers")
cacheFolderFanartTMDB = os.path.join(cacheFolder, "fanart")
libraryFolder = xbmc.translatePath("special://profile/addon_data/"+addonID+"/library")
libraryFolderMovies = xbmc.translatePath("special://profile/addon_data/"+addonID+"/library/Movies")
libraryFolderTV = xbmc.translatePath("special://profile/addon_data/"+addonID+"/library/TV")
cookieFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/cookies")
profileFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/profile")
authFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/authUrl")
localeFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/locale")
dontUseKiosk = addon.getSetting("dontUseKiosk") == "true"
showAllEpisodesInVA = addon.getSetting("showAllEpisodesInVA") == "true"
hideMoviesInVA = addon.getSetting("hideMoviesInVA") == "true"
browseTvShows = addon.getSetting("browseTvShows") == "true"
singleProfile = addon.getSetting("singleProfile") == "true"
showProfiles = addon.getSetting("showProfiles") == "true"
forceView = addon.getSetting("forceView") == "true"
useUtility = addon.getSetting("useUtility") == "true"
updateDB = addon.getSetting("updateDB") == "true"
useTMDb = addon.getSetting("useTMDb") == "true"
username = addon.getSetting("username")
password = addon.getSetting("password")
provider = addon.getSetting("provider")
zipcode = addon.getSetting("zipcode")
viewIdVideos = addon.getSetting("viewIdVideos")
viewIdEpisodes = addon.getSetting("viewIdEpisodes")
viewIdActivity = addon.getSetting("viewIdActivity")
winBrowser = int(addon.getSetting("winBrowserNew"))
osxBrowser = int(addon.getSetting("osxBrowser"))
language = ""
country = ""
if os.path.exists(localeFile):
    fh = open(localeFile, 'r')
    language = fh.read()
    fh.close()
    country = language.split("-")[1]
auth = ""

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
userAgent = "Mozilla/5.0 (Windows NT 5.1; rv:25.0) Gecko/20100101 Firefox/25.0"
opener.addheaders = [('User-agent', userAgent)]

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not os.path.isdir(cacheFolder):
    os.mkdir(cacheFolder)
if not os.path.isdir(cacheFolderCoversTMDB):
    os.mkdir(cacheFolderCoversTMDB)
if not os.path.isdir(cacheFolderFanartTMDB):
    os.mkdir(cacheFolderFanartTMDB)
if not os.path.isdir(libraryFolder):
    os.mkdir(libraryFolder)
if not os.path.isdir(libraryFolderMovies):
    os.mkdir(libraryFolderMovies)
if not os.path.isdir(libraryFolderTV):
    os.mkdir(libraryFolderTV)
if os.path.exists(cookieFile):
    cj.load(cookieFile)
if os.path.exists(authFile):
    fh = open(authFile, 'r')
    auth = fh.read()
    fh.close()

while (username == "" or password == ""):
    addon.openSettings()
    username = addon.getSetting("username")
    password = addon.getSetting("password")
    zipcode = addon.getSetting("zipcode")
    provider = addon.getSetting("provider")

####################################################################################################

class HBOGO:
    def __init__(self):
        try:
            #self.hbo_auth_cookie = __settings__.getSetting("hbo_auth_cookie")
            #self.hbo_saml_cookie = __settings__.getSetting("hbo_saml_cookie")
            #self.remember_me = __settings__.getSetting("login_data")
            #self.udid = __settings__.getSetting("udid")
            #self.stream_quality = __settings__.getSetting("quality")
            # LEVEL3 / LIMELIGHT / VELOCIX
            self.cdn = "VELOCIX"
            if self.session_is_valid():
                self.user_tkey = re.search('"tkey":"(.*?)"', urllib2.unquote(self.hbo_auth_cookie)).group(1)
            else:
                #self.connectedLogin()
                print "skip this"
	except:
            print "Error during HBOGO init: %s" % sys.exc_info()[0]

    def get_url(self, url):
        cj = CookieJar()
        session = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),urllib2.HTTPSHandler)
        session.addheaders.append(('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'))
        #session.addheaders.append(('Cookie', "auth=%s;saml=%s" % (self.hbo_auth_cookie, self.hbo_saml_cookie)))
        data = session.open(url).read()
        return data

    # Verify if existing session cookies are valid
    def session_is_valid(self):
        data = self.get_url('https://register.hbogo.com/apps/profile/rest/device/secure/active.json')
        return self.valid_response(data)

    # Get user info
    def get_affiliate(self):
        data = self.get_url('https://profile.hbogo.com/apps/profile/rest/profileService/secure/user.json')
        json_data = json.loads(data)['response']['body']
        print json_data
        return json_data['affiliateCode']

    # Verify this response is OK and not an ERROR, returning True or False
    def valid_response(self, response):
        json_data = json.loads(response)
        print json_data['response']['responseType']
        try:
            if json_data['response']['responseType'] == "OK":
                return True
            else:
                return False
        except:
            print "HBOGO ERROR: Error validating response"
            return False

    # Generate a PIN for device activation
    def generatePin(self):
        device_uuid = str(uuid.uuid4())
        __settings__.setSetting("udid", device_uuid)
        response = self.get_url('https://register.hbogo.com/apps/profile/rest/device/pin.json?deviceModel=DESKTOP&deviceSerialNumber=%s&deviceCode=DESKTOP&platformCode=TV' % device_uuid)
        json_data = json.loads(response)
        try:
            if self.valid_response(response):
                pin = json_data['response']['body']
                __settings__.setSetting("generated_pin", pin)
                return pin
            else:
                print "generatePin() ERROR: %s" % json_data
                return False
        except:
            print "generatePin() ERROR: %s" % sys.exc_info()[0]
            return False

    # Generate login XML for paired devices
    def buildLoginXML(self, login_data):
        xml = "<rememberMeLoginRequest><token>%s</token><userTkey>%s</userTkey><udid>%s</udid><expirationTime>%s</expirationTime><authnDataElement>%s</authnDataElement></rememberMeLoginRequest>" % (login_data['token'], login_data['userTkey'], self.udid, login_data['expirationTime'], login_data['authnDataElement'])
        print "LOGIN XML: %s" % xml
        return xml
    # Pair device to generated PIN
    def connectPin(self, pin):
        response = self.get_url('http://register.hbogo.com/apps/profile/rest/device/connect.json?devicePin=%s' % pin)
        json_data = json.loads(response)
        try:
            if self.valid_response(response):
                login_data = json_data['response']['body']
                login_response = self.buildLoginXML(login_data)
                __settings__.setSetting("login_data", login_response)
                self.connectedLogin()
                return True
            else:
                print "connectPin() ERROR: %s" % json_data
                return False
        except:
            print sys.exc_info()[0]
            return False

    def deactivateDevice(self):
        self.getJson("http://register.hbogo.com/apps/profile/rest/device/secure/deactivate?serviceCode=HBO&deviceCode=DESKTOP&deviceSerialNumber=%s" % self.udid)
        print "De-activating device %s" % self.udid

    # Login with paired credentials
    def connectedLogin(self):
        try:
            cj = CookieJar()
            session = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),urllib2.HTTPSHandler)
            req = urllib2.Request('https://register.hbogo.com/apps/profile/rest/profileService/connectedtvlogin', self.remember_me, { 'Content-Type': 'text/xml' })
            response = session.open(req).read()
            json_data = json.loads(response)
            if json_data['clientLoginRequest']['loginStatus'] == "success":
                hbo_auth_cookie = cj._cookies['.hbogo.com']['/']['auth'].value
                hbo_saml_cookie = cj._cookies['.hbogo.com']['/']['saml'].value
                self.hbo_auth_cookie = hbo_auth_cookie
                self.hbo_saml_cookie = hbo_auth_cookie
                __settings__.setSetting("hbo_auth_cookie", hbo_auth_cookie)
                __settings__.setSetting("hbo_saml_cookie", hbo_saml_cookie)
                __settings__.setSetting("login_data", self.buildLoginXML(json_data['clientLoginRequest']['rememberMeToken']))
                return True
            else:
                print "connectedLogin() ERROR: %s" % json_data
                return False
        except:
            print "connectedLogin() ERROR: %s" % sys.exc_info()[0]
            return False

    # Get json and return the body
    def getJson(self, tkey):
        print "tkey is :" + tkey
        data = self.get_url('%s.json' % tkey)
        json_data = json.loads(data)
        if self.valid_response(data):
            json_data = json_data['response']['body']
            return json_data
        else:
            print "getJson() ERROR: %s" % json_data
            return False

    def quicklinkService(self, uri):
        data = self.get_url('http://catalog.lv3.hbogo.com/apps/mediacatalog/rest/quicklinkService/HBO/quicklink/%s.json' % uri)
        json_data = json.loads(data)
        if self.valid_response(data):
            return json_data['response']['body']['quicklinks']['quicklinkElement']
        else:
            print "quicklinkService ERROR! %s" % json_data
            return False

hbo = HBOGO()


def get_param(p):
    try:
        return params[p]
    except:
        return False

def getCatalogTypes():
    return {"Series": "SE",
            "Movies": "MO",
            "Comedy": "CO",
            "Sports": "ST",
            "Documentaries": "DO",
            "Late Night": "LN" }

def getAssetImage(items):
    for image in items['imageResponses']:
        if image['mediaSubType'] == "SLIDESHOW":
            return image['resourceUrl']

def getAssetVideo(items):
    for video in items:
        if video['mediaSubType'] == "WEB_ADAPTIVE":
            return video['TKey']

def get_params(items,mode,feature_bundle=False):
    url_items = {}
    info_items = {}
    url_items['mode'] = mode
    if feature_bundle:
        url_items['feature_bundle'] = 1

    url_items['thumbnail'] = getAssetImage(items)

    for item,v in items.iteritems():
        if item == "primaryGenre":
            url_items['genre'] = v
            info_items['genre'] = v
        elif item == "title":
            url_items['title'] = v
            info_items['title'] = v
        elif item == "year":
            url_items['year'] = v
            info_items['year'] = v
        #elif item == "videoResponses":
            #url_items['stream_tkey'] = getAssetVideo(v)
            #info_items['stream_tkey'] = getAssetVideo(v)
        elif item == "featureResponses":
            url_items['TKey'] = v
            info_items['Tkey'] = v
        elif item == "TKey":
            url_items['catalog_tkey'] = v
            info_items['catalog_tkey'] = v
        elif item == "ratingResponse":
            url_items['mpaa'] = v['rating']
            info_items['mpaa'] = v['rating']
        elif item == "summary":
            url_items['plot'] = v
            info_items['plot'] = v
        elif item == "episodeCount":
            info_items['count'] = int(v)
        elif item == "episodeInSeries":
            info_items['episode'] = v
        elif item == "startDate":
            if not v == "0":
                info_items['aired'] = v
        elif item == "season":
            match = re.search(r"\d+", v)
            if match:
                info_items['season'] = match.group()




    # Encode URL string
    u = sys.argv[0] + "?" + urllib.urlencode(url_items)

    return {"url": u, "info": info_items}

# 0
def build_main_directory():
    for k,v in getCatalogTypes().iteritems():
        listitem = xbmcgui.ListItem( label = k,)
        u = sys.argv[0] + "?mode=1&name=" + urllib.quote_plus( k ) + "&uri=" + urllib.quote_plus( v )
        ok = xbmcplugin.addDirectoryItem( handle = int( sys.argv[1] ), url = u, listitem = listitem, isFolder = True )
        print u
    xbmcplugin.addSortMethod( handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( int( sys.argv[1] ) )

# 1
def build_category_folders(uri,name):
    print uri
    for sub in hbo.quicklinkService(uri):
        if sub.has_key("uri") and re.search("productBrowseService|categoryBrowseService", sub['uri']):
            listitem = xbmcgui.ListItem(label = sub['displayName'])
            u = sys.argv[0] + "?mode=2&name=" + urllib.quote_plus(name) + "&uri=" + urllib.quote_plus(sub['uri'])
            print u
            ok = xbmcplugin.addDirectoryItem( handle = int( sys.argv[1] ), url = u, listitem = listitem, isFolder = True )
            print u
    xbmcplugin.addSortMethod( handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( int( sys.argv[1] ) )

def build_category_items(uri,name):
    print uri

    if re.search("productBrowseService", uri):
        product = hbo.getJson(uri)['productResponses']

        # Regular products -- Movies/Sports/Late Night/Docs/Comedy
        if product.has_key('featureResponse'):
            for item in product['featureResponse']:
                if name == "Movies" or "Documentaries":
                    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
                else:
                    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

                # Get info items
                these_params = get_params(item, 3)

                # List item
                image = getAssetImage(item)
                liz = xbmcgui.ListItem(str(item['title']), image, image)
                liz.setProperty('fanart_image', image)
                liz.setThumbnailImage(image)
                liz.setProperty('isPlayable', 'true')
                liz.setInfo( type="Video", infoLabels=these_params['info'])

                # Add this item to the folder
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=these_params['url'], listitem=liz, isFolder=False)
                print url
            xbmcplugin.endOfDirectory(int(sys.argv[1]))

    elif re.search("categoryBrowseService", uri):
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        product = hbo.getJson(uri)
        if product.has_key('categoryResponses'):
            for item in product['categoryResponses']['bundleCategory']:
                title = item['title']
                summary = item['summary']
                tkey = item['TKey']
                these_params = get_params(item, 4)

                # List item
                image = getAssetImage(item)
                liz = xbmcgui.ListItem(item['title'], image, image)
                liz.setProperty('fanart_image', image)
                liz.setThumbnailImage(image)
                liz.setInfo( type="Video", infoLabels=these_params['info'])

                # Add this item to the folder
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=these_params['url'], listitem=liz, isFolder=True)
            xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_bundles(name):
    if get_param("feature_bundle"):
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        catalog = hbo.getJson("http://catalog.lv3.hbogo.com/apps/mediacatalog/rest/productBrowseService/HBO/bundle/%s" % params['catalog_tkey'])
        print "Catalog: " + str(catalog)
    else:
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_TITLE)
        catalog = hbo.getJson("http://catalog.lv3.hbogo.com/apps/mediacatalog/rest/productBrowseService/HBO/category/%s" % params['catalog_tkey'])
        print "Catalog: " + str(catalog)
    for bundle in catalog['productResponses']['bundleResponse']:
        if not get_param("feature_bundle"):
            these_params = get_params(bundle, 4, feature_bundle=True)
            image = getAssetImage(bundle)
            liz = xbmcgui.ListItem(bundle['title'], image, image)
            liz.setProperty('fanart_image', image)
            liz.setThumbnailImage(image)
            liz.setInfo(type="Video", infoLabels=these_params['info'])


        if get_param("feature_bundle"):
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_EPISODE)
            for feature in bundle['featureResponses']:
                feature_params = get_params(feature, 3)
                image = getAssetImage(feature)
                feature_item = xbmcgui.ListItem(feature['title'], image, image)
                feature_item.setProperty('fanart_image', image)
                feature_item.setThumbnailImage(image)
                feature_item.setProperty('isPlayable', 'true')
                feature_item.setInfo(type="Video", infoLabels=feature_params['info'])
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=feature_params['url'], listitem=feature_item, isFolder=False)

        # Add this item to the folder
        if not get_param("feature_bundle"):
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=these_params['url'], listitem=liz, isFolder=True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
def play_video(name):
    xbmc.Player().stop()
    url = STREAM_URL % (params['catalog_tkey'], "charter")
    print "URL: " + url
    kiosk = "yes"
    if dontUseKiosk:
        kiosk = "no"
    if osOsx:
        if osxBrowser == 0:
            xbmc.executebuiltin("RunPlugin(plugin://plugin.program.chrome.launcher/?url="+urllib.quote_plus(url)+"&mode=showSite&kiosk="+kiosk+")")
        elif osxBrowser == 1:
            subprocess.Popen('open -a "/Applications/Safari.app/" '+url, shell=True)
        try:
            xbmc.sleep(10000)
            subprocess.Popen('cliclick c:500,500', shell=True)
            subprocess.Popen('cliclick kp:arrow-up', shell=True)
            xbmc.sleep(5000)
            subprocess.Popen('cliclick c:500,500', shell=True)
            subprocess.Popen('cliclick kp:arrow-up', shell=True)
        except:
            pass
    elif osLinux:
        xbmc.executebuiltin("RunPlugin(plugin://plugin.program.chrome.launcher/?url="+urllib.quote_plus(url)+"&mode=showSite&kiosk="+kiosk+"&userAgent="+urllib.quote_plus(userAgent)+")")
        try:
            xbmc.sleep(10000)
            subprocess.Popen('xdotool mousemove 9999 9999 click 1', shell=True)
            xbmc.sleep(5000)
            subprocess.Popen('xdotool mousemove 9999 9999 click 1', shell=True)
            xbmc.sleep(5000)
            subprocess.Popen('xdotool mousemove 9999 9999 click 1', shell=True)
        except:
            pass
    elif osWin:
        if winBrowser == 1:
            path = 'C:\\Program Files\\Internet Explorer\\iexplore.exe'
            path64 = 'C:\\Program Files (x86)\\Internet Explorer\\iexplore.exe'
            if os.path.exists(path):
                subprocess.Popen('"'+path+'" -k "'+url+'"', shell=False)
            elif os.path.exists(path64):
                subprocess.Popen('"'+path64+'" -k "'+url+'"', shell=False)
        else:
            xbmc.executebuiltin("RunPlugin(plugin://plugin.program.chrome.launcher/?url="+urllib.quote_plus(url)+"&mode=showSite&kiosk="+kiosk+")")
        if useUtility:
            subprocess.Popen('"'+utilityPath+'"', shell=False)

# Get parameters -- lol
params = dict(urlparse.parse_qsl(urlparse.urlsplit(sys.argv[2])[3]))

mode = None
name = None
url = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    uri = urllib.unquote_plus(params["uri"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass




def generate_pin_message():
    dialog = xbmcgui.Dialog()
    pin = hbo.generatePin()
    if pin:
        pin_message = "2) Choose XBOX, then enter PIN: %s" % pin
        dialog.ok("HBOGo Device Pairing", "1) Go to http://www.hbogo.com/activate/", pin_message, "3) Once confirmed online, press OK to continue")

def validate_pin_message():
    pin = __settings__.getSetting("generated_pin")
    dialog = xbmcgui.Dialog()
    if hbo.connectPin(pin):
        pin_message = "You have successfully paired this device. Enjoy!"
        pin_header = "Pairing successful!"
        build_main_directory()
    else:
        pin_message = "There was an error pairing this device!"
        pin_header = "Pairing error!"
    dialog.ok(pin_header, pin_message)


if mode == None:
    build_main_directory()
#    if hbo.session_is_valid():
#        build_main_directory()
#
#    elif hbo.connectedLogin():
#        build_main_directory()
#    else:
#        generate_pin_message()
#        validate_pin_message()

elif mode == 0:
    build_video_directory(name)
elif mode == 1:
    build_category_folders(str(uri),name)
elif mode == 2:
    build_category_items(str(uri),name)
elif mode == 3:
    play_video(name)
elif mode == 4:
    build_bundles(name)
