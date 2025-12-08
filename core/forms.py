from django import forms
from .models import Productos, Categoria, Personas
import re


class ContactFormForm(forms.Form):
    """Formulario de contacto con validación completa"""
    name = forms.CharField(
        label='Nombre',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    lastname = forms.CharField(
        label='Apellido',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Apellido',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    phone = forms.CharField(
        label='Teléfono',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Teléfono',
            'class': 'form-control',
            'type': 'tel'
        })
    )
    
    message = forms.CharField(
        label='Mensaje',
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': 'Mensaje',
            'class': 'form-control',
            'cols': 30,
            'rows': 5
        })
    )
    
    terms_accepted = forms.BooleanField(
        label='Acepto los Términos y Condiciones',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'terms-checkbox',
            'required': 'required'
        })
    )
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Validar que sea un número razonable (solo números, +, -, espacios, paréntesis)
            phone_pattern = r'^[\d\s\+\-\(\)]+$'
            if not re.match(phone_pattern, phone):
                raise forms.ValidationError('El teléfono debe contener solo números y caracteres permitidos (+, -, espacios, paréntesis).')
            # Verificar que tenga al menos 7 dígitos
            digits = re.sub(r'\D', '', phone)
            if len(digits) < 7:
                raise forms.ValidationError('El teléfono debe tener al menos 7 dígitos.')
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Validar que no contenga 'ñ' ni otros caracteres especiales problemáticos
        if email and 'ñ' in email.lower():
            raise forms.ValidationError('El correo no debe contener caracteres especiales como "ñ".')
        return email


class PasswordRecoveryEmailForm(forms.Form):
    """Formulario para solicitar recuperación de contraseña por correo"""
    correo = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu correo registrado',
            'required': 'required'
        })
    )


class SetNewPasswordForm(forms.Form):
    """Formulario para establecer una nueva contraseña"""
    password = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nueva contraseña',
            'required': 'required'
        }),
        min_length=10
    )
    
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu nueva contraseña',
            'required': 'required'
        }),
        min_length=10
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data


class ProductoCreateForm(forms.ModelForm):
    imagen = forms.ImageField(required=True, error_messages={
        'required': 'La imagen es requerida para crear el producto'
    })

    class Meta:
        model = Productos
        fields = [
            'nombre', 'descripcion_producto', 'precio', 'referencia',
            'cantidad_existente', 'stock_max', 'stock_min', 'categoria_id_categoria', 'imagen'
        ]

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if not imagen:
            raise forms.ValidationError('La imagen es requerida para crear el producto')
        return imagen


class ProductoEditForm(forms.ModelForm):
    # En edición la imagen es opcional (se puede mantener la existente)
    imagen = forms.ImageField(required=False)

    class Meta:
        model = Productos
        fields = [
            'nombre', 'descripcion_producto', 'precio', 'referencia',
            'cantidad_existente', 'stock_max', 'stock_min', 'categoria_id_categoria', 'imagen'
        ]


class RegisterForm(forms.Form):
    """
    Formulario de registro para nuevos usuarios.
    Crea SIEMPRE usuarios con rol='cliente', sin opción de elección.
    """
    nombre_persona = forms.CharField(
        label='Nombre',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    apellido_persona = forms.CharField(
        label='Apellido',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Apellido',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    correo_persona = forms.EmailField(
        label='Correo Electrónico',
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'tu@correo.com',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña (mín. 10 caracteres)',
            'class': 'form-control',
            'required': 'required'
        }),
        min_length=10
    )
    
    telefono = forms.CharField(
        label='Teléfono',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Teléfono',
            'class': 'form-control',
            'type': 'tel',
            'required': 'required'
        })
    )
    
    direccion = forms.CharField(
        label='Dirección',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Dirección',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    acepto_terminos = forms.BooleanField(
        label='Acepto los Términos y Condiciones',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'required': 'required'
        })
    )
    
    def clean_correo_persona(self):
        """Valida que el correo no esté registrado"""
        correo = self.cleaned_data.get('correo_persona')
        if Personas.objects.filter(correo_persona=correo).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return correo
    
    def clean_password(self):
        """Valida la seguridad de la contraseña"""
        password = self.cleaned_data.get('password')
        
        if not password or len(password) < 10:
            raise forms.ValidationError('La contraseña debe tener al menos 10 caracteres.')
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('Debe contener al menos una letra minúscula.')
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Debe contener al menos una letra mayúscula.')
        if not re.search(r'\d', password):
            raise forms.ValidationError('Debe contener al menos un número.')
        
        special_chars = re.findall(r'[!@#$%^&*()_+\-=[\]{}|;:\\\",.<>/?]', password)
        if len(special_chars) < 2:
            raise forms.ValidationError('Debe contener al menos dos caracteres especiales.')
        
        return password

