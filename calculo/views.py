#This Python file uses the following encoding: utf-8

import re
from decimal import *

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse

from constantes import *
from .models import Proforma, Partida, Material, Contenedor, ContenedoresDeProforma, Montaje, Cliente, Proveedor
from .forms import ProformaForm, PartidaForm, ContenedoresDeProformaForm, MontajeForm, ClienteForm, ProveedorForm, MaterialForm 

def index(request):
    context = {}
    return render(request, 'calculo/html/index.html', context)

def proformas(request):
    proforma_list = Proforma.objects.all().order_by('-fecha')
    context = {'proforma_list': proforma_list}
    return render(request, 'calculo/html/proforma_list.html', context)

def detalles(request, proforma_id):
    proforma = get_object_or_404(Proforma, pk=proforma_id)
    if request.method == 'POST':
        form = ProformaForm(request.POST,instance=proforma)
        if form.is_valid():
            newProforma = form.save()
            return redirect(reverse('calculo:detalles', args=(newProforma.id,)))
    else:
        form = ProformaForm(instance=proforma)
        
    return render(request, 'calculo/html/detalles.html', {
        'proforma': proforma,
        'form': form,
        'materials':Material.objects.order_by('nombre'),
        'contenedores':Contenedor.objects.all(),
        'costes':proforma.costes(),
        'comisiones':proforma.comisiones(),
    })

def detallesPartida(request, partida_id):
    partida = get_object_or_404(Partida, pk=partida_id)
    if request.method == 'POST':
        form = PartidaForm(request.POST,instance=partida)
        if form.is_valid():
            renewPartida = form.save()
            return redirect(reverse('calculo:detalles', args=(renewPartida.proforma.id,)))
    else:
        form = PartidaForm(instance=partida)
        
    return render(request, 'calculo/detallesPartida.html', {
        'partida': partida,
        'form': form,
    })

def nuevaProforma(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ProformaForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            renewProforma = form.save()
            # Process the data in form.cleaned_data
            # ...
            return redirect(reverse('calculo:detalles', args=(renewProforma.id,))) # Redirect after POST
    else:
        form = ProformaForm() # An unbound form

    return render(request, 'calculo/html/nuevaProforma.html', {
        'form': form,
    })

def nuevaPartida(request, proforma_id, material_id=None):
    proforma = get_object_or_404(Proforma, pk=proforma_id)
    if request.method == 'POST': # If the form has been submitted...
        form = PartidaForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            renewPartida = form.save(commit=False)
            renewPartida.proforma = proforma
            #renewPartida.pco_manipulado = renewPartida.pcoUnitario 
            renewPartida.save()
            # Process the data in form.cleaned_data
            # ...

            # Redirect after POST
            return redirect(reverse('calculo:detalles', 
                                    args=(renewPartida.proforma.id,))) 
    elif material_id:
        material = get_object_or_404(Material, pk=material_id)
        newPartida = Partida(material = material, cantidad = 1, 
                             pcoUnitario = material.precioRef,
                             pco_manipulado = material.precioRef,)
        form = PartidaForm(instance = newPartida) 
    else:
        form = PartidaForm() # An unbound form

    return render(request, 'calculo/nuevaPartida.html', {
        'proforma': proforma,
        'form': form,
    })

def editContenedorDP(request, contenedorDP_id):
    contenedorDP = get_object_or_404(ContenedoresDeProforma, pk=contenedorDP_id)
    proforma = get_object_or_404(Proforma, pk=contenedorDP.proforma.id)
    if request.method == 'POST': 
        form = ContenedoresDeProformaForm(request.POST) 
        if form.is_valid(): # All validation rules pass
            renewContenedorDP = form.save(commit=False)
            return redirect(reverse('calculo:detalles', 
                                    args=(proforma_id,))) 
    else:
        form = ContenedoresDeProformaForm(instance = contenedorDP) 
        
    return render(request, 'calculo/editContenedorDP.html', {
        'contenedorDP': contenedorDP,
        'form': form,
    })


def nuevoContenedorDeProforma(request, proforma_id, contenedor_id=None):
    proforma = get_object_or_404(Proforma, pk=proforma_id)
    if request.method == 'POST': 
        form = ContenedoresDeProformaForm(request.POST) 
        if form.is_valid(): # All validation rules pass
            newContenedorDP = form.save(commit=False)
            newContenedorDP.proforma = proforma
            newContenedorDP.save()
            return redirect(reverse('calculo:detalles', 
                                    args=(proforma_id,))) 
    elif contenedor_id:
        contenedor = get_object_or_404(Contenedor, pk=contenedor_id)
        newContenedorDP = ContenedoresDeProforma(
            proforma=proforma,
            contenedor = contenedor, cantidad = 1, 
            precio = contenedor.precio, 
            precioFlete = contenedor.precioFlete,
            transporteMontaje = contenedor.transporteMontaje,
        )
        form = ContenedoresDeProformaForm(instance = newContenedorDP) 
    else:
        form = ContenedoresDeProformaForm() # An unbound form

    return render(request, 'calculo/nuevoContenedorDP.html', {
        'proforma': proforma,
        'form': form,
    })


def add_montaje(request, proforma_id):
    proforma = get_object_or_404(Proforma, pk=proforma_id)
    if proforma.con_montaje():
        form = MontajeForm(instance = proforma.montaje) 
    elif request.method == 'POST': 
        form = MontajeForm(request.POST) 
        if form.is_valid(): # All validation rules pass
            montaje = form.save(commit=False)
            montaje.proforma = proforma
            montaje.save()
            # Redirect after POST
            return redirect(reverse('calculo:detalles', 
                                    args=(montaje.proforma.id,))) 
    else:
        montaje = Montaje(
            proforma = proforma,
            transporte_local = proforma.transporte_contenedores_local(),
            comercial2 = proforma.comercial2,
            comercial3 = proforma.comercial3,)
        form = MontajeForm(instance = montaje) 

    return render(request, 'calculo/add_montaje.html', {
        'proforma': proforma,
        'form': form,
    })

def comadot2Dec(un):
    ns= re.split(r'[.,]',un)
    if len(ns)==0:
        n = 0
    elif len(ns) == 1:
        n = ns[0]
    else:
        n = ns[0]+"."+ns[1]
    return Decimal(n)

def pendulo(request, proforma_id):
    """Modificar los precios"""
    #todo:
    #change names en forma de "1" a por ejempo "precio1" 
    proforma = get_object_or_404(Proforma, pk=proforma_id)
    mensaje = ""
    if request.method == 'POST':
        pids=[p for p in request.POST.getlist('penpart')]
        if len(pids)==0 or len(pids)==len(proforma.partida_set.all()):
            mensaje = "Elije algo, pero no todo!!!"
        else:
            mps = {get_object_or_404(Partida, pk=int(pid)):
                   comadot2Dec(request.POST[pid]) for pid in pids}
            preciomps = sum([mps[p] for p in mps])
            nomps = [p for p in proforma.partida_set.all() if p not in mps]
            precionomps = sum([p.pvTotal() for p in nomps])
            if precionomps == 0:
                mensaje = "Error, precios no elejedos no pueden ser cero."
            else:
                kp = (proforma.pvTotal() - preciomps)/precionomps
                for p in nomps:
                    p.save_pco_manipulado(kp*p.pco(moneda=USD))
                for p in mps:
                    p.save_pv_manipulado(mps[p], moneda = USD,
                                         cantidad = p.cantidad)
                return redirect(reverse('calculo:detalles', 
                                args=(proforma.id,))) 
    else:
        pass
    return render(request, 'calculo/pendulo.html', 
                  {'proforma': proforma, 'mensaje':mensaje})

def materials_list(request):
    context = {'materials': Material.objects.order_by('nombre')}
    return render(request, 'calculo/html/materials_list.html', context)

def clientes_list(request):
    context = {'clientes': Cliente.objects.order_by('nombre')}
    return render(request, 'calculo/html/clientes_list.html', context)

def proveedores_list(request):
    context = {'proveedores': Proveedor.objects.order_by('nombre')}
    return render(request, 'calculo/html/proveedores_list.html', context)

def edit_entrada(request, entrada_name, entrada_id = None):
    if entrada_name == 'cliente':
        EntradaForm = ClienteForm
        Entrada = Cliente
    else:
        return HttpResponseNotFound('<h1>Entrada Error</h1>')
    if request.method == 'POST':
        if entrada_id:
            entrada = get_object_or_404(Entrada, pk=int(entrada_id))
            form = EntradaForm(request.POST,instance = entrada)
            if form.is_valid(): # All validation rules pass
                entrada = form.save()
        else:
            form = EntradaForm(request.POST) 
            if form.is_valid(): # All validation rules pass
                entrada = form.save()
            # Redirect after POST
        return redirect(reverse('calculo:'+entrada_name+'_list'))
    else:
        if entrada_id:
            entrada = get_object_or_404(Entrada, pk=int(entrada_id))
            form = EntradaForm(instance = entrada)
            context = {'form': form, entrada_name: entrada}
        else:
            form = EntradaForm() 
            context = {'form': form}
        return render(request, 'calculo/html/edit_'+entrada_name+'.html', context)

def remove_entrada(request, entrada_name, entrada_id):
    if entrada_name == 'cliente':
        Entrada = Cliente
    elif entrada_name == 'proforma':
        Entrada = Proforma
    else:
        return HttpResponseNotFound('<h1>Entrada Error</h1>')
    entrada = get_object_or_404(Entrada, pk=int(entrada_id))
    entrada.delete()
    return redirect(reverse('calculo:'+entrada_name+'_list'))

def edit_material(request, material_id = None):
    pass


