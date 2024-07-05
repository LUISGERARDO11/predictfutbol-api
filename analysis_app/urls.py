from django.urls import path
from . import views

urlpatterns = [
    # Rutas existentes
    path('predict/', views.make_prediction, name='make_prediction'),
    
    # Nueva ruta para el endpoint POST
    path('predictwithouttd/', views.make_prediction_without_teamdata, name='make_prediction_without_teamdata'),
]
