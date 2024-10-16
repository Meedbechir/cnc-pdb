from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Article, Designation,Famille
from .serializers import ArticleSerializer, DesignationSerializer, FamilleSerializer
from .services import ArticleService, ArticleCreationError

class FamilleViewSet(viewsets.ModelViewSet):
    queryset = Famille.objects.all()
    serializer_class = FamilleSerializer

class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('id')
    serializer_class = ArticleSerializer
    article_service = ArticleService()

    def create(self, request, *args, **kwargs):
        try:
            articles = self.article_service.create_article(request.data)
            return Response({'message': f'{len(articles)} articles créés', 'articles': ArticleSerializer(articles, many=True).data}, status=status.HTTP_201_CREATED)
        except ArticleCreationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        article = self.get_object()
        emplacement_nom = request.data.get('emplacement').replace(' ', '-')

        if not emplacement_nom:
            return Response({'error': 'Le nom de l\'emplacement est requis.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            code_article = self.article_service.update_article(article, emplacement_nom)
            return Response({
                'message': 'Article mis à jour avec succès.',
                'article': ArticleSerializer(article).data,
                'code_article': code_article
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

