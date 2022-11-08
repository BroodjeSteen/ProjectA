from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('station/', views.stations, name='stations'),
    path('station/search/', views.station_search, name='station_search'),
    path('station/<slug:id>/', views.station, name='station'),
    path('station/<slug:id>/get-messages/', views.station_get_messages, name='station_get_messages'),
    path('station/<slug:id>/get-forecast/', views.station_get_forecast, name='station_get_forecast'),
    path('station/<slug:id>/get-departures/', views.station_get_departures, name='station_get_departures'),
    path('station/<slug:id>/get-facilities/', views.station_get_facilities, name='station_get_facilities'),
    path('station/<slug:id>/get-disruptions/', views.station_get_disruptions, name='station_get_disruptions'),
    path('station/<slug:id>/message/', views.station_message, name='station_message'),

    path('admin/', views.admin, name='admin'),
    path('admin/mod/', views.admin_mod, name='admin_mod'),
    path('admin/mod/get-message/', views.admin_mod_get_message, name='admin_mod_get_message'),
    path('admin/mod/<slug:id>/', views.admin_mod, name='admin_mod'),

    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
]