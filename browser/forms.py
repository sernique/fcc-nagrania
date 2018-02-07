from django import forms


class SearchForm(forms.Form):
    text = forms.CharField(label='Ciąg znaków do wyszukania', max_length=100)
