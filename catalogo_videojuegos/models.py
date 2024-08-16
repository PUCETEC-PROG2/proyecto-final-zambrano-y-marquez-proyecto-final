from django.db import models

class Catalogos(models.Model):
    catalogo = models.CharField(max_length=30, null=True, blank=True)
    item_catalogo = models.CharField(max_length=30, null=True, blank=True)
    id_raiz = models.IntegerField(null=True, blank=True)

    def __str__(self):
        if self.item_catalogo:
            return self.item_catalogo
        return self.catalogo
    
    class Meta:
        db_table = 'catalogo_videojuegos_catalogos'


class Clientes(models.Model):
    cedula = models.CharField(max_length=10, unique=True)
    apellidos_nombres = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100, unique=True)
    provincia = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.apellidos_nombres

    class Meta:
        db_table = 'catalogo_videojuegos_clientes'

class Inventario(models.Model):
    codigo_producto = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    id_formato = models.ForeignKey(Catalogos, on_delete=models.CASCADE, db_column='id_formato' ,related_name='formato')
    id_genero = models.ForeignKey(Catalogos, on_delete=models.CASCADE, db_column='id_genero' ,related_name='genero')
    id_plataforma = models.ForeignKey(Catalogos, on_delete=models.CASCADE, db_column='id_plataforma' ,related_name='plataforma')
    ano_lanzamiento = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    id_estado_producto = models.ForeignKey(Catalogos, on_delete=models.CASCADE, db_column='id_estado_producto' ,related_name='estado_producto')

    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'catalogo_videojuegos_inventario'


class Ventas(models.Model):
    id_cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, db_column='id_cliente')
    fecha = models.DateTimeField()
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    id_forma_pago = models.ForeignKey(Catalogos, on_delete=models.CASCADE, db_column='id_forma_pago' ,related_name='forma_pago')

    def __str__(self):
        return f"Venta {self.id} - Cliente {self.id_cliente}"
    
    class Meta:
        db_table = 'catalogo_videojuegos_ventas'


class Detalle_Ventas(models.Model):
    id_venta = models.ForeignKey(Ventas, on_delete=models.CASCADE, db_column='id_venta')
    id_producto = models.ForeignKey(Inventario, on_delete=models.CASCADE, db_column='id_producto')
    cantidad_producto = models.IntegerField()

    def __str__(self):
        return f"Detalle Venta {self.id} - Venta {self.id_venta}"

    class Meta:
        db_table = 'catalogo_videojuegos_detalle_ventas'
