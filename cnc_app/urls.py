from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, DesignationViewSet, FamilleViewSet


router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'designations', DesignationViewSet)
router.register(r'familles', FamilleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
