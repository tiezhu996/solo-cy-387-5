from django.urls import path

from .views import PackageListCreateView, PackagePickupView, PackageStoreView

urlpatterns = [
    path('packages/', PackageListCreateView.as_view()),
    path('packages/store/', PackageStoreView.as_view()),
    path('packages/pickup/', PackagePickupView.as_view()),
]
