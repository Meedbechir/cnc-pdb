from rest_framework import viewsets
from .models import Article, Famille, Origine, Emplacement, Inventaire, DetailInventaire
from .serializers import ArticleSerializer, DetailInventaireSerializer
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework import filters

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['designation', 'famille__nom', 'origine__nom', 'emplacement__nom']

    def create(self, request, *args, **kwargs):
        designation = request.data.get('designation')
        famille_nom = request.data.get('famille')
        origine_nom = request.data.get('origine')
        quantite = request.data.get('quantite')
        etat = request.data.get('etat', 'Bon')
        annee = request.data.get('annee', datetime.now().year)

        if not designation or not famille_nom or not origine_nom or not quantite:
            return Response({'error': 'Les champs désignation, famille, origine, et quantité doivent être remplis.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantite = int(quantite)
            if quantite <= 0:
                return Response({'error': 'La quantité doit être un nombre entier positif.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'La quantité doit être un nombre entier.'}, status=status.HTTP_400_BAD_REQUEST)

        famille, _ = Famille.objects.get_or_create(nom=famille_nom)
        origine, _ = Origine.objects.get_or_create(nom=origine_nom)
        inventaire, _ = Inventaire.objects.get_or_create(annee=annee)

        articles = []
        details_inventaire = []

        emplacement_nom = request.data.get('emplacement', 'emplacement-pas-defini')
        emplacement_nom_hyphenated = emplacement_nom.replace(' ', '-').lower()

        for i in range(1, quantite + 1):
            article_designation = f"{designation}{i}"  
            code_article = f"{designation[:4].lower()}{i}/{emplacement_nom_hyphenated}/{origine_nom.lower()}"  

            article = Article(
                designation=article_designation,
                famille=famille,
                origine=origine,
                inventaire=inventaire,
                code_article=code_article 
            )
            article.save()
            articles.append(article)

            detail = DetailInventaire(
                article=article,
                inventaire=inventaire,
                quantite=1,
                etat=etat
            )
            detail.save()
            details_inventaire.append(detail)

        created_articles = ArticleSerializer(articles, many=True).data
        created_details_inventaire = DetailInventaireSerializer(details_inventaire, many=True).data

        return Response({
            'message': f'{quantite} articles créés',
            'articles': created_articles,
            'details_inventaire': created_details_inventaire
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        article = self.get_object()
        emplacement_nom = request.data.get('emplacement')

        if emplacement_nom:
            emplacement, _ = Emplacement.objects.get_or_create(nom=emplacement_nom)
            article.emplacement = emplacement
            designation = article.designation
            origine = article.origine.nom

            emplacement_nom_hyphenated = emplacement.nom.replace(' ', '-')

            existing_articles_count = Article.objects.filter(designation=designation).count()
            new_code_number = existing_articles_count + 1
            new_code_article = f"{designation[:4].lower()}{new_code_number}/{emplacement_nom_hyphenated.lower()}/{origine.lower()}"

            article.code_article = new_code_article
            article.save()

            return Response({'message': 'Article mis à jour avec emplacement et code généré', 'article': ArticleSerializer(article).data})

        return Response({'error': 'Emplacement non fourni.'}, status=status.HTTP_400_BAD_REQUEST)
