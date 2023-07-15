from django.urls import path
from tablebuilder.views import TableListView, TableDetailView, RowListView, RowDetailView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/table', TableListView.as_view(), name='table'),
    path('api/table/<int:id>', TableDetailView.as_view(),
         name='table_detail'),  # Changed 'table_id' to 'id'
    path('api/table/<int:id>/row', RowListView.as_view(),
         name='table_row'),  # Changed 'table_id' to 'id'
    path('api/table/<int:id>/row/<int:row_id>', RowDetailView.as_view(),
         name='table_row_detail'),  # Changed 'table_id' to 'id'
]
