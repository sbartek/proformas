#This Python file uses the following encoding: utf-8

#TO DO:
#0. Montaje, 
#1. Pdf 
#2. Ventans rotas: unidades, unidades, puntuacion de numeros, 
#3. manual
#4. usuario, numeracion de proformas
#5. copias de proformas
#seguro_cif -> seguro_CIF

from django.db import models
import datetime
from decimal import *
from .constantes import *

class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    #Primeria linea de la direccion
    direccion1 = models.CharField(max_length=60)
    #Segunda linea de la direccion 
    direccion2 = models.CharField(blank=True, max_length=60)
    pais = models.CharField(max_length=40)
    telefono = models.CharField(max_length=20)

    def direccion(self):
        return self.direccion1+" "+self.direccion2+" "

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.nombre

class Material(models.Model):
    nombre = models.CharField(max_length=200)
    proveedor = models.ForeignKey(Proveedor)
    ###Lista de unidades en futuro:
    unidades = models.CharField(max_length=3,
                                choices=UNIDADES,
                                default=UNIDAD)
    precioRef = models.DecimalField(blank=True, null=True, max_digits=11, 
                                    decimal_places=2)
    #Moneda Euro

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.nombre+": "+self.proveedor.__unicode__()


#en lo que sigue, por ejemplo, 0.11 = 11%
COMERCIAL_SOLUCIONES = 0.12
COMERCIAL_AY = 0.03
COMERCIAL_PDE = 0.03

#COMERCIAL1 = 0.18

COMERCIAL2 = 0.12  #sobre Pv_CIF (MARGEN SAEMA)
COMERCIAL3 = 0 #sobre pvp (precio de venta al cliente final)

class Proforma(models.Model):
    """Lo que falta:
    campo: moneda_de_venta
    Usuario """
    EUR2USD = 1.35 


    #Seguro: sobre Pv_CIF 
    SEGURO_CIF = 0.005
    
    ADUANA = 0.3 #sobre Pv_CIF
    #Coste transitario y puerto Angola (sobre Pv_CIF)
    TRANS_PUERTO = 0.021

    #Sobre pvp
    GASTOS_FINANCIEROS = 0.01
    GASTOS_IMPREVISTOS = 0.05
    IMPUESTO_MATERIALES = 0.055
    
 
    titulo =  models.CharField(max_length=200)   
    vendedor = models.CharField(max_length=2,
                                choices=VENDEDORES,
                                default=SAEMA)
    cliente = models.ForeignKey(Cliente)
    fecha = models.DateField(default =  datetime.date.today())
    incoterms = models.CharField(max_length=3,
                                 choices=INCOTERMS,
                                 default=CIF)
    paisDeVenta = models.CharField("pais de venta", max_length=2,
                                   choices=PAISES, default=ANGOLA)
    comercialSoluciones = models.DecimalField("coeficiente Soluciones",
                                              max_digits=6, decimal_places=4,
                                              default = COMERCIAL_SOLUCIONES)
    comercialAY = models.DecimalField("coeficiente AY",
                                      max_digits=6, decimal_places=4,
                                      default = COMERCIAL_AY)
    comercialPDE = models.DecimalField("coeficiente PDE",
                                       max_digits=6, decimal_places=4,
                                      default = COMERCIAL_PDE)

    comercial2 = models.DecimalField("coeficiente Saema",
                                     max_digits=6, decimal_places=4,
                                      default = COMERCIAL2)
    comercial3 = models.DecimalField("coeficiente terceros",
                                     max_digits=6, decimal_places=4,
                                     default = COMERCIAL3)
    eur2usd = models.DecimalField("tipo de cambio Euro a Dolar",
                                  max_digits=6, decimal_places=4,
                                  default = EUR2USD)
    seguro_cif = models.DecimalField(max_digits=7, decimal_places=5,
                                     default = SEGURO_CIF)
    aduana = models.DecimalField(max_digits=6, decimal_places=4,
                                 default = ADUANA)
    #costes, puerto Angola
    trans_puerto = models.DecimalField(max_digits=6, decimal_places=4,
                                       default = TRANS_PUERTO)
    gastos_financieros = models.DecimalField(max_digits=6, decimal_places=4,
                                       default = GASTOS_FINANCIEROS)
    gastos_imprevistos = models.DecimalField(max_digits=6, decimal_places=4,
                                       default = GASTOS_IMPREVISTOS)
    #Impuesto local
    impuestoMaterial = models.DecimalField(max_digits=6, decimal_places=4,
                                       default = IMPUESTO_MATERIALES)
    
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.titulo+":"+self.cliente.__unicode__()+","+self.incoterms

    def comercial1(self): 
        return self.comercialSoluciones + self.comercialAY + self.comercialPDE

    def tipoDeCambio(self, moneda1, moneda2):
        if moneda1 == EUR:
            if moneda2 == EUR:
                return Decimal(1.0)
            elif moneda2 == USD:
                return self.eur2usd
            else:
                return None
        elif moneda1 == USD:
            if moneda2 == USD:
                return Decimal(1.0)
            elif moneda2 == EUR:
                return Decimal(1.0)/self.eur2usd
        else:
            return None

    def pcoTotal(self, moneda = EUR):
        return Decimal(sum([p.pcoTotal(moneda) for p in self.partida_set.all()]))

    def costeContenedores(self, moneda=USD):
        """Coste total de compra de contenedores"""
        if self.incoterms == EXW:
            return 0
        cps = self.contenedoresdeproforma_set.all()
        cConEUR=sum([cp.cantidad*cp.precio 
                     for cp in cps])
        return cConEUR*Decimal(self.tipoDeCambio(EUR,moneda))

    def costePortesFOB(self, moneda = EUR):
        """Coste total de seguros, transporte terestra hasta puerto,
        embalaje ... NO INCLUYE COSTE DE COMPRA DE CONTENEDOR"""
        if self.incoterms == EXW:
            return 0
        cps = self.contenedoresdeproforma_set.all()
        cPortesEUR=sum([cp.cantidad*cp.portes_fob for cp in cps])
        return cPortesEUR*Decimal(self.tipoDeCambio(EUR,moneda))

    def costeFOB(self, moneda = EUR):
        """Coste total de compra de contenedores, seguros, transporte terestra
        hasta puerto, embalaje ...
        """
        return  self.costeContenedores(moneda)+self.costePortesFOB(moneda)

    def costeFlete(self,moneda = EUR):
        if self.incoterms == EXW or self.incoterms == FOB:
            return 0
        cps = self.contenedoresdeproforma_set.all()
        cFleteEUR = sum([cp.cantidad*cp.precioFlete  for cp in cps])
        return cFleteEUR*Decimal(self.tipoDeCambio(EUR,moneda))

    def transporte_contenedores_local(self, moneda=USD):
        """función número y tipo contenedores y destino en Angola,
        sirve como referencia para coste de transporte local en Montaje"""
        cps = self.contenedoresdeproforma_set.all()
        cTL_USD=sum([cp.cantidad*cp.transporteMontaje 
                     for cp in cps])
        return cTL_USD*Decimal(self.tipoDeCambio(USD,moneda))
    
    def con_montaje(self):
        return len(Montaje.objects.filter(proforma = self))==1
        
    def coste_montaje(self,moneda=USD):
        if self.con_montaje():
            return self.montaje.pvp_montaje_total(moneda)
        else:
            return 0
    
    def pre_k(self,incoterms=CIF):
        ###Mis ks no contienen tipo de cambio!!!!!!
        if incoterms == EXW:
            return  1/(1-self.comercial1())
        elif incoterms == CIF:
            return 1/(1-self.comercial1()-self.seguro_cif)
        else:
            return None
            
    def decimal_pre_k(self):
        return self.pre_k(incoterms=CIF).quantize(Decimal('1.00'))


    def k(self,incoterms):
        ###Mis ks no contienen tipo de cambio!!!!!!
        if self.pcoTotal() == 0:
            return 1
        if incoterms == EXW:
            kP =  1/(1-self.comercial1())
        elif incoterms == FOB:
            kP = (1+(self.costeFOB()/self.pcoTotal()))/(1-self.comercial1())
        else:
            kP1 = ((1+((self.costeFOB()+self.costeFlete())/self.pcoTotal()))/
                    (1-self.comercial1()-self.seguro_cif))
            if incoterms == CIF:
                kP = kP1
            else:
                kP2 = (kP1*(1+self.comercial2+self.aduana+self.trans_puerto)
                          /(1-self.comercial3-self.gastos_financieros
                            -self.gastos_imprevistos-self.impuestoMaterial))
                if incoterms == DDP:
                    kP=kP2
                elif incoterms == D_M:
                    kP=kP2*(1+self.coste_montaje(moneda=USD)
                            /(self.pcoTotal(moneda=USD)*kP2))
                else:
                    return None
        return kP

    def decimal_k(self,incoterms):
        return self(incoterms).quantize(Decimal("1.00"))

    def pv(self, incoterms, moneda=USD):
        if incoterms == EXW:
            return self.pcoTotal(moneda)*self.k(EXW)
        elif incoterms == FOB:
            return (self.pcoTotal(moneda)+self.costeFOB(moneda))*self.k(FOB)
        elif incoterms == CIF:
            return (self.pcoTotal(moneda))*self.k(CIF)
        elif incoterms == DDP:
            return (self.pcoTotal(moneda))*self.k(DDP)
        else:
            return Decimal('0.0')

    def kProforma(self):
        ###Mis ks no contienen tipo de cambio!!!!!!
        return self.k(self.incoterms)

    def k_con_taza(self,moneda1=EUR, moneda2=USD):
        return self.kProforma()*Decimal(self.tipoDeCambio(moneda1,moneda2))

    def pvTotalTest(self, moneda = USD):
        return self.pcoTotal(moneda)*self.kProforma()

    def pvTotal(self, moneda = USD):
        return sum([p.pvTotal(moneda) for p in self.partida_set.all()])

    def pv_total_manipulado(self, moneda = USD):
        return sum([p.pv_total_manipulado(moneda) 
                    for p in self.partida_set.all()])

    def costes(self, moneda = USD):
        return {EXW:{'compra_materiales':self.pcoTotal(moneda),
                 },
                FOB:{'compra_contenedores':self.costeContenedores(moneda),
                     'costes_portes_FOB':self.costePortesFOB(moneda),
                     'costes_FOB':self.costeFOB(moneda)},
                CIF:{
                    'pv_CIF':(self.pv(CIF,moneda)).quantize(Decimal('1.00')),
                    'costes_flete':self.costeFlete(moneda),
                    'seguro_CIF':
                       (self.pv(CIF,moneda)
                        *self.seguro_cif).quantize(Decimal('1.00')),
                    'transporte1': 
                       ((self.costeFlete(moneda)+self.costeFOB(moneda)
                       )*self.pre_k(CIF)).quantize(Decimal('1.00')),#de tablaC14
                 },
                DDP:{
                    'pv_DDP':(self.pv(DDP,moneda)).quantize(Decimal('1.00')),
                    'costes_puerto_Angola':
                         (self.pv(CIF,moneda)*self.trans_puerto
                         ).quantize(Decimal('1.00')),
                    'aduana': (self.pv(CIF,moneda)*self.aduana
                               ).quantize(Decimal('1.00')),
                    'costes_financieros': 
                       (self.pv(DDP,moneda)*self.gastos_financieros).quantize(Decimal('1.00')),
                    'impuestos_locales':
                       (self.pv(DDP,moneda)*self.impuestoMaterial).quantize(Decimal('1.00')),
                    'imprevistos':
                       (self.pv(DDP,moneda)*self.gastos_imprevistos).quantize(Decimal('1.00')),
                 },
        }

    def comision(self,org,moneda=USD):
        com = 0
        if org == SOLUCIONES:
            com = self.pv(CIF,moneda)*self.comercialSoluciones
        elif org == AY:
            com = self.pv(CIF,moneda)*self.comercialAY
        elif org == PDE:
            com = self.pv(CIF,moneda)*self.comercialPDE
        elif org == SAEMA:
            com = self.pv(CIF,moneda)*self.comercial2
        return com.quantize(Decimal('1.00'))

    def comisiones(self, moneda = USD):
        return {EXW:{'comisionSoluciones': self.comision(SOLUCIONES,moneda),
                     'comisionAY': self.comision(AY,moneda),
                     'comisionPDE': self.comision(PDE,moneda),
                 },
                DDP:{'comisionSaema':self.comision(SAEMA,moneda)},
                
        }

    def coste_total(self,moneda = USD):
        return (self.pcoTotal(moneda)+self.costeContenedores(moneda))

#class CapituloOferta(models.Model):
#    """permite separar partidas en oferta por capitulos"""
#    nombre = models.CharField(max_length=40)

class Partida(models.Model):
    #EURO !!!!!!!!!
    proforma = models.ForeignKey(Proforma)
    material = models.ForeignKey(Material)
    cantidad = models.IntegerField()
    pcoUnitario = models.DecimalField("precio de compra unitario (EUR)",
        max_digits=11, decimal_places=2)
    #Precio manipulado (compra en EUR):
    pco_manipulado = models.DecimalField("pco unitario (pendulum) (EUR)",
                                         max_digits=11, decimal_places=2, 
                                         default = 0)

    def __unicode__(self):
        return (self.material.__unicode__())

    def pco(self, moneda = EUR):
        return self.proforma.tipoDeCambio(EUR, moneda)*self.pcoUnitario

    def pcoTotal(self, moneda=EUR):
        return self.pco(moneda)*self.cantidad

    def pvUnitario(self, moneda = USD):
        return (Decimal(self.proforma.tipoDeCambio(EUR, moneda)
                *self.proforma.kProforma())
                *self.pcoUnitario).quantize(Decimal('1.00'))

    def pvTotal(self, moneda = USD):
        return (self.pvUnitario(moneda)*self.cantidad).quantize(Decimal('1.00'))

    def pv_manipulado(self, moneda = USD):
        return (Decimal(self.proforma.tipoDeCambio(EUR, moneda)
                *self.proforma.kProforma())
                *self.pco_manipulado).quantize(Decimal('1.00'))

    def pv_total_manipulado(self, moneda = USD):
        return (self.pv_manipulado(moneda)*self.cantidad).quantize(Decimal('1.00'))

    def proformaID(self):
        return self.proforma.id

    def save_pco_manipulado(self, precio, moneda = USD):
        self.pco_manipulado = precio*self.proforma.tipoDeCambio(moneda, EUR)
        return self.save()

    def save_pv_manipulado(self, precio, moneda = USD, cantidad = 1):
        return self.save_pco_manipulado(
            precio/(self.proforma.kProforma()*cantidad), 
            moneda)

class Contenedor(models.Model):
    """Precios en euro"""
    ###Cambio de los numeros aqui cambia TODAS ofertas
    tipo = models.CharField(max_length=40)
    #Precio de compra de un contenedor
    precio = models.DecimalField(max_digits=7, decimal_places=2)
    #Precio que ha de pagarse por alquiler de espacio en un barco
    precioFlete = models.DecimalField(max_digits=7, decimal_places=2)
    
    #Transporte Montaje en Dolares en Angola
    transporteMontaje = models.DecimalField(max_digits=7, decimal_places=2)

    def __unicode__(self):  # Python 3: def __str__(self):
        return (self.tipo+"-"+str(self.precio)+","+
                str(self.precioFlete)+","+str(self.transporteMontaje))

class ContenedoresDeProforma(models.Model):
    #portes_fob incluen seguros, transporte terestra hasta puerto,
    #embalaje ... NO INCLUYE COSTE DE COMPRA DE CONTENEDOR
    PORTES_FOB = 300

    proforma = models.ForeignKey(Proforma)
    contenedor = models.ForeignKey(Contenedor)
    cantidad = models.DecimalField(max_digits=5, decimal_places=2,
                                    default = 1)
    portes_fob = models.DecimalField(max_digits=7, decimal_places=2,
                                    default = PORTES_FOB)
    #Precio de compra de un contenedor
    precio = models.DecimalField(max_digits=7, decimal_places=2)
    #Precio que ha de pagarse por alquiler de espacio en un barco
    precioFlete = models.DecimalField(max_digits=7, decimal_places=2)    
    #Transporte Montaje en Dolares en Angola
    transporteMontaje = models.DecimalField(max_digits=7, decimal_places=2)

    def __unicode__(self):  # Python 3: def __str__(self):
        return (self.proforma.titulo+":"+self.contenedor.tipo+
                ":"+str(self.cantidad)+","+str(self.precio))
# class Oferta(models.Model):
#     proforma = models.ForeignKey(Proforma)

# class OfertaItems(models.Model):
#     oferta = models.ForeignKey(Oferta)
#     partida = models.ForeignKey(Partida)
#     pvItem = models.DecimalField(max_digits=7, decimal_places=2)

class Montaje(models.Model):
    """Cambiar: una proforma puede tener dos montajes
    """
    #Sobre Pv
    GASTOS_FINANCIEROS = 0.01 #%
    GASTOS_IMPREVISTOS = 0.05 #%
    IMPUESTO_SOBRE_SERVICIO = 0.1125 #%
    
    proforma = models.OneToOneField(Proforma, primary_key=True)
    #en USD:
    coste = models.DecimalField(max_digits=11, decimal_places=2, default = 0)
    transporte_local = models.DecimalField(max_digits=11, decimal_places=2,
                                           default = 0)
    gastos_financieros = models.DecimalField(max_digits=6, decimal_places=4,
                                       default = GASTOS_FINANCIEROS)
    gastos_imprevistos = models.DecimalField(max_digits=6, decimal_places=4,
                                       default = GASTOS_IMPREVISTOS)
    impuesto_sobre_servicio = models.DecimalField(max_digits=6, decimal_places=4,
                                       default = IMPUESTO_SOBRE_SERVICIO)
    comercial2 = models.DecimalField(max_digits=6, decimal_places=4,
                                     default = COMERCIAL2)
    comercial3 = models.DecimalField(max_digits=6, decimal_places=4,
                                     default = COMERCIAL3)
    
    descripcion = models.CharField(blank=True, max_length=240)

    def __unicode__(self):
        return "Montaje de proforma "+self.proforma.titulo+":"+str(self.coste)+" $"

    def pre_k_montaje(self):
        return Decimal(1.0)/(1-self.comercial2-self.comercial3
                             -self.gastos_financieros -self.gastos_imprevistos 
                             -self.impuesto_sobre_servicio)

    def pvp_montaje(self, moneda=USD):
        return (self.coste*self.pre_k_montaje()
                *Decimal(self.proforma.tipoDeCambio(USD,moneda)))

    def pvp_transporte_local(self, moneda=USD):
        return (self.transporte_local*self.pre_k_montaje()
                *Decimal(self.proforma.tipoDeCambio(USD,moneda)))

    def pvp_montaje_total(self, moneda=USD):
        return  (self.pvp_montaje(moneda)
                 +self.pvp_transporte_local(moneda)).quantize(Decimal('1.00'))
    

    def k_montaje(self):
        if self.coste == 0:
            return Decimal(1.0)
        else:
            return self.pvp_montaje_total()/self.coste
        
