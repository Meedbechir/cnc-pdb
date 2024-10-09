from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Article, Designation, Origine, Inventaire, DetailInventaire
from .serializers import ArticleSerializer, DesignationSerializer

class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        designation = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def create(self, request, *args, **kwargs):
        designation_id = request.data.get('designation_id')
        origine_nom = request.data.get('origine')
        quantite = request.data.get('quantite')
        annee = request.data.get('annee', datetime.now().year)

        # Validation des champs obligatoires
        if not all([designation_id, origine_nom, quantite]) or quantite < 1:
            return Response({'error': 'Les champs désignation, origine, et quantité doivent être remplis, et la quantité doit être positive.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            designation = Designation.objects.get(id=designation_id)
        except Designation.DoesNotExist:
            return Response({'error': 'La désignation spécifiée n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)

        origine, _ = Origine.objects.get_or_create(nom=origine_nom)
        inventaire, _ = Inventaire.objects.get_or_create(annee=annee)

        articles = self.create_articles(designation, origine, inventaire, quantite)

        return Response({'message': f'{quantite} articles créés', 'articles': ArticleSerializer(articles, many=True).data}, status=status.HTTP_201_CREATED)

    def create_articles(self, designation, origine, inventaire, quantite):
        articles = []
        articles_existants = Article.objects.filter(designation=designation)

        dernier_numero = self.get_dernier_numero(articles_existants, designation)

        for i in range(1, quantite + 1):
            code_article = self.generate_code_article(designation, origine, dernier_numero + i)

            article = Article(
                designation=designation,
                origine=origine,
                inventaire=inventaire,
                code_article=code_article
            )
            article.save()

            DetailInventaire.objects.create(
                article=article,
                inventaire=inventaire,
                quantite=1,
                etat='Moyen',
                date=datetime.now().date()
            )

            articles.append(article)

        return articles

    def get_dernier_numero(self, articles_existants, designation):
        if articles_existants.exists():
            dernier_article = articles_existants.order_by('-code_article').first()
            dernier_code_article = dernier_article.code_article.split('/')[0]
            return int(dernier_code_article[len(designation.nom[:4].lower()):])
        return 0

    def generate_code_article(self, designation, origine, numero_article):
        code_article = f"{designation.nom[:4].lower()}{numero_article}/emplacement-pas-defini/{origine.nom.lower()}"
        
        while Article.objects.filter(code_article=code_article).exists():
            numero_article += 1 
            code_article = f"{designation.nom[:4].lower()}{numero_article}/emplacement-pas-defini/{origine.nom.lower()}"
        
        return code_article
