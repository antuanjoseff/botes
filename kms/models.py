# from django.db import models
from django.contrib.auth.models import User
import datetime
from django.db.models import Sum

from django.contrib.gis.db import models
from django.contrib import admin
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.geos import Point, LineString, MultiLineString
import gpxpy
import gpxpy.gpx
from django.contrib.gis.geos import GEOSGeometry, WKTWriter

# from django.conf import settings

def GPX_Folder(instance, filename):
    return "uploaded_gpx_files/%s" % (filename)

class gpxFile(models.Model):
    title = models.CharField("Title", max_length=100)
    gpx_file = models.FileField(upload_to=GPX_Folder, blank=True)

    def __unicode__(self):
        return self.title

class GPXPoint(models.Model):
    name = models.CharField("Name", max_length=50, blank=True)
    description = models.CharField("Description", max_length=250, blank=True)
    gpx_file = models.ForeignKey(gpxFile, on_delete=models.CASCADE)
    point = models.PointField()
    objects = models.Manager()

    def __unicode__(self):
        return unicode(self.name)

class GPXTrack(models.Model):
    track = models.MultiLineStringField(dim=4)
    gpx_file = models.ForeignKey(gpxFile, on_delete=models.CASCADE)
    objects = models.Manager()

class Botes(models.Model):
    id = models.AutoField(primary_key=True)
    bota = models.CharField(max_length=50, null=False, blank=False)
    date = models.DateField(default=None, null=True, verbose_name='Data compra')

    def __str__(self):
        u"""bota."""
        return "%s" % (self.bota)

class Kms(models.Model):
    """Llistat d'excursions."""

    def get_default_botes():
        return Botes.objects.all().order_by('-id')[:1]

    BOTES = [
        ('Salomon negres (no gorotex)', 'Salomon negres (no gorotex)'),
        ('Salomon vermelles', 'Salomon vermelles'),
        ('Salomon verdes', 'Salomon verdes'),
        ('Salewa', 'Salewa'),
        ('Salomon no cordills', 'Salomon no cordills'),
    ]

    id = models.AutoField(primary_key=True)

    date = models.DateField(default=datetime.date.today)
    ruta = models.TextField(default='',max_length=255, null=False, blank=False)
    distancia = models.FloatField(null=False, blank=False, verbose_name="Distancia (kms)")
    botes = models.CharField(choices=BOTES, max_length=50,
                             default='Salomon negres (no gorotex)', null=False, blank=False)
    bota = models.ForeignKey(Botes, null=True, default=get_default_botes, on_delete=models.CASCADE)
    comentari = models.CharField(default='', null=True, blank=True, max_length=255)

    gpx_file = models.FileField(upload_to=GPX_Folder, default=None, null=True, blank=True)
    geom = models.MultiLineStringField(default=None, null=True, dim=2, blank=True)
    # times = ArrayField(
    #             models.DateField(null=True, default=None),
    #             default='', null=True
    #         )
    # elevations = ArrayField(
    #             models.FloatField(null=True, default=None),
    #             default='', null=True
    #         )

    # @classmethod
    # def from_db(cls, db, field_names, values):
    #     instance = cls(*values)
    #     instance._state.adding = False
    #     instance._state.db = db

    #     if instance.geom is not None:
    #         wkt_w = WKTWriter()
    #         wkt_w.outdim = 2 # This sets the writer to output 2D WKT

    #         polygon = GEOSGeometry(instance.geom)
    #         temp = wkt_w.write(polygon)
    #         polygon = GEOSGeometry(temp) # The 3D geometry
    #         instance.geom = polygon
    #     return instance

    def save(self, *args, **kwargs):
        # self.elevations = None
        # self.times = None
        self.geom = None
        super(Kms, self).save(*args, **kwargs)
        if self.gpx_file.name is not None:
            gpx_file = open('/home/toni/git/botes/' + str(self.gpx_file.name.replace(" ", "_")))
            gpx = gpxpy.parse(gpx_file)

            if gpx.tracks:
                for track in gpx.tracks:
                    for segment in track.segments:
                        track_list_of_points = []
                        ar_elevations = []
                        ar_times = []
                        for point in segment.points:
                            point_in_segment = Point(point.longitude, point.latitude)
                            point_zm = Point(point.longitude, point.latitude)
                            track_list_of_points.append(point_in_segment.coords)
                            ar_elevations.append(point.elevation)
                            ar_times.append(point.time)
                        new_track_segment = LineString(track_list_of_points)

                    self.geom = MultiLineString(new_track_segment)
                    # self.elevations = ar_elevations
                    # self.times = ar_times
                    #print(self.geom)
        super(Kms, self).save(*args, **kwargs)

    def __str__(self):
        u"""Llista una ruta."""
        return "%s (%s)" % (self.ruta, self.date)

    def colored_is_long(self):
        if self.distancia >= 30:
            cell_html = '<span style="color: red;">%s</span>'
        else:
            cell_html = '<span>%s</span>'
        # for below line, you may consider using 'format_html', instead of python's string formatting
        return cell_html % self.distancia

    colored_is_long.allow_tags = True
