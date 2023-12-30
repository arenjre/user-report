from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from test_app import views
urlpatterns = [
    path('api/v1/login/', views.UserLoginView.as_view(), name="user-login"),
    path('api/v1/logout/', views.UserLogoutView.as_view(), name="user-logout"),
    path('api/v1/users/<int:id>/', views.UserDetailView.as_view(), name="user-details"),
    path('api/v1/countries/', views.CountryDetailView.as_view()),
    path('api/v1/upload-file/', views.UploadFileDetail.as_view()),
    path('api/v1/sales/', views.FileUploadView.as_view()),
    path('api/v1/sales/<int:pk>/', views.FileUploadView.as_view()),
    
    path('api/v1/sales-data/', views.SalesDataDetail.as_view()),
    path('api/v1/sale_statistics/', views.SalesStatisticsView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
