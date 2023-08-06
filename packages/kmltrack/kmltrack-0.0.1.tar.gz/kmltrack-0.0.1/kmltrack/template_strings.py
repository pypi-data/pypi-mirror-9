# ============================================================================ #
#   KML Document templates
# ============================================================================ #

document_kml_template = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
    <name>$name</name>
    <StyleMap id="vesselStyleMap">
        <Pair>
            <key>normal</key>
            <styleUrl>#normVesselStyle</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#hlightVesselStyle</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="hlightVesselStyle">
        <IconStyle>
            <scale>1.2</scale>  
            <color>ff006666</color>
            <Icon>
                <href>$icon</href>
            </Icon>
            <hotSpot x="16" y="3" xunits="pixels" yunits="pixels"/>
        </IconStyle>
        <LabelStyle><color>ff999999</color><scale>0.8</scale></LabelStyle>
    </Style>
    <Style id="normVesselStyle">
        <IconStyle>
          <color>ff009999</color>
          <Icon><href>$icon</href></Icon>
          <hotSpot x="16" y="3" xunits="pixels" yunits="pixels"/>
        </IconStyle>
        <LabelStyle><scale>0</scale></LabelStyle>
    </Style>
    <StyleMap id="trackStyle1">
        <Pair>
            <key>normal</key>
            <styleUrl>#normTrackStyle1</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#hlightTrackStyle1</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="hlightTrackStyle1">
        <LineStyle>
            <color>ff999999</color>
            <width>2</width>
        </LineStyle>
    </Style>
    <Style id="normTrackStyle1">
        <LineStyle>
            <color>ff999999</color>
            <width>1.2</width>
        </LineStyle>
    </Style>    
    <StyleMap id="trackStyle2">
        <Pair>
            <key>normal</key>
            <styleUrl>#normTrackStyle2</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#hlightTrackStyle2</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="hlightTrackStyle2">
        <LineStyle>
            <color>ff00ffff</color>
            <width>6</width>
        </LineStyle>
    </Style>
    <Style id="normTrackStyle2">
        <LineStyle>
            <color>ff00ffff</color>
            <width>4</width>
        </LineStyle>
    </Style>    
    <StyleMap id="trackStyle3">
        <Pair>
            <key>normal</key>
            <styleUrl>#normTrackStyle3</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#hlightTrackStyle3</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="hlightTrackStyle3">
        <LineStyle>
            <color>ff0000ff</color>
            <width>6</width>
        </LineStyle>
    </Style>
    <Style id="normTrackStyle3">
        <LineStyle>
            <color>ff0000ff</color>
            <width>4</width>
        </LineStyle>
    </Style>        
    <StyleMap id="trackStyle4">
        <Pair>
            <key>normal</key>
            <styleUrl>#normTrackStyle4</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#hlightTrackStyle4</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="hlightTrackStyle4">
        <LineStyle>
            <color>00000000</color>
            <width>6</width>
        </LineStyle>
    </Style>
    <Style id="normTrackStyle4">
        <LineStyle>
            <color>00000000</color>
            <width>4</width>
        </LineStyle>
    </Style>
    $track_kml
</Document>
</kml>
"""


# ============================================================================ #
#   Vessel template
# ============================================================================ #

vessel_kml_template = """
<Folder>
    <name>Vessel Tracks</name>
    $track_kml
</Folder>

<Folder>
    <name>AIS Points</name>
    $placemarks_kml
</Folder>
"""


# ============================================================================ #
#   Track template
# ============================================================================ #

track_template = """    <Placemark>
    <name>$name</name>
    <styleUrl>#$style</styleUrl>
    <LineString>
        <tessellate>1</tessellate>
        <coordinates>
            $coords
        </coordinates>
    </LineString>
    <TimeSpan><begin>$time_begin</begin><end>$time_end</end></TimeSpan>
     
</Placemark>"""


# ============================================================================ #
#   Placemark folder template
# ============================================================================ #

placemark_folder_template = """<Folder>
    <name>$name</name>
$placemarks_kml
</Folder>
"""


# ============================================================================ #
#   Placemark template
# ============================================================================ #

placemark_template = """<Placemark>
    <name>$timestamp</name>
    <description>
<table width="300">
    <tr><th align="right">Vessel Name</th><td>$name</td></tr>
    <tr><th align="right">Vessel Type</th><td>$shiptype</td></tr>
    <tr><th align="right">MMSI</th><td>$mmsi</td></tr>
    <tr><th align="right">Length</th><td>$to_bow</td></tr>
    <tr><th align="right">Datetime</th><td>$timestamp</td></tr>
    <tr><th align="right">True Heading</th><td>$heading</td></tr>
    <tr><th align="right">Speed Over Ground</th><td>$speed</td></tr>
    <tr><th align="right">Course Over Ground</th><td>$course</td></tr>
    <tr><th align="right">Latitude</th><td>$lat</td></tr>
    <tr><th align="right">Longitude</th><td>$lon</td></tr>
    <tr><th align="right">Vessel Info</th><td><a href="$marinetraffic_url">marinetraffic.com</a> <a href="$itu_url">ITU</a></td></tr>
</table>    
    </description>    
    <styleUrl>#vesselStyleMap</styleUrl>
    <TimeStamp><when>$when</when></TimeStamp>
    <Point>
        <coordinates>$lon,$lat,0</coordinates>
    </Point>
    <Style><IconStyle><heading>$course</heading><color>$icon_color</color></IconStyle></Style>
</Placemark>"""
