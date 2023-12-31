# -*- coding: utf-8 -*-
pip install apache-beam[interactive]

import apache_beam as beam
import re
import apache_beam.runners.interactive.interactive_beam as ib

p1 = beam.Pipeline()

class FormatElements(beam.DoFn):
  def process(self,record):
    year, producers = record
    raw_str_producers = re.sub(r'\s*, and | and \s*|, ', ',', producers)
    producers = raw_str_producers.split(',')

    rows = []

    if (len(producers) > 0):
      for idx, producer in enumerate(producers):
        rows.append(producer + "," + str(year))

    return rows

class CalculateYearsInterval(beam.DoFn):
  def process(self,record):
    key, value = record
    years = []

    for idx, year in enumerate(value):
      years.append(year[1])

    years.sort()

    followingWin = int(years[len(years) -1])
    previousWin = int(years[len(years) -2])
    interval = (followingWin - previousWin)

    row = key, previousWin, followingWin, interval

    return [row]

load_csv = (
    p1
      | "Import movie list" >> beam.io.ReadFromText("movielist.csv", skip_header_lines = 1)
      | "Split by comma" >> beam.Map(lambda record: record.split(';'))
      | "Filter by winners" >> beam.Filter(lambda record: record[4] == "yes")
      | "Map producers and year columns" >> beam.Map(lambda record: [record[0], record[3]])
      | "Format elements" >> beam.ParDo(FormatElements())
      | "Split Producer and Year by comma" >> beam.Map(lambda producers: producers.split(','))
      | "Group By producer's key" >> beam.GroupBy(lambda producer: producer[0])
      | "Filter Producers with more than 2 awards" >> beam.Filter(lambda record: len(record[1]) > 1)
      | "Calculate Years Interval" >> beam.ParDo(CalculateYearsInterval())
#      | "Write to Text" >> beam.io.WriteToText('results.txt')
      | "Print Results Year" >> beam.Map(print)
    )

p1.run()