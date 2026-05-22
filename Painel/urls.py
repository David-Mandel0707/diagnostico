from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('/painel/')),
    path('painel/', views.render_painel, name='painel'),
    path('membro/', views.buscar_membro, name='buscar_membro')
]