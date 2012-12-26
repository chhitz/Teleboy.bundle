####################################################################################################

VIDEO_PREFIX = "/video/teleboy"
VIDEO_URL_BASE = "http://www.teleboy.ch"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art-default.jpg'
ICON          = 'icon-default.png'

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('Title'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

def languagePrefs():
    lang = list()
    if Prefs['channels_de']:
        lang.append('de')
    if Prefs['channels_fr']:
        lang.append('fr')
    if Prefs['channels_it']:
        lang.append('it')
    if Prefs['channels_en']:
        lang.append('en')
    return lang

def getChannelDetails(lang):
    channels = dict()
    response = HTML.ElementFromURL(VIDEO_URL_BASE + "/programm/?program_date=live")
    #Log.Debug(HTML.StringFromElement(response))

    for channel in response.xpath('//tr[contains(@class, "playable")]'):
        Log.Debug(HTML.StringFromElement(channel))
        thumbElement = channel.find('td[@class="station"]/a')
        name = thumbElement.find('img').get('title')
        thumb = thumbElement.find('img').get('src')
        summary = '\n'.join(map(lambda x: x.text_content(), channel.xpath('td[@class="show"]/*')))

        stationId = int(thumb.split('/')[4])
        staticThumb = R("Logos/%d.png" % stationId)
        if staticThumb:
            thumb = staticThumb
        else:
            Log.Debug("No logo found for station %s (ID: %d)" % (name, stationId))
        channels[stationId] = (name, thumb, summary)
    return channels

def VideoMainMenu():
    dir = MediaContainer(viewGroup="InfoList", noCache=True)

    # Login
    response = HTTP.Request(VIDEO_URL_BASE + "/watchlist/")
    response = HTTP.Request(VIDEO_URL_BASE + "/layer/login_check", values={'login': Prefs['username'], 'password': Prefs['password'], 'x': 14, 'y': 7, 'keep_login': 1})
    
    myChannels = list()
    if Prefs['my_channels']:
        response = HTML.ElementFromURL(VIDEO_URL_BASE + "/programm/station/edit.php")
        for channel in response.xpath('//table[@id="mystations_table"]/tbody/tr'):
            position = int(channel.findtext('td[@class="station_pos"]'))
            stationId = int(channel.find('td/input').get('value'))
            myChannels.append(stationId)
        
        allChannels = getChannelDetails('all')
        for stationId in myChannels:
            try:
                dir.Append(WebVideoItem(VIDEO_URL_BASE + "/tv/player/player.php?stationId=%d" % stationId, title=allChannels[stationId][0], thumb=allChannels[stationId][1], summary=allChannels[stationId][2]))
            except:
                pass
    
    for lang in languagePrefs():
        for (stationId, (name, thumb, summary)) in getChannelDetails(lang).items():
            dir.Append(WebVideoItem(VIDEO_URL_BASE + "/tv/player/player.php?stationId=%d" % stationId, title=name, thumb=thumb, summary=summary))

    dir.Append(
        PrefsItem(
            title=L('Preferences'),
            summary=L('Set your login credentials'),
            thumb=R("icon-prefs.png")
        )
    )

    # ... and then return the container
    return dir
