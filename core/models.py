from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CarritoCompras(models.Model):
    id_carrito_compras = models.BigAutoField(primary_key=True)
    cantidad_productos = models.IntegerField(blank=True, null=True)
    estado = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    ultima_actualizacion = models.DateTimeField(blank=True, null=True)
    clientes_personas_id_personas = models.ForeignKey('Personas', models.DO_NOTHING, db_column='clientes_personas_id_personas', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'carrito_compras'


class Categoria(models.Model):
    id_categoria = models.BigAutoField(primary_key=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    nombre_categoria = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'categoria'


class Clientes(models.Model):
    personas_id_personas = models.OneToOneField('Personas', models.DO_NOTHING, db_column='personas_id_personas', primary_key=True)

    class Meta:
        managed = False
        db_table = 'clientes'


class Compra(models.Model):
    id_compra = models.BigAutoField(primary_key=True)
    estado_compra = models.CharField(max_length=255, blank=True, null=True)
    fecha_compra = models.DateField(blank=True, null=True)
    metodo_pago = models.CharField(max_length=255, blank=True, null=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    sub_total_compra = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)
    total_compra = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)
    proveedores_id_proveedores = models.ForeignKey('Proveedores', models.DO_NOTHING, db_column='proveedores_id_proveedores', blank=True, null=True)
    vendedores_personas_id_personas = models.ForeignKey('Vendedores', models.DO_NOTHING, db_column='vendedores_personas_id_personas', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'compra'


class CompraHasProductos(models.Model):
    compra_id_venta = models.ForeignKey(Compra, models.DO_NOTHING, db_column='compra_id_venta')
    producto_id_producto = models.ForeignKey('Productos', models.DO_NOTHING, db_column='producto_id_producto')

    class Meta:
        managed = False
        db_table = 'compra_has_productos'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Marcas(models.Model):
    id_marcas = models.BigAutoField(primary_key=True)
    marca = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'marcas'


class PersonasManager(BaseUserManager):
    """Manager personalizado para el modelo Personas"""
    
    def create_user(self, correo_persona, password=None, **extra_fields):
        """Crea y guarda un usuario con el correo y contraseña dados"""
        if not correo_persona:
            raise ValueError('El correo es obligatorio')
        
        correo_persona = self.normalize_email(correo_persona)
        user = self.model(correo_persona=correo_persona, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, correo_persona, password=None, **extra_fields):
        """Crea y guarda un superusuario con el correo y contraseña dados"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(correo_persona, password, **extra_fields)


class Personas(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuario personalizado que hereda de AbstractBaseUser"""
    
    id_personas = models.BigAutoField(primary_key=True)
    apellido_persona = models.CharField(max_length=255, blank=True, null=True)
    correo_persona = models.CharField(unique=True, max_length=255)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    nombre_persona = models.CharField(max_length=255, blank=True, null=True)
    remember_token = models.CharField(max_length=255, blank=True, null=True)
    rol = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=50, default='Activo')
    
    # Campos estándar de autenticación - explícitamente declarados para managed=False
    # password: heredado de AbstractBaseUser
    last_login = models.DateTimeField(blank=True, null=True)
    # Campos de permisos - heredados de PermissionsMixin
    is_superuser = models.BooleanField(default=False)
    # Campos de staff y estado
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = PersonasManager()
    
    # Atributos requeridos por Django para modelo de usuario personalizado
    USERNAME_FIELD = 'correo_persona'  # Campo usado para login
    REQUIRED_FIELDS = []  # Otros campos obligatorios (aparte de password)
    
    class Meta:
        managed = False
        db_table = 'personas'
    
    def __str__(self):
        return f"{self.nombre_persona} ({self.correo_persona})"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        if self.nombre_persona and self.apellido_persona:
            return f"{self.nombre_persona} {self.apellido_persona}"
        return self.nombre_persona or self.correo_persona
    
    def get_short_name(self):
        """Retorna el nombre corto del usuario"""
        return self.nombre_persona or self.correo_persona



class Productos(models.Model):
    id_producto = models.BigAutoField(primary_key=True)
    cantidad_existente = models.IntegerField(blank=True, null=True)
    descripcion_producto = models.CharField(max_length=255, blank=True, null=True)
    # La imagen ahora se almacena como ImageField y es obligatoria (null=False, blank=False)
    imagen = models.ImageField(upload_to='uploads/', max_length=255, blank=False, null=False)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    precio = models.FloatField(blank=True, null=True)
    referencia = models.CharField(max_length=255, blank=True, null=True)
    stock_max = models.IntegerField(blank=True, null=True)
    stock_min = models.IntegerField(blank=True, null=True)
    categoria_id_categoria = models.ForeignKey(Categoria, models.DO_NOTHING, db_column='categoria_id_categoria', blank=True, null=True)
    marcas_id_marcas = models.ForeignKey(Marcas, models.DO_NOTHING, db_column='marcas_id_marcas', blank=True, null=True)
    vendedor = models.ForeignKey('Vendedores', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'productos'



class ProductosHasVentas(models.Model):
    producto_id_producto = models.ForeignKey(
        'Productos',
        db_column='producto_id_producto',
        on_delete=models.CASCADE,
        primary_key=True
    )
    ventas_id_venta = models.ForeignKey(
        'Ventas',
        db_column='ventas_id_venta',
        on_delete=models.CASCADE
    )
    cantidad = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        db_table = 'productos_has_ventas'
        managed = False
        unique_together = (('producto_id_producto', 'ventas_id_venta'),)


class Proveedores(models.Model):
    id_proveedores = models.BigAutoField(primary_key=True)
    correo = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    nombre_proveedor = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proveedores'


class Vendedores(models.Model):
    personas_id_personas = models.OneToOneField(Personas, models.DO_NOTHING, db_column='personas_id_personas', primary_key=True)

    class Meta:
        managed = False
        db_table = 'vendedores'


class Ventas(models.Model):
    id_venta = models.BigAutoField(primary_key=True)
    comentarios = models.CharField(max_length=255, blank=True, null=True)
    descuento = models.FloatField(blank=True, null=True)
    direccion_envio = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=255, blank=True, null=True)
    fecha_entrega_estimada = models.DateTimeField(blank=True, null=True)
    fecha_venta = models.DateTimeField(blank=True, null=True)
    metodo_pago = models.CharField(max_length=255, blank=True, null=True)
    sub_total = models.FloatField(blank=True, null=True)
    total = models.FloatField(blank=True, null=True)
    clientes_personas_id_personas = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='clientes_personas_id_personas', blank=True, null=True)
    vendedores_personas_id_personas = models.ForeignKey(Vendedores, models.DO_NOTHING, db_column='vendedores_personas_id_personas', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ventas'




