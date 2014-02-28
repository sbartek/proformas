#This Python file uses the following encoding: utf-8

###TO DO
#test: proforma sin items DIVISION POR CERO!

from calculo.models import Proveedor, Material, Cliente, Proforma, Partida, Contenedor, ContenedoresDeProforma
import datetime, csv, re
from decimal import *

def dot2Dec(un):
    if len(un)==0:
        return Decimal(0)
    un_sin_comas=un.replace(",","")
    ns= re.split(r'\.',un_sin_comas)
    if len(ns)==0:
        n = 0
    elif len(ns) == 1:
        n = ns[0]
    else:
        n = ns[0]+"."+ns[1]
    return Decimal(n)


def re_proveedor(nombre):
    """Si proveedor existe, devuelva objeto, si lo crea y devuelva"""
    provs = Proveedor.objects.filter(nombre = nombre)
    if provs:
        return provs[0]
    else:
        prov = Proveedor(nombre=nombre)
        prov.save()
        return prov

def addProveedor():
    ps = ['Genesal','Enrique','Saltoki']
    [re_proveedor(p) for p in ps]
    return True

def re_material(material):
    """Si material existe, devuelva objeto, si no lo crea y devuelva.
    formato de material [nombre, nombre de proveedor, unidades, precioRef]
    
    para implementar:
    si el precio o unidades del material existente no so iguales, lo actualiza.
    """
    ms = Material.objects.filter(nombre = material[0], 
                                 proveedor = re_proveedor(material[1]))
    if ms:
        m = ms[0]
        return m
    else:
        m = Material(nombre=material[0], 
                     proveedor=re_proveedor(material[1]),
                     unidades=material[2], 
                     precioRef=dot2Dec(material[3]))
        m.save()
        return m

def addMaterial(ms):    
    [re_material(m) for m in ms]
    return True

def addCliente():
    cs= [('Sea', 'Paseo Sagasta 6', 'Zaragoza', 'Espana', '+56 55 2355526')]
    [Cliente(nombre=c[0], direccion1=c[1], direccion2 = c[2],
             pais =c[3], telefono = c[4]).save() for c in cs]
    return True

def addProforma():
    fechaHoy = datetime.date.today()
    fechaManana = datetime.date.today() + datetime.timedelta(days=1)
    fechaAyer = datetime.date.today() - datetime.timedelta(days=1)
    
    ps = [('SO', 'Sea', 'Suministro Generadores', fechaHoy, 'EXW', 'ES', 0.18),
          ('SO', 'Sea', 'BombaEXW', fechaAyer, 'EXW', 'AO', 0.18),
          ('SO', 'Sea', 'BombaFOB', fechaAyer, 'FOB', 'AO', 0.18),
          ('SO', 'Sea', 'BombaCIF', fechaAyer, 'CIF', 'AO', 0.18),
          ('SO', 'Sea', 'BombaDDP', fechaManana, 'DDP', 'AO', 0.18),
    ]
    

    [Proforma(vendedor=p[0], cliente=Cliente.objects.get(nombre=p[1]), 
              titulo=p[2], fecha=p[3], incoterms = p[4], 
              paisDeVenta = p[5]).save() for p in ps]
    return True

def addPartida():
    ps=[('Suministro Generadores', 1, 4, 3800),
        ('BombaEXW',4,1,1000), ('BombaFOB',4,1,1000),
        ('BombaCIF',4,1,1000), ('BombaDDP',4,1,1000)]

    [Partida(proforma=Proforma.objects.get(titulo=p[0]), 
             material=Material.objects.get(id=p[1]),  
             cantidad=p[2], pcoUnitario=p[3],
             pco_manipulado = p[3]).save() for p in ps]
    return True

def addTodo1():
    addProveedor()
    ms = [('Generador 7 kVAs Estacionario', 'Genesal', 'u', 4000),
          ('Generador 33 kVAs Estacionario', 'Genesal', 'u', 16000),
          ('Generador 60 kVAs Estacionario', 'Genesal', 'u', 24000),
          ('Tanque combustible 1000l', 'Enrique', 'u', 1000),]
    addMaterial(ms)
    addCliente()
    addProforma()
    addPartida()
    return True

def addContenedor():
    cs = [("1x20", 1500, 3500, 1500), ("1x40st", 2200, 5000, 2000),
     ("1x40hc", 2500, 5500, 2000), ("1x40ot", 3500, 5500, 2000)]
    [Contenedor(tipo = c[0], precio = c[1], precioFlete = c[2],
                transporteMontaje = c[3]).save() for c in cs] 
    return True

def addContenedoresDeProforma():
    cps = [('BombaFOB', "1x20", 1), ('BombaFOB', "1x40st", 1),
           ('BombaCIF', "1x20", 1), ('BombaCIF', "1x40st", 1),
           ('BombaDDP', "1x20", 1), ('BombaDDP', "1x40st", 1),]

    for cp in cps:
        contenedorT = Contenedor.objects.get(tipo=cp[1])
        proformaT = Proforma.objects.get(titulo=cp[0])
        ContenedoresDeProforma( 
            proforma=proformaT, 
            contenedor= contenedorT, cantidad = cp[2], 
            precio =contenedorT.precio, 
            precioFlete = contenedorT.precioFlete,
            transporteMontaje=contenedorT.transporteMontaje).save() 
    return True

def addTodo2():
    addContenedoresDeProforma()
    return True
    
def addTodo():
    addTodo1()
    addContenedor()
    addTodo2()

###
def testCalPartida(): 
    proforma = Proforma.objects.all()[0]
    partida = proforma.partida_set.all()[0]
    print(proforma.kProforma())
    print(partida.pvUnitario())


####

#Base de datos de csv

def populate_db_csv(csv_path):
    with open(csv_path,'rb') as csvfile:
        datos = csv.reader(csvfile)
        firstLine = True
        for row in datos:
            if firstLine:
                firstLine = False
            else:
                re_material(row)
                
