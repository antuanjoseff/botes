from django.contrib import admin
from .models import Kms, Botes, GPXPoint, GPXTrack, gpxFile
from django.db.models import Sum, Max
from django.db.models import Subquery
from django.contrib.gis import admin as gisadmin
from django.contrib.gis.forms.widgets import OSMWidget

class CustomBotesFilter(admin.SimpleListFilter):
    title = 'Per bota'
    parameter_name = 'kms_kms'

    def lookups(self, request, model_admin):
        qs = Botes.objects.all()
        qs = Botes.objects.annotate(total=Sum('kms__distancia'), last_date=Max('kms__date')).order_by("total").order_by("-last_date")
        l = list()
        for item in qs:
            l.append((item.id, item.bota + ' (' + str(int(item.total)) + 'kms)'))
        return (
            l
        )
    def queryset(self, request, queryset):
        if self.value() is None :
            return queryset
        return queryset.filter(bota__exact=self.value())


class CustomGeoWidget(OSMWidget):
    template_name = 'gis/admin/openlayers-cust.html'
    class Media:
        css = {
            "all": (
                "https://cdnjs.cloudflare.com/ajax/libs/ol3/4.6.5/ol.css",
                "gis/css/ol3.css",
            )
        }
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/ol3/4.6.5/ol.js",
            "static-2/gis/js/OLMapWidget.js",
        )    


class KmsAdmin(gisadmin.GISModelAdmin):
    list_filter = (CustomBotesFilter,)
    # gis_widget = CustomGeoWidget
    ordering = ('-date', 'distancia', 'ruta')
    list_display = ("ruta", "date", "distancia","gpx_file",)
    # readonly_fields = ["geom"]

    class Meta:
        widgets = {
            'geom': CustomGeoWidget
        }

    def get_readonly_fields(self, request, obj=None):
        return []
        # if obj.geom is None:
        #     return ["geom"]
        # else:
        #     return []
        # else:
        #     return super(TranslationAdmin, self).get_readonly_fields(request, obj)

    def get_ordering(self, request):
        return ['-date']

    exclude = ('botes',)


class BotesAdmin(admin.ModelAdmin):
    model = Botes
    list_display = ("bota", "date", "last_date", "total")
    ordering = ('-date',)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = Botes.objects.annotate(total=Sum('kms__distancia'), last_date=Max('kms__date'))
        return qs

    def total(self, obj):
        return obj.total


    def last_date(self, obj):
        return obj.last_date

    total.short_description = 'TOTAL (kms)'
    last_date.short_description = 'ÚLTIMA RUTA'

    total.admin_order_field = 'total'
    last_date.admin_order_field = 'last_date'

admin.site.register(Botes, BotesAdmin)
admin.site.register(Kms, KmsAdmin)

# admin.site.register(Kms, KmsAdmin)
# geoadmin.site.register(GPXPoint, geoadmin.OSMGeoAdmin)
# geoadmin.site.register(GPXTrack, geoadmin.OSMGeoAdmin)
