import sys
import math
import kmltrack.template
import kmltrack.iterators
import kmltrack.template_strings

class DocumentKMLTemplate(kmltrack.template.Template):
    template = kmltrack.template_strings.document_kml_template
    icon = 'http://alerts.skytruth.org/markers/triangle-up.png'
    name = 'out'

    class track_kml(kmltrack.template.Template):
        template = kmltrack.template_strings.vessel_kml_template

        @staticmethod
        def rows(context):
            # Note: this method is called twice times!

            context['reader'] = context['input']()

            for row in context['reader']:
                if 'timestamp' not in row or 'lat' not in row or 'lon' not in row:
                    if context.get('verify-rows', False):
                        raise Exception("Missing column (lat, lon, timestamp): " + str(row))
                    continue
                mmsi = row.get('mmsi', '')
                if not row.get('name', ''):
                    row['name'] = mmsi
                row['marinetraffic_url'] = 'http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=%s'% mmsi
                row['itu_url'] = 'http://www.itu.int/cgi-bin/htsh/mars/ship_search.sh?sh_mmsi=%s' % mmsi

                ctx = dict(context)
                ctx.update(row)
                yield ctx

        class PlacemarkFolderTemplate(kmltrack.template.Template):
            template = kmltrack.template_strings.placemark_folder_template

            class PlacemarkTemplate(kmltrack.template.Template):
                template = kmltrack.template_strings.placemark_template
                ignore_missing = True

                @staticmethod
                def when(out_file, context):
                    out_file.write(context['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ'))

                @staticmethod
                def icon_color(out_file, context):
                    c = context.get('color', 0)

                    if isinstance(c, float):
                        def fudge(v):
                            a = 0.1
                            return v/2.0 - math.sqrt(4.0*a*a + v*v - 2.0*v + 1.0) / 2.0 + 1.0/2.0
                        c = (
                            255, # Alpha
                            fudge(c * 1.0) * 255, # Blue
                            fudge(c * 1.5) * 255, # Green
                            fudge(c * 3.0) * 255 # Red
                            )

                    if isinstance(c, tuple):
                        c = '%02x%02x%02x%02x' % c

                    out_file.write(c)

            def placemarks_kml(self, out_file, context):
                for row in context['rows']:
                    ctx = dict(context)
                    ctx.update(row)
                    self.PlacemarkTemplate(out_file, ctx)
                    if not hasattr(context['rows'], 'peek'):
                        return
                    next_date = context['rows'].peek['timestamp'].date()
                    if next_date != context['prev_date']:
                        return

        def placemarks_kml(self, out_file, context):
            context['rows'] = kmltrack.iterators.lookahead(self.rows(context))

            while hasattr(context['rows'], 'peek'):
                context['prev_date'] = context['rows'].peek['timestamp'].date()
                context['name'] = context['prev_date'].strftime('%Y-%m-%d')
                self.PlacemarkFolderTemplate(out_file, context)

        time_gap_styles = [
            {'range': (0, (3600 * 12)), 'style': 'trackStyle1'},
            {'range': ((3600 * 12), (3600 * 48)), 'style': 'trackStyle2'},
            {'range': ((3600 * 48), (3600 * 168)), 'style': 'trackStyle3'},
            {'range': ((3600 * 168), sys.maxint), 'style': 'trackStyle4'},
            ]

        def get_time_gap_style(self, dt, last_dt):
            td = (dt - last_dt).total_seconds()

            for s in self.time_gap_styles:
                if td >= s['range'][0] and td < s['range'][1]:
                    return s['style']

        def row_pairs(self, context):
            last = None
            for row in self.rows(context):
                if last is not None:
                    yield {
                        'src': last,
                        'dst': row,
                        'style': self.get_time_gap_style(row['timestamp'], last['timestamp'])
                        }
                last = row

        class TrackSegmentTemplate(kmltrack.template.Template):
            template = kmltrack.template_strings.track_template
            name = 'Vessel Track'

            @staticmethod
            def coords(out_file, context):
                first = True
                for row_pair in context['row_pairs']:
                    context['time_end'] = row_pair['dst']['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')

                    if first:
                        out_file.write('%(lon)s,%(lat)s,0 ' % row_pair['src'])
                        first = False
                    out_file.write('%(lon)s,%(lat)s,0 ' % row_pair['dst'])

                    if (not hasattr(context['row_pairs'], 'peek')
                        or context['row_pairs'].peek['style'] != row_pair['style']):
                        break

        def track_kml(self, out_file, context):
            context['row_pairs'] = kmltrack.iterators.lookahead(self.row_pairs(context))

            first = True
            while hasattr(context['row_pairs'], 'peek'):
                next_row_pair = context['row_pairs'].peek
                if first:
                    context['time_begin'] = next_row_pair['src']['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
                    first = False
                context['style'] = next_row_pair['style']

                self.TrackSegmentTemplate(out_file, context)
