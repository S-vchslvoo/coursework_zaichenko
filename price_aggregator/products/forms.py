from django import forms

class OrderForm(forms.Form):
    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '+375 (29) ...'
        })
    )
    address = forms.CharField(
        label="Адрес доставки",
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Улица, дом, квартира...'
        })
    )