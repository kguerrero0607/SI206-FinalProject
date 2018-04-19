import requests
import json
import sqlite3
from bs4 import BeautifulSoup
import secrets

class Artist:
    def __init__(self, artist_id, name, ontour, ontouruntil, uri, d18=None, d17=None, d16=None, d15=None, d14=None):
        self.artist_id = artist_id
        self.name = name
        self.ontour = ontour
        self.ontouruntil = ontouruntil
        self.uri = uri
        self.d18 = d18
        self.d17 = d17
        self.d16 = d16 
        self.d15 = d15
        self.d14 = d14

    def __str__(self):
        return('{} ({} - {}) | On tour: {} | On tour until: {}'.format(self.name, self.artist_id, self.uri, self.ontour, self.ontouruntil))
        # return('{} ({} - {}) | On tour: {} | On tour until: {} | 2018 concerts: {} | 2017 concerts: {} | 2016 concerts: {} | 2015 concerts: {} | 2014 concerts: {}'.format(self.name, self.artist_id, self.uri, self.ontour, self.ontouruntil, self.d18, self.d17, self.d16, self.d15, self.d14))

################################################################################

# search for specific artist in api to get songkick id, cache info
try:
    f = open('artist_cache.json', 'r')
    c = f.read()
    ARTIST_CACHE_DICT = json.loads(c)
    cache_file.close()
except:
    ARTIST_CACHE_DICT = {}


api_key = secrets.api_key
artist_url = 'http://api.songkick.com/api/3.0/search/artists.json'


def make_artist_request_using_cache(artist):
    if artist in ARTIST_CACHE_DICT:
        print('Getting data from cache...')
        return ARTIST_CACHE_DICT[artist]

    else:
        print('Requesting new data...')
        resp = get_artist(artist)
        ARTIST_CACHE_DICT[artist] = json.loads(resp.text)
        dumped_json_cache = json.dumps(ARTIST_CACHE_DICT)
        fw = open('artist_cache.json',"w")
        fw.write(dumped_json_cache)
        fw.close()
        return ARTIST_CACHE_DICT[artist]


def get_artist(artist):
    r = requests.get(artist_url, params = {
        'apikey': api_key,
        'query': artist
    })
    return r

################################################################################

# scrape artists page for concert data and add to cache
try:
    fref = open('concert_data.json', 'r')
    data = fref.read()
    CONCERT_CACHE_DICT = json.loads(data)
    fref.close()
except:
    CONCERT_CACHE_DICT = {}

def params_unique_combination(baseurl, artist_info):
    artist = artist_info[1].replace(' ', '-')
    return baseurl + artist_info[0] + '-' + artist

def make_concert_request_using_cache(artist):
    # use artist cache to get the artist's id
    baseurl = 'https://www.songkick.com/artists/'
    artist_id = get_artist_id(artist)
    artist_info = [str(artist_id), artist]
    unique_id = params_unique_combination(baseurl, artist_info)
    if unique_id in CONCERT_CACHE_DICT:
        return CONCERT_CACHE_DICT[unique_id]
    else:
        resp = requests.get(unique_id)
        CONCERT_CACHE_DICT[unique_id] = resp.text
        dumped_json_cache = json.dumps(CONCERT_CACHE_DICT)
        fref = open('concert_data.json',"w")
        fref.write(dumped_json_cache)
        fref.close()
        return CONCERT_CACHE_DICT[unique_id]

def get_artist_id(artist):
    artist_data = make_artist_request_using_cache(artist)
    artist_id = artist_data['resultsPage']['results']['artist'][0]['id']
    return artist_id

################################################################################

def init_db():
    conn = sqlite3.connect('music.db')
    cur = conn.cursor()

    # Drop tables
    statement = '''
        DROP TABLE IF EXISTS 'Artists';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Concerts';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Cities';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'ArtistRelations';
    '''
    cur.execute(statement)

    conn.commit()

    statement = '''
        CREATE TABLE 'Artists' (
            'Id' INTEGER PRIMARY KEY,
            'Name' TEXT NOT NULL,
            'onTour' TEXT,
            'onTourUntil' TEXT,
            'uri' TEXT NOT NULL,
            '2018Dates' INTEGER,
            '2017Dates' INTEGER,
            '2016Dates' INTEGER,
            '2015Dates' INTEGER,
            '2014Dates' INTEGER
        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Concerts' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'ArtistId' INTEGER,
            'Venue' TEXT,
            'City' TEXT,
            'State' TEXT,
            'Country' TEXT,
            'Date' TEXT
        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Cities' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'ArtistId' INTEGER,
            'City1' TEXT,
            'City1Count' INTEGER,
            'City2' TEXT,
            'City2Count' INTEGER,
            'City3' TEXT,
            'City3Count' INTEGER,
            'City4' TEXT,
            'City4Count' INTEGER,
            'City5' TEXT,
            'City5Count' INTEGER
        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'ArtistRelations' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'ArtistId' INTEGER,
            'Band1' TEXT,
            'Band1Count' INTEGER,
            'Band2' TEXT,
            'Band2Count' INTEGER,
            'Band3' TEXT,
            'Band3Count' INTEGER,
            'Band4' TEXT,
            'Band4Count' INTEGER,
            'Band5' TEXT,
            'Band5Count' INTEGER
        );
    '''
    cur.execute(statement)

    conn.commit()
    conn.close()

def create_artists():
    f = open('artist_cache.json', 'r')
    d = f.read()
    artists_data = json.loads(d)
    f.close()

    f2 = open('concert_data.json', 'r')
    d2 = f2.read()
    concert_data = json.loads(d2)
    f2.close()

    artist_list = []

    artist_id = 0
    display_name = ''
    on_tour = ''
    on_tour_until = ''
    uri = ''
    d18 = 0
    d17 = 0
    d16 = 0
    d15 = 0
    d14 = 0

    for x in artists_data:
        artist_info = artists_data[x]['resultsPage']['results']['artist'][0]
        artist_id = artist_info['id']
        display_name = artist_info['displayName']
        uri = artist_info['uri']
        if artist_info['onTourUntil'] == None:
            on_tour_until = 'Not on tour'
            on_tour = 'No'
        else:
            on_tour_until = artist_info['onTourUntil']
            on_tour = 'Yes'

        for y in concert_data:
            specific_artist_url = ''
            if x.replace(' ', '-') in y:
                specific_artist_url = y
            else:
                continue

            page_soup = BeautifulSoup(concert_data[specific_artist_url], 'html.parser')

            # see if artist is on tour or not
            # content_div = page_soup.find(class_="col-8 primary")
            # on_tour_data = content_div.find(class_='ontour')
            # if 'no' in on_tour_data.text:
            #     on_tour = 'No'
            # elif 'yes' in on_tour_data.text:
            #     on_tour = 'Yes'

            # get past num concerts for past 5 years
            try:
                tour_stats_div = page_soup.find(class_="component artist-touring-stats")
                tour_history = tour_stats_div.find(class_="touring-activity")
                tour_rows = tour_history.find_all('tr')
                for row in tour_rows:
                    if row.find('td').text.strip() == '2018':
                        d18 = int(row.find('td')['title'].split()[0])
                    elif row.find('td').text.strip() == '2017':
                        d17 = int(row.find('td')['title'].split()[0])
                    elif row.find('td').text.strip() == '2016':
                        d16 = int(row.find('td')['title'].split()[0])
                    elif row.find('td').text.strip() == '2015':
                        d15 = int(row.find('td')['title'].split()[0])
                    elif row.find('td').text.strip() == '2014':
                        d14 = int(row.find('td')['title'].split()[0])
            except:
                d18 = 0
                d17 = 0
                d16 = 0
                d15 = 0
                d14 = 0

            # create artist object
            artist_list.append(Artist(artist_id, display_name, on_tour, on_tour_until, uri, d18, d17, d16, d15, d14))
    return artist_list

def insert_stuff():
    conn = sqlite3.connect('music.db')
    cur = conn.cursor()

    artist_list = create_artists()

    for x in artist_list:
        params = (x.artist_id, x.name, x.ontour, x.ontouruntil, x.uri, x.d18, x.d17, x.d16, x.d15, x.d14)
        statement = '''
            INSERT INTO 'Artists'
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cur.execute(statement, params)

    conn.commit()
    conn.close()

def insert_from_artist():
    conn = sqlite3.connect('music.db')
    cur = conn.cursor()

    # reading artist cache
    f = open('artist_cache.json', 'r')
    d = f.read()
    artists_data = json.loads(d)
    f.close()

    for x in artists_data:
        artist_info = artists_data[x]['resultsPage']['results']['artist'][0]
        params = (artist_info['id'], artist_info['displayName'], artist_info['onTourUntil'], artist_info['uri'])

        statement = '''
            INSERT INTO 'Artists' (Id, Name, onTourUntil, uri)
            VALUES (?, ?, ?, ?)
        '''
        cur.execute(statement, params)
    conn.commit()
    conn.close()

def insert_from_concert():
    conn = sqlite3.connect('music.db')
    cur = conn.cursor()
    # reading concert cache
    f2 = open('concert_data.json', 'r')
    d2 = f2.read()
    concert_data = json.loads(d2)
    f2.close()

    # page_html = make_concert_request_using_cache(baseurl, artist_info)
    # page_soup = BeautifulSoup(page_html, 'html.parser')

    for x in concert_data:
        print(x)
        page_soup = BeautifulSoup(concert_data[x], 'html.parser')

        content_div = page_soup.find(class_="col-8 primary")
        on_tour = content_div.find(class_='ontour')
        d18 = 0
        d17 = 0
        d16 = 0
        d15 = 0
        d14 = 0
        try:
            tour_stats_div = page_soup.find(class_="component artist-touring-stats")
            tour_history = tour_stats_div.find(class_="touring-activity")
            tour_rows = tour_history.find_all('tr')
            for x in tour_rows:
                if x.find('td').text.strip() == '2018':
                    d18 = int(x.find('td')['title'].split()[0])
                elif x.find('td').text.strip() == '2017':
                    d17 = int(x.find('td')['title'].split()[0])
                elif x.find('td').text.strip() == '2016':
                    d16 = int(x.find('td')['title'].split()[0])
                elif x.find('td').text.strip() == '2015':
                    d15 = int(x.find('td')['title'].split()[0])
                elif x.find('td').text.strip() == '2014':
                    d14 = int(x.find('td')['title'].split()[0])
            print(str(d18))
            print(str(d17))
            print(str(d16))
            print(str(d15))
            print(str(d14))

        except:
            print(str(d18))
            print(str(d17))
            print(str(d16))
            print(str(d15))
            print(str(d14))


    # for x in countries_data:
    #     params = (None, x['alpha2Code'], x['alpha3Code'], x['name'], x['region'], x['subregion'], x['population'], x['area'])
    #
    #     statement = '''
    #         INSERT INTO 'Countries'
    #         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    #     '''
    #     cur.execute(statement, params)
    #
    # conn.commit()
    #
    # # reading CSV
    # with open(BARSCSV, encoding = 'utf-8') as csvDataFile:
    #     csvReader = csv.reader(csvDataFile)
    #
    #     for x in csvReader:
    #         params = (None, x[0], x[1], x[2], x[3], x[4][:-1], x[5], x[6], x[7], x[8], x[5])
    #
    #         statement = '''
    #             INSERT INTO Bars (Id, Company, SpecificBeanBarName, REF, ReviewDate, CocoaPercent, CompanyLocation, CompanyLocationId, Rating, BeanType, BroadBeanOrigin, BroadBeanOriginId)
    #             SELECT ?, ?, ?, ?, ?, ?, ?, Countries.Id, ?, ?, ?, Countries.Id
    #             FROM Countries
    #             WHERE Countries.EnglishName = ?
    #         '''
    #         cur.execute(statement, params)
    #
    #         statement = '''
    #             UPDATE Bars
    #             SET BroadBeanOriginId = (
    #                 SELECT Id
    #                 FROM Countries
    #                 WHERE Countries.EnglishName = ?
    #             )
    #             WHERE BroadBeanOrigin = ?
    #         '''
    #         params = (x[8], x[8])
    #         cur.execute(statement, params)
    #
    # conn.commit()
    # conn.close()


# user_input = input('gimmie a band boyo: ')
# while user_input != 'exit':
#     make_artist_request_using_cache(user_input)
#     (make_concert_request_using_cache(user_input))
#     user_input = input('gimmie a band boyo: ')
init_db()
insert_stuff()
