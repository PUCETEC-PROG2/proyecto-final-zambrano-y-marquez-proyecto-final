from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
import pytz

from .models import Clientes, Catalogos, Inventario, Ventas, Detalle_Ventas
from .forms import ClienteForm, InventarioForm, CatalogoForm, VentaForm, DetalleVentaForm


class CustomLoginView(LoginView):
    template_name = "login.html"

def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({'es_index': True}, request))

def clientes(request):
    clientes = Clientes.objects.order_by('id')
    template = loader.get_template('clientes.html')
    return HttpResponse(template.render({'clientes': clientes}, request))

def inventario(request):
    inventario = Inventario.objects.order_by('id')
    template = loader.get_template('inventario.html')
    return HttpResponse(template.render({'inventario': inventario}, request))

def catalogos(request):
    catalogos = Catalogos.objects.order_by('id')
    template = loader.get_template('catalogos.html')
    return HttpResponse(template.render({'catalogos': catalogos}, request))

def ventas(request):
    ventas = Ventas.objects.all().order_by('-fecha')
    detalle_ventas = Detalle_Ventas.objects.select_related('id_venta', 'id_producto', 'cantidad_producto').order_by('id')
    context = {
        'ventas': ventas,
        'detalle_ventas': detalle_ventas,
    }
    template = loader.get_template('ventas.html')
    return HttpResponse(template.render(context, request))

@login_required
def ingresar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('catalogo_videojuegos:clientes')
    else:
        form = ClienteForm()
    return render(request, 'formulario_cliente.html', {'form': form})

@login_required
def actualizar_cliente(request, cedula):
    cliente = get_object_or_404(Clientes, cedula=cedula)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('catalogo_videojuegos:clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'formulario_cliente.html', {'form': form})

@login_required
def eliminar_cliente(request, cedula):
    cliente = get_object_or_404(Clientes, cedula=cedula)
    cliente.delete()
    return redirect('catalogo_videojuegos:clientes')

def consultar_cliente(request):
    query = request.GET.get('cedula', None)
    cliente = None
    if query:
        try:
            cliente = Clientes.objects.get(cedula=query)
        except Clientes.DoesNotExist:
            cliente = None
            
    return render(request, 'consultar_cliente.html', {'cliente': cliente, 'query': query})

@login_required
def ingresar_catalogo(request):
    if request.method == 'POST':
        form = CatalogoForm(request.POST)
        if form.is_valid():
            catalogo = form.cleaned_data.get('catalogo')
            item_catalogo = form.cleaned_data.get('item_catalogo')
            id_raiz = form.cleaned_data.get('id_raiz')

            if catalogo:
                nuevo_catalogo = form.save(commit=False)
                nuevo_catalogo.id_raiz = None
                nuevo_catalogo.save()
            elif item_catalogo and id_raiz:
                form.save()

            return redirect('catalogo_videojuegos:catalogos')
    else:
        form = CatalogoForm()

    catalogos = Catalogos.objects.filter(id_raiz__isnull=True)
    return render(request, 'formulario_catalogo.html', {'form': form, 'catalogos': catalogos})

@login_required
def actualizar_catalogo(request, id):
    catalogo_instance = get_object_or_404(Catalogos, pk=id)
    catalogo_padre = None
    
    if catalogo_instance.item_catalogo:
        catalogo_padre = get_object_or_404(Catalogos, pk=catalogo_instance.id_raiz)

    if request.method == 'POST':
        form = CatalogoForm(request.POST, instance=catalogo_instance)
               
        if form.is_valid():           
            form.save() 
            return redirect('catalogo_videojuegos:catalogos') 
    else:
        form = CatalogoForm(instance=catalogo_instance)

    return render(request, 'actualizar_catalogo.html', {'form': form, 'catalogo_padre': catalogo_padre})

@login_required
def eliminar_catalogo(request, id):
    catalogo = get_object_or_404(Catalogos, pk=id)
    catalogo.delete()
    return redirect('catalogo_videojuegos:catalogos')

@login_required
def ingresar_inventario(request):
    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('catalogo_videojuegos:inventario')
    else:
        form = InventarioForm()
    return render(request, 'formulario_inventario.html', {'form': form})

@login_required
def actualizar_inventario(request, codigo_producto):
    producto = get_object_or_404(Inventario, codigo_producto=codigo_producto)
    if request.method == 'POST':
        form = InventarioForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('catalogo_videojuegos:inventario')
    else:
        form = InventarioForm(instance=producto)
    return render(request, 'formulario_inventario.html', {'form': form})

@login_required
def eliminar_inventario(request, codigo_producto):
    producto = get_object_or_404(Inventario, codigo_producto=codigo_producto)
    producto.delete()
    return redirect('catalogo_videojuegos:inventario')

def consultar_inventario(request):
    query = request.GET.get('codigo_producto', None)
    producto = None
    if query:
        try:
            producto = Inventario.objects.get(codigo_producto=query)
        except Inventario.DoesNotExist:
            producto = None
            
    return render(request, 'consultar_inventario.html', {'producto': producto, 'query': query})

def detalle_venta(request, id):
    venta = get_object_or_404(Ventas, pk=id)
    detalles = Detalle_Ventas.objects.filter(id_venta=venta) 
    
    return render(request, 'detalle_venta.html', {
        'venta': venta,
        'detalles': detalles
    })

@login_required    
def ingresar_venta(request):
    clientes = Clientes.objects.all()
    forma_pago_id = Catalogos.objects.get(catalogo="FORMA DE PAGO").id
    formas_pago = Catalogos.objects.filter(id_raiz=forma_pago_id)
    productos = Inventario.objects.all()
    
    tz_local = pytz.timezone('America/Bogota')
    fecha_hoy = timezone.now().astimezone(tz_local).strftime('%Y-%m-%dT%H:%M')

    if request.method == 'POST':
        # Extraer los datos del formulario
        cliente_id = request.POST.get('cliente')
        fecha = request.POST.get('fecha')
        forma_pago_id = request.POST.get('forma_pago')
        productos_seleccionados = request.POST.getlist('productos[]')  # IDs de productos seleccionados
        cantidades = request.POST.getlist('cantidades[]')  # Cantidades correspondientes a los productos


        # Crear una nueva venta
        venta = Ventas.objects.create(
            id_cliente_id=cliente_id,
            fecha=fecha,
            total_venta=0,  # Temporalmente 0, se actualizará más tarde
            id_forma_pago_id=forma_pago_id
        )

        # Procesar los productos seleccionados
        total_venta = 0
        for idx, producto_id in enumerate(productos_seleccionados):
            producto = Inventario.objects.get(id=producto_id)
            cantidad = int(cantidades[idx])
            precio_total = producto.precio_unitario * cantidad
            total_venta += precio_total

            # Crear detalle de la venta
            Detalle_Ventas.objects.create(
                id_venta=venta,
                id_producto=producto,
                cantidad_producto=cantidad
            )

        # Actualizar el total de la venta
        venta.total_venta = total_venta
        venta.save()

        return redirect('catalogo_videojuegos:ventas')

    context = {
        'clientes': clientes,
        'formas_pago': formas_pago,
        'productos': productos,
        'fecha_hoy': fecha_hoy,
    }
    return render(request, 'ingresar_venta.html', context)

def consultar_venta(request):
    query = request.GET.get('cedula', None)
    ventas = None
    if query:
        try:
            cliente_id = Clientes.objects.get(cedula=query).id
            ventas = Ventas.objects.filter(id_cliente=cliente_id).prefetch_related('detalle_ventas_set')
        except Clientes.DoesNotExist:
            ventas = None
    
    return render(request, 'consultar_venta.html', {'ventas': ventas, 'query': query})