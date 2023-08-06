================================================
Pygmie Query Maker for Python 3.4 and PostgreSQL
================================================

This is a web interface with some nice tools that can greatly help if you are working with big complicated
queries with PostgreSQL. Some of the features include,

1. Tabbed interface for working with multiple queries at the same time.
2. Basic DB/Table structure information.
3. Query history using browsers Local Storage API, with bookmarks. Never lose another query half way into making.
3. User friendly interface for errors and logs without cluttering main UI
4. Integrated ACE Editor
5. Integrated Query Formatter.

NOTE: The result browser will limit the display of rows to around 100 unless there is a limit clause in the query.

Installation
============

You can install Pygmie via pip.

pip install pygmie

After installing start the server by using 'pygmie' command,
which should be in your path. You can use --ip and --port arguments
to specify the IP address and Port for the server.

Open the path to the webserver in browser. Enter the database credentials. Select the database from the dropdown.
Switch to queries tab. Start making queries!!

Dependencies
============

Flask
psycopg2
sqlparse (If you want the Query formatter)

Tested on Python 3.4

Have fun!

