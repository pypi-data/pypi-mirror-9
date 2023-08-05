#pypelogs

A generator-based tool for piping log data (and other sources) from inputs to outputs,
with any number of filters in between. Website: [https://github.com/gear11/pypelogs](https://github.com/gear11/pypelogs)

Pypelogs is modeled after the Unix shell: it's fed from an input file or STDIN, sends input through any number
of filters, then outputs to STDOUT or a specified sink. Internally, pypelogs is treating each input line
as an "event" (a Python dict object), similar to Logstash or other event processors that work on JSON objects.
Pypelogs can input and output data as either plain text or JSON.  Many other output options are possible
(e.g. output events as documents into a MongoDB instance).

Pypelogs makes extensive use of Python generators.  This benefits in a few ways:
* New directives are very easy to create.  Many are less that 20 lines of code.
* Event processing is very efficient.  Events are 'pulled' through the system, so that if the
output is blocked for any reason, then the tool simply stops reading in more data.

## Installation

Pypelogs can be installed via Pip:

    $ pip install pypelogs

## Usage

Pypelogs installs itself as `pl` (and as `pypelogs`).  The syntax is as follows:

    $ pl input [filter1 filter2 ... filterN] [output]

* The first argument is an input.  It tells pypelogs where and how to parse events from a source.
* After that, one or more filters are supplied.  Filters transform the input events.
* Optionally, an output is specified.  If the output is omitted, then pypelogs will output JSON to STDOUT.

## Example 1 - Basic text processing

Pypelogs can do stream processing similar to the Unix command line.
As a basic example, let's find all of the directories in my PC documents that contain a `.jpg` file.
This example could be accomplished with a perl one-liner; the point here is to demonstrate the
ability to compose pypelogs directives:

    $ find Documents -name '*.jpg' | pl text split:text,/,dir=[0:-1] groupby:dir bucket:0 keep:dir

The first part is just the Cygwin find, which will list all `*.jpg` files under the named path.  Here is
what pypelogs does:

1. `text` - Parse STDIN as text, creating a new event (Python dict) per line.  Each event has a single field
   called `text` which is the text of the line
1. `split:text,/,dir=[0:-1]` - Split the `text` field of each incoming event at the `/` character.  Join back
   the first through next-to-last elements and assign it to `dir`.  Each event now has a `dir` field indicating
   the parent directory of the file.
1. `groupby:dir` - Group incoming events by the value of the `dir` field (so that events with the same value
   of `dir` are condensed.  This will slurp in all incoming events and yield a single list as output containing
   the discovered dirs, and the number of events for each (the `count` field)
1. `bucket:0` - The `groupby` filter turned our event stream into a bucket (list of dict objects).  Convert
   it back to a stream of individual events.
1. `keep:dir` - Keep only the `dir` field of each event.  In this case, the original `text` field and the `count`
   field are stripped

The output looks something like the following:

    {"dir": "Documents/PC/OldPC/UVA Club/newsletter 02"}
    {"dir": "Documents/PC/HoldMail.jsp_files"}
    {"dir": "Documents/Personal/Kenneth Robert/Contributions_files"}
    ...

Oops, let's sort by directory name.  The command is the same, but with an extra filter on the end to sort:

    $ find Documents -name '*.jpg' | pl text split:text,/,dir=[0:-1] groupby:dir bucket:0 keep:dir sort:dir

Note the added filter to sort by the `dir` field.  Now output looks something like the following:

    {"dir": "Documents/Eve/Penguin Movie"}
    {"dir": "Documents/Gear11"}
    {"dir": "Documents/Mom Finances"}
    {"dir": "Documents/Mom Finances/Check scans"}
    {"dir": "Documents/PC"}
    {"dir": "Documents/PC/Baby Stuff"}
    ...

Maybe we want to feed this list into xargs to do some more processing.  Let's add an output filter to convert
the events to simple text strings:

    $ find Documents -name '*.jpg' | pl text split:text,/,dir=[0:-1] groupby:dir bucket:0 keep:dir sort:dir 'text:${dir}'

The `text` directive is an output directive that substitutes the event into the template after the colon (using
Python's string `Template` class).  Now the output is just unadorned text:

    Documents/Eve/Penguin Movie
    Documents/Gear11
    Documents/Mom Finances
    Documents/Mom Finances/Check scans
    Documents/PC
    Documents/PC/Baby Stuff
    ...

## Example 2 - Loading Geo-tagged Wikipedia articles into MongoDB

The event/text filtering becomes more interesting with non-text inputs and outputs.  Consider the following,
which extracts coordinate data from Wikipedia articles and then uploads the results to a MongoDB instance:

    $ bunzip2 -c 'C:\git\wp-download\data\en\20140203\enwiki-20140203-pages-articles.xml.bz2' | \
    pl wikig each:coords=loc head:n=5 mongodb:wikip.points

Here is what the pypelogs directives are doing:

1. `wikig` - Parses the standard dump of Wikipedia articles, searching for geographic coordinates.  The output is an event
   per geo-tagged Wikipedia article that includes the title, URL, and any coordinates discovered (as a list called `coords`).
1. `each:coords=loc` - Many Wikipedia articles specify multiple coords.  This directive 'denormalizes' incoming
   events, creating a new event per each item in the `coords` list.  The individual coordinate is copied into the `loc` field.
1. `head:n=5` - The file we are working with is huge.  The `head` directive works like the Unix `head` command,
   terminating the flow after 5 items.  It's useful for testing to make sure the command is working as expected.
1. `mongodb:wikip.points` - Insert the resulting documents into a MongoDB, using the database `wikip` and the
   collection `points`.  This output supports `host` and `port` options; it defaults to localhost and the default
   MongoDB port.

If we want to see what's going on, we can insert a `log` filter at any point in the process, to see what's
coming out:

    $ bunzip2 -c 'C:\git\wp-download\data\en\20140203\enwiki-20140203-pages-articles.xml.bz2' | \
    pl wikig log each:coords=loc log head:n=5 mongodb:wikip.points

This will log events after the `each` step.  Running this way yields:

    $  bunzip2 -c 'C:\git\wp-download\data\en\20140203\enwiki-20140203-pages-articles.xml.bz2' | \
      pl wikig each:coords=loc head:n=5 log mongodb:wikip.points
    2014-04-03 03:04:31,381 WARNING:MongoDB:2.6.3
    2014-04-03 03:04:31,385 WARNING:Connector:Connection: MongoClient('127.0.0.1', 27017)
    {'url': 'http://wikipedia.org/wiki/Algeria', 'source': 'wikipedia', 'loc': {'type': 'Point', 'coordinates': (2.0, 28.0)}, 'title': 'Algeria'}
    {'url': 'http://wikipedia.org/wiki/Atlantic_Ocean', 'source': 'wikipedia', 'loc': {'type': 'Point', 'coordinates': (-30.0, 0.0)}, 'title': 'Atlantic Ocean'}
    {'url': 'http://wikipedia.org/wiki/Aegean_Sea', 'source': 'wikipedia', 'loc': {'type': 'Point', 'coordinates': (22.95, 36.46666666666667)}, 'title': 'Aegean Sea'}
    {'url': 'http://wikipedia.org/wiki/Aegean_Sea', 'source': 'wikipedia', 'loc': {'type': 'Point', 'coordinates': (25.0, 39.0)}, 'title': 'Aegean Sea'}
    {'url': 'http://wikipedia.org/wiki/Apple_Inc.', 'source': 'wikipedia', 'loc': {'type': 'Point', 'coordinates': (-122.03118, 37.33182)}, 'title': 'Apple Inc.'}

