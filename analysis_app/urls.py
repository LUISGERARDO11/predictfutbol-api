from django.urls import path
from . import views

urlpatterns = [
    # Rutas existentes
    path('predict/', views.make_prediction, name='make_prediction'),
    path('retrain_model/', views.retrain_model, name='retrain_model'),
    path('predictwithouttd/', views.make_prediction_without_teamdata, name='make_prediction_without_teamdata'),
    path('get_teams_season/', views.get_teams_season, name='get_teams_season'),
]
