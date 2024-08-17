from django import forms
from django.core.exceptions import ValidationError
from .models import Clientes, Inventario, Ventas, Detalle_Ventas, Catalogos

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['cedula', 'apellidos_nombres', 'correo', 'direccion', 'telefono']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos_nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')

        # Verificar que solo se hayan ingresado números
        if not cedula.isdigit():
            raise ValidationError("La cédula solo debe contener números.")

        # Algoritmo de validación de cédula ecuatoriana
        if len(cedula) != 10:
            raise ValidationError("La cédula debe tener 10 dígitos.")

        primeros_num = int(cedula[:2])
        if primeros_num < 1 or primeros_num > 24:
            raise ValidationError("Los dos primeros números deben estar entre 01 y 24.")

        tercer_num = int(cedula[2])
        if tercer_num < 0 or tercer_num > 5:
            raise ValidationError("El tercer número debe estar entre 0 y 5.")

        suma_impares = sum([(int(cedula[i]) * 2 if (int(cedula[i]) * 2) < 10 else (int(cedula[i]) * 2) - 9)
                            for i in range(0, 9, 2)])
        suma_pares = sum([int(cedula[i]) for i in range(1, 8, 2)])
        suma_total = suma_impares + suma_pares

        modulo_digito = suma_total % 10
        digito_verificador = 0 if modulo_digito == 0 else 10 - modulo_digito

        if digito_verificador != int(cedula[-1]):
            raise ValidationError("La cédula no es válida.")

        return cedula
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not telefono.isdigit():
            raise ValidationError("El teléfono solo debe contener números.")

        if len(telefono) != 10:
            raise ValidationError("El teléfono debe tener 10 dígitos.")
        
        if telefono[:2] != '09':
            raise ValidationError("El teléfono debe empezar con 09.")

        return telefono
    
    def save(self, commit=True):
        cliente = super().save(commit=False)
        # Llenar el campo provincia automáticamente
        provincia_map = {
            "01": "AZUAY", "02": "BOLIVAR", "03": "CAÑAR", "04": "CARCHI",
            "05": "COTOPAXI", "06": "CHIMBORAZO", "07": "EL ORO", "08": "ESMERALDAS",
            "09": "GUAYAS", "10": "IMBABURA", "11": "LOJA", "12": "LOS RÍOS",
            "13": "MANABÍ", "14": "MORONA SANTIAGO", "15": "NAPO", "16": "PASTAZA",
            "17": "PICHINCHA", "18": "TUNGURAHUA", "19": "ZAMORA CHINCHIPE", "20": "GALÁPAGOS",
            "21": "SUCUMBÍOS", "22": "ORELLANA", "23": "SANTO DOMINGO DE LOS TSÁCHILAS",
            "24": "SANTA ELENA"
        }
        primeros_dos_digitos = self.cleaned_data.get('cedula')[:2]
        cliente.provincia = provincia_map.get(primeros_dos_digitos, 'Desconocido')
        
        cliente.apellidos_nombres = cliente.apellidos_nombres.upper()
        cliente.correo = cliente.correo.upper()
        cliente.direccion = cliente.direccion.upper()
        
        if commit:
            cliente.save()
        return cliente
    
class CatalogoForm(forms.ModelForm):
    class Meta:
        model = Catalogos
        fields = ['catalogo', 'item_catalogo', 'id_raiz']
        widgets = {
            'catalogo': forms.TextInput(attrs={'class': 'form-control'}),
            'item_catalogo': forms.TextInput(attrs={'class': 'form-control'}),
            'id_raiz': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        catalogo = cleaned_data.get('catalogo')
        item_catalogo = cleaned_data.get('item_catalogo')
  
        if catalogo:
            cleaned_data['catalogo'] = catalogo.upper()
        if item_catalogo:
            cleaned_data['item_catalogo'] = item_catalogo.upper()
            
        if Catalogos.objects.filter(catalogo=catalogo, item_catalogo=item_catalogo).exists():
            self.add_error('item_catalogo','Ya existe un catálogo con el mismo nombre.')

        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if instance.catalogo and not instance.id_raiz:
            instance.id_raiz = None
            
        if instance.item_catalogo and not instance.id_raiz:
            catalogo_padre = Catalogos.objects.filter(catalogo=instance.catalogo, item_catalogo__isnull=True).first()
            if catalogo_padre:
                instance.id_raiz = catalogo_padre.id
        
        if commit:
            instance.save()
        return instance
    
class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['nombre', 'id_formato', 'id_genero', 'id_plataforma', 'ano_lanzamiento', 'precio_unitario', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'id_formato': forms.Select(attrs={'class': 'form-control'}),
            'id_genero': forms.Select(attrs={'class': 'form-control'}),
            'id_plataforma': forms.Select(attrs={'class': 'form-control'}),
            'ano_lanzamiento': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(InventarioForm, self).__init__(*args, **kwargs)
        
        formato_id = Catalogos.objects.get(catalogo="FORMATO").id
        genero_id = Catalogos.objects.get(catalogo="GENERO").id
        plataforma_id = Catalogos.objects.get(catalogo="PLATAFORMA").id
        
        self.fields['id_formato'].queryset = Catalogos.objects.filter(id_raiz=formato_id)
        self.fields['id_genero'].queryset = Catalogos.objects.filter(id_raiz=genero_id)
        self.fields['id_plataforma'].queryset = Catalogos.objects.filter(id_raiz=plataforma_id)
    
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        id_formato = cleaned_data.get('id_formato')
        id_plataforma = cleaned_data.get('id_plataforma')
        
        if Inventario.objects.filter(nombre=nombre, id_formato=id_formato, id_plataforma=id_plataforma).exists():
            self.add_error('nombre','Ya existe un producto con el mismo nombre, con el mismo formato y para la misma plataforma.')
            self.add_error('id_formato','Ya existe un producto con el mismo nombre, con el mismo formato y para la misma plataforma.')
            self.add_error('id_plataforma','Ya existe un producto con el mismo nombre, con el mismo formato y para la misma plataforma.')
            
        return cleaned_data
    
    def clean_ano_lanzamiento(self):
        ano_lanzamiento = self.cleaned_data.get('ano_lanzamiento')

        if ano_lanzamiento < 0:
            raise ValidationError("El año de lanzamiento no puede ser negativo.")
        
        return ano_lanzamiento
    
    def clean_precio_unitario(self):
        precio_unitario = self.cleaned_data.get('precio_unitario')

        if precio_unitario < 0:
            raise ValidationError("El precio unitario no puede ser negativo.")

        return precio_unitario
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')

        if stock < 0:
            raise ValidationError("El stock no puede ser negativo.")

        return stock

    def save(self, commit=True):
        inventario = super().save(commit=False)
        inventario.nombre = inventario.nombre.upper()
        
        if inventario.stock > 0:
            estado_disponible = Catalogos.objects.get(item_catalogo='DISPONIBLE')
            inventario.id_estado_producto = estado_disponible
        else:
            estado_no_disponible = Catalogos.objects.get(item_catalogo='NO DISPONIBLE')
            inventario.id_estado_producto = estado_no_disponible
            
        if not inventario.codigo_producto:
            inventario.codigo_producto = self.generar_codigo_producto()
        
        if commit:
            inventario.save()
        return inventario
    
    def generar_codigo_producto(self):
        ultimo_inventario = Inventario.objects.order_by('id').last()
        if ultimo_inventario:
            ultimo_codigo = ultimo_inventario.codigo_producto
            siguiente_numero = int(ultimo_codigo[1:]) + 1
        else:
            siguiente_numero = 1

        return f'P{siguiente_numero:05d}'
    
class VentaForm(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = ['id_cliente', 'fecha', 'id_forma_pago']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'id_cliente': forms.Select(attrs={'class': 'form-control'}),
            'id_forma_pago': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(VentaForm, self).__init__(*args, **kwargs)
        
        forma_pago_id = Catalogos.objects.get(catalogo="FORMA DE PAGO").id

        self.fields['id_forma_pago'].queryset = Catalogos.objects.filter(id_raiz=forma_pago_id)

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = Detalle_Ventas
        fields = ['id_producto', 'cantidad_producto']
        widgets = {
            'id_producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_producto': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }    