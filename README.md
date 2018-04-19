# SI206-FinalProject
Data Sources:
    - SongKick API
        - need API key (obtained through online form request to SongKick). key is imported in program from secrets.py file
    - scraping and crawling www.songkick.com
Additional Site:
    - must create account for plot.ly and retrieve API key to put in plotly credentials file

Two classes are created at the top of this code. They are used to help store data about artists and concerts.
Requests are then made to the API for artist data and the results are cached. The same occurs for
concert data, except this is getting the html for pages rather than using the API. Following this are functions
to create objects within the Artist and Concert classes. The data obtained is then inserted into the database.
An interactive prompt allows the user to pick a certain graph to create for a particular artist
and that graph is then displayed using the information from the database and giving it to plotly.

Once the program has started, all a user must do is type in a band or artist name. They are then given
four options for graphs to be displayed. The user should pick a number 1-4 to be shown the corresponding
graph. The user can then choose to look at more graphs for the same artist, or type "exit" to go back
and enter the name of a different artist. To end the program, the user must type 'exit' from the
artist selection screen.
