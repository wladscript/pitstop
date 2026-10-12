from django.urls import path
from . import views

app_name = "pagamentos"

urlpatterns = [
    path("os/<int:ordem_id>/pix/", views.pix_os_view, name="pix_os"),
]
