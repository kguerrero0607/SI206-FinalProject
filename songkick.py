import requests
import json
import sqlite3
from bs4 import BeautifulSoup
import secrets
import plotly.plotly as py
import plotly.graph_objs as go

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

################################################################################

class Concert:
    def __init__(self, venue, id):
        self.venue = venue
        self.id = id

    def __str__(self):
        return('{} {}'.format(self.venue, self.id))

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
        return ARTIST_CACHE_DICT[artist]

    else:
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

################################################################################

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

################################################################################

def total_concerts_bar_chart(artist_id):
    d18 = 0
    d17 = 0
    d16 = 0
    d15 = 0
    d14 = 0

    conn = sqlite3.connect('music.db')
    cur = conn.cursor()

    statement = '''
        SELECT [2018Dates], [2017Dates], [2016Dates], [2015Dates], [2014Dates]
        FROM Artists
        WHERE Id = ?
    '''
    params = (artist_id,)

    cur.execute(statement, params)

    for x in cur:
        d18 = x[0]
        d17 = x[1]
        d16 = x[2]
        d15 = x[3]
        d14 = x[4]


    data = [go.Bar(
            x=['2018', '2017', '2016', '2015', '2014'],
            y=[d18, d17, d16, d15, d14]
    )]

    layout = go.Layout(
    title='Total Concerts for Past 5 Years',
    )

    fig = go.Figure(data=data, layout=layout)

    py.plot(fig, filename='total_concerts_bar')

    conn.close()

################################################################################

def total_concerts_line_graph(artist_id):
    d18 = 0
    d17 = 0
    d16 = 0
    d15 = 0
    d14 = 0

    conn = sqlite3.connect('music.db')
    cur = conn.cursor()

    statement = '''
        SELECT [2018Dates], [2017Dates], [2016Dates], [2015Dates], [2014Dates]
        FROM Artists
        WHERE Id = ?
    '''
    params = (artist_id,)

    cur.execute(statement, params)

    for x in cur:
        d18 = x[0]
        d17 = x[1]
        d16 = x[2]
        d15 = x[3]
        d14 = x[4]

    data = [go.Scatter(
        x=['2018', '2017', '2016', '2015', '2014'],
        y=[d18, d17, d16, d15, d14]
    )]

    layout = go.Layout(
    title='Total Concerts for Past 5 Years',
    )

    fig = go.Figure(data=data, layout=layout)

    py.plot(fig, filename='total-concerts-line')

    conn.close()

################################################################################

def most_freq_venues_bar_chart(artist_id):
    conn = sqlite3.connect('music.db')
    cur = conn.cursor()

    xdata = []
    ydata = []

    statement = '''
        SELECT Venue, COUNT(Venue)
        From Concerts
        WHERE ArtistId = ?
        GROUP BY Venue
        ORDER BY COUNT(Venue) DESC
        LIMIT 5
    '''
    params = (artist_id,)

    cur.execute(statement, params)

    for x in cur:
        xdata.append(x[0])
        ydata.append(x[1])

    data = [go.Bar(
            x=xdata,
            y=ydata
    )]

    layout = go.Layout(
    title='5 Most Frequent Venues',
    )

    fig = go.Figure(data=data, layout=layout)

    py.plot(fig, filename='most-freq-venues-bar')

    conn.close()

################################################################################

def least_freq_venues_bar_chart(artist_id):
    conn = sqlite3.connect('music.db')
    cur = conn.cursor()

    xdata = []
    ydata = []

    statement = '''
        SELECT Venue, COUNT(Venue)
        From Concerts
        WHERE ArtistId = ?
        GROUP BY Venue
        ORDER BY COUNT(Venue) ASC
        LIMIT 5
    '''
    params = (artist_id,)

    cur.execute(statement, params)

    for x in cur:
        xdata.append(x[0])
        ydata.append(x[1])

    data = [go.Bar(
            x=xdata,
            y=ydata
    )]

    layout = go.Layout(
    title='5 Least Frequent Venues',
    )

    fig = go.Figure(data=data, layout=layout)

    py.plot(fig, filename='least-freq-venues-bar')

    conn.close()

################################################################################
# uncomment lines that are commented out to make fresh caches and db
def user_interaction():
    user_input = input('Type in a band/artist name or "exit" to quit:  ')
    while user_input != 'exit':
        # make_artist_request_using_cache(user_input)
        # make_concert_request_using_cache(user_input)
        artist_id = get_artist_id(user_input)
        user_command = input('Select a graph to be displayed or type "exit" to select a different artist:\n1. Bar chart of total concerts \n2. Line graph of total concerts \n3. Bar chart of most frequently played venues \n4. Bar chart of least frequently played venues\n')
        while user_command != 'exit':
            if user_command == '1':
                total_concerts_bar_chart(artist_id)
            elif user_command == '2':
                total_concerts_line_graph(artist_id)
            elif user_command == '3':
                most_freq_venues_bar_chart(artist_id)
            elif user_command == '4':
                least_freq_venues_bar_chart(artist_id)
            else:
                print('Bad input. Try again')

            user_command = input('Select a graph to be displayed or type "new" to select a different artist:\n1. Bar chart of total concerts \n2. Line graph of total concerts \n3. Bar chart of most frequently played venues \n4. Bar chart of least frequently played venues\n')
        user_input = input('Type in a band/artist name or "exit" to quit:  ')

    # create_artists()
    # create_concerts()
    # init_db()
    # insert_stuff()

# graph1: total concerts bar chart
# graph2: total concerts line graph
# graph3: 5 most frequent venues bar chart
# graph4: 5 least frequent venues bar chart

if __name__=="__main__":
    user_interaction()
