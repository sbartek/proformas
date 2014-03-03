from django.contrib import admin
from calculo.models import Proveedor, Material, Cliente, Proforma, Partida, Contenedor, ContenedoresDeProforma, Montaje

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

admin.site.register(Proveedor,ProveedorAdmin)

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'proveedor', 'unidades', 'precioRef')

admin.site.register(Material, MaterialAdmin)

admin.site.register(Cliente)

class PartidaAdmin(admin.ModelAdmin):
    list_display = ('id', 'proforma', 'material')

admin.site.register(Partida, PartidaAdmin)

class PartidaInLine(admin.StackedInline):
    model = Partida
    extra = 1

class ContenedoresDeProformaInLine(admin.StackedInline):
    model = ContenedoresDeProforma
    extra = 1

class MontajeInLine(admin.StackedInline):
    model = Montaje

class ProformaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'incoterms', 'vendedor', 'paisDeVenta', 'pcoTotal', 'pvTotal')
    inlines = [PartidaInLine,  ContenedoresDeProformaInLine, MontajeInLine]
    list_filter = ['fecha']

admin.site.register(Proforma, ProformaAdmin)

admin.site.register(Contenedor)
admin.site.register(ContenedoresDeProforma)

