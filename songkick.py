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

class Concert:
    def __init__(self, venue, id):
        self.venue = venue
        self.id = id

    def __str__(self):
        return('{} {}'.format(self.venue, self.id))

################################################################################

class Cities:
    def __init__(self, artist_id, c1, c1num, c2, c2num, c3, c3num, c4, c4num, c5, c5num):
        self.artist_id = artist_id
        self.c1 = c1
        self.c1num = c1num
        self.c2 = c2
        self.c2num = c2num
        self.c3 = c3
        self.c3num = c3num
        self.c4 = c4
        self.c4num = c4num
        self.c5 = c5num

    def __str__(self):
        return '{} - {} ({}), {} ({}), {} ({}), {} ({}), {} ({}),'.format(self.artist_id, self.c1, self.c1num, self.c2, self.c2num, self.c3, self.c3num, self.c4, self.c4num, self.c5, self.c5num)

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

try:
    fref = open('past_gigs.json', 'r')
    data = fref.read()
    GIG_CACHE_DICT = json.loads(data)
    fref.close()
except:
    GIG_CACHE_DICT = {}

def make_past_gig_request_using_cache(url):
    if url in GIG_CACHE_DICT:
        return GIG_CACHE_DICT[url]
    else:
        resp = requests.get(url)
        GIG_CACHE_DICT[url] = resp.text
        dumped_json_cache = json.dumps(GIG_CACHE_DICT)
        fref = open('past_gigs.json',"w")
        fref.write(dumped_json_cache)
        fref.close()
        return GIG_CACHE_DICT[url]

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
            'Venue' TEXT
        );
    '''
    # 'City' TEXT,
    # 'State' TEXT,
    # 'Country' TEXT,
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

def create_concerts():
    f2 = open('concert_data.json', 'r')
    d2 = f2.read()
    concert_data = json.loads(d2)
    f2.close()

    concert_list = []


    location = ''
    id = 0
    for x in concert_data:
        all_gigs_url = x + '/gigography'
        page_html = make_past_gig_request_using_cache(all_gigs_url)
        page_soup = BeautifulSoup(page_html, 'html.parser')

        artist_name_div = page_soup.find(class_="component brief")
        artist_name = artist_name_div.find('a').text
        id = get_artist_id(artist_name)

        past_gigs_div = page_soup.find(class_="component events-summary", id='event-listings')
        past_gigs = past_gigs_div.find_all(class_="event-listings ")
        for gig in past_gigs:

            location_info = gig.find_all(class_="location")
            for l in location_info:
                location_list = l.find_all('span')
                if ',' in location_list[0].text.strip():
                    location = 'No venue'
                else:
                    location = location_list[0].text.strip()
                concert_list.append(Concert(location, id))
    return concert_list

def create_cities():
    f = open('artist_cache.json', 'r')
    d = f.read()
    artists_data = json.loads(d)
    f.close()

    f2 = open('concert_data.json', 'r')
    d2 = f2.read()
    concert_data = json.loads(d2)
    f2.close()

    cities_list = []
    artist_id = 0
    c1 = ''
    c1num = 0
    c2 = ''
    c2num = 0
    c3 = ''
    c3num = 0
    c4 = ''
    c4num = 0
    c5 = ''
    c5num = 0

    for x in artists_data:
        print(x)
        artist_info = artists_data[x]['resultsPage']['results']['artist'][0]
        artist_id = artist_info['id']

        for y in concert_data:
            print(y)
            specific_artist_url = ''
            if x.replace(' ', '-') in y:
                specific_artist_url = y
            else:
                continue

            page_soup = BeautifulSoup(concert_data[specific_artist_url], 'html.parser')
            content_div = page_soup.find(class_="component artist-touring-stats")
            most_played_div = content_div.find_all(class_="stat")
            # most_played_div_closer = most_played_div.find()
            for z in most_played_div:
                if 'Most played' in z.find('p').text:
                    closer_look = z.find(class_="info")
                    cities = closer_look.find_all('li')
                    for c in cities:
                        info = c.text.strip().split('\n')
                        cities_list.append({artist_id: {info[0]: int(info[1][2:(len(info[1])-1)])}})
            print(cities_list)
        # most_played = most_played_div.find_all('li')
        # print(most_played_div)

################################################################################

def insert_stuff():
    conn = sqlite3.connect('music.db')
    cur = conn.cursor()

    artist_list = create_artists()
    concert_list = create_concerts()

    for x in artist_list:
        params = (x.artist_id, x.name, x.ontour, x.ontouruntil, x.uri, x.d18, x.d17, x.d16, x.d15, x.d14)
        statement = '''
            INSERT INTO 'Artists'
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cur.execute(statement, params)

    for x in concert_list:
        params = (None, x.id, x.venue)
        statement = '''
            INSERT INTO 'Concerts'
            VALUES(?, ?, ?)
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

    date = ''
    location = ''
    for x in concert_data:
        print(x)
        all_gigs_url = x + '/gigography'
        page_html = make_past_gig_request_using_cache(all_gigs_url)
        page_soup = BeautifulSoup(page_html, 'html.parser')

        past_gigs_div = page_soup.find(class_="component events-summary", id='event-listings')
        past_gigs = past_gigs_div.find_all(class_="event-listings ")
        for gig in past_gigs:
            dates = gig.find_all(class_="with-date")
            for y in dates:
                date = y.text.strip()
            location_info = gig.find_all(class_="location")
            for l in location_info:
                location_list = l.find_all('span')
                if ',' in location_list[0].text.strip():
                    location = 'No venue'
                else:
                    location = location_list[0].text.strip()
                print(location)
        # all_gigs_url = past_gigs_div.find('a')['href']

        # print(past_gigs)


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


user_input = input('gimmie a band boyo: ')
while user_input != 'exit':
    make_artist_request_using_cache(user_input)
    (make_concert_request_using_cache(user_input))
    user_input = input('gimmie a band boyo: ')
create_artists()
create_concerts()
init_db()
insert_stuff()
# for x in create_concerts():
#     print(x)
