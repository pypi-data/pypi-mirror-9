import kmltrack.generator
import os.path
import dateutil.parser
import csv
import json
try:
    import msgpack
except:
    pass

def column_mapper(rows, **mapping):
    "Usage: column_mapper(rows, dst_col1=src_col1, dst_col2=src_col2, ...)"
    env = {
        "d": dateutil.parser.parse
        }
    for row in rows:
        renv = dict(row)
        renv.update(env)
        renv['row'] = row
        for key, expr in mapping.iteritems():
            try:
                row[key] = eval(expr, renv)
            except:
                pass
        yield row

def file_to_kml(infile_name, outfile_name, reader, **kw):
    column_map = {
        'timestamp': 'd(timestamp)',
        'lat': 'float(lat)',
        'lon': 'float(lon)',
        'color': 'float(color)',
        'course': 'float(course)'
        }
    column_map.update(kw.get('column_map', {}))

    def input():
        with sys.stdin if infile_name is None or '-' == infile_name else open(infile_name, 'rb') as in_file:
            for row in column_mapper(reader(in_file), **column_map):
                yield row

    with sys.stdout if outfile_name is None or '-' == outfile_name else open(outfile_name, 'w') as kml_file:
        kw['input'] = input
        kw["name"] = os.path.splitext(outfile_name)[0]
        kmltrack.generator.DocumentKMLTemplate(kml_file, kw)


def csv_to_kml(infile_name, outfile_name, **kw):
     file_to_kml(infile_name, outfile_name, cvs.DictReader, **kw)

def json_to_kml(infile_name, outfile_name, **kw):
    def reader(file):
        for row in file:
            yield json.loads(row)
    file_to_kml(infile_name, outfile_name, reader, **kw)

def msgpack_to_kml(infile_name, outfile_name, **kw):
    file_to_kml(infile_name, outfile_name, msgpack.Unpacker, **kw)
