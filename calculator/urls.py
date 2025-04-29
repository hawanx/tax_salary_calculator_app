from django.urls import path
from .views import tax_calculator

urlpatterns = [
    path('', tax_calculator, name='tax_calculator'),
] 