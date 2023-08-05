# sumologic-export

Easily export your Sumologic log data.

![Box Sketch](https://github.com/rdegges/sumologic-export/raw/master/assets/box-sketch.jpg)


## Purpose

At [Stormpath](https://stormpath.com) we use
[Sumologic](http://www.sumologic.com) to store our server logs.

We were preparing to export our logs for safe keeping, so I wrote this tool.  It
uses the Sumologic API and downloads every log stored over a predefined time
period.

`sumologic-export` will grab every single Sumologic log you've ever written
and store it in gzipped JSON files.


## Installation

Installing `sumologic-export` is simple -- just use
[pip](http://www.pip-installer.org/en/latest/)!

Once you have pip installed on your computer, you can run the following to
install the latest release of `sumologic-export`:

```console
$ pip install -U sumologic-export
```

That's it :)


## Usage

Before you can export all your Sumologic data, you'll need to configure
`sumologic-export` and give it your Sumologic credentials.  To do this,
simply run:

```console
$ sumologic-export configure
```

On the command line.  This will prompt you for some basic information, then
store your credentials in the local file `~/.sumo`.

Next, to run a backup job, you can run:

```console
$ sumologic-export
```

This will export all your Sumologic data for the past month and dump it into a
new directory named `exports`.

If you'd like to specify a custom date range, you can do so by adding a start
and stop date of the form `YYYY-MM-DD`, for instance:

```console
$ sumologic-export 2014-01-01 2014-06-01
```

Or, if you'd like, you can just specify a start date, and the exporter will
export all logs from the start date till the current day.

```console
$ sumologic-export 2014-01-01
```

**NOTE**: Depending on how many logs you have, this process may take a while.

Once the process is finished, you'll have an `exports` directory populated with
gziped JSON files.  There will be one JSON file for each day, for instance:

```console
$ ls exports
2014-01-01.json.gz
2014-01-02.json.gz
```

For full usage information, run `sumologic-export -h`.


## Help

Need help?  Can't figure something out?  If you think you've found a bug, please
open an issue on the GitHub issue tracker.

Otherwise, [shoot me an email](mailto:r@rdegges.com)!


## Changelog

v0.0.2: 01-19-2015

    - Fixing off-by-one error in pagination logic. This was causing us to NOT
      download the last page of logs :(  Thanks
      [@sumoway](https://github.com/sumoway) for the report!

v0.0.1: 06-25-2014

    - First release!  Woo!
