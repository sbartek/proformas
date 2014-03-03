from django.conf.urls import patterns, url

from calculo import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^lista/$', views.proformas, name='proformas'),
    url(r'^proforma_list/$', views.proformas, name='proforma_list'),
    url(r'^(?P<proforma_id>\d+)/$', views.detalles, name='detalles'),
    url(r'^nuevaProforma/$', views.nuevaProforma, name='nuevaProforma'),
    url(r'^(?P<proforma_id>\d+)/pendulo/$', views.pendulo, name='pendulo'),
    url(r'^partida/(?P<partida_id>\d+)/$', 
        views.detallesPartida, name='detallesPartida'),
    url(r'^(?P<proforma_id>\d+)/nuevaPartida/$', 
        views.nuevaPartida, name='nuevaPartida'),
    url(r'^(?P<proforma_id>\d+)/nuevaPartida/material/(?P<material_id>\d+)/$', 
        views.nuevaPartida, name='nuevaPartida'),
    url(r'^(?P<proforma_id>\d+)/nuevoContenedorDP/$', 
        views.nuevoContenedorDeProforma, name='nuevoContenedorDP'),
    url(r'^(?P<proforma_id>\d+)/nuevoContenedorDP/contenedor/(?P<contenedor_id>\d+)/$', 
        views.nuevoContenedorDeProforma, name='nuevoContenedorDP'),
    url(r'^(?P<proforma_id>\d+)/add_montaje/$', 
        views.add_montaje, name='add_montaje'),
    url(r'^(?P<proforma_id>\d+)/edit_montaje/$', 
        views.add_montaje, name='edit_montaje'),
    url(r'^editContenedorDP/(?P<contenedorDP_id>\d+)/$', 
        views.editContenedorDP, name='editContenedorDP'),
    #url(r'^cliente/list$', views.clientes_list, name='cliente_list'),
    url(r'^(?P<entrada_name>\w+)/edit/(?P<entrada_id>\d+)/$', 
        views.edit_entrada, name='edit_entrada'),
    url(r'^(?P<entrada_name>\w+)/edit/$', 
        views.edit_entrada, name='new_entrada'),
    url(r'^(?P<entrada_name>\w+)/remove/(?P<entrada_id>\d+)/$', 
        views.remove_entrada, name='remove_entrada'),
    url(r'^(?P<entrada_name>\w+)/list$', views.entrada_list, 
        name='entrada_list'),
)                     
