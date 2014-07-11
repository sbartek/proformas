import datetime

from django import forms
from django.contrib.admin import widgets   
from django.forms.extras.widgets import SelectDateWidget

from .models import Proforma, Partida, ContenedoresDeProforma, Montaje, Material, Cliente, Proveedor
from .constantes import *

class ProformaForm(forms.ModelForm):
    class Meta:
        model = Proforma
        fields = ['titulo', 'vendedor', 'cliente', 'fecha', 'incoterms', 
                  'paisDeVenta', 'eur2usd', 'comercialSoluciones', 'comercial2',
                  'comercial3',  'comercialAY', 'comercialPDE']
        widgets = {
            'fecha': SelectDateWidget(),
        }

class PartidaForm(forms.ModelForm):
    class Meta:
        model = Partida
        fields = ['material', 'cantidad', 'pcoUnitario', 'pco_manipulado']

class ContenedoresDeProformaForm(forms.ModelForm):
    class Meta:
        model = ContenedoresDeProforma
        exclude = ['proforma']

class MontajeForm(forms.ModelForm):
    class Meta:
        model = Montaje
        exclude = ['proforma']
        widgets = {
            'descripcion': forms.Textarea(attrs={'cols': 40, 'rows': 6}),
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
