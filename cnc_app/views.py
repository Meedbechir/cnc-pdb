from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Article, Designation, Origine, Emplacement, Inventaire, Famille, StatusArticle, DetailEntree, DetailInventaire
from .serializers import ArticleSerializer, DesignationSerializer, FamilleSerializer

class FamilleViewSet(viewsets.ModelViewSet):
    queryset = Famille.objects.all()
    serializer_class = FamilleSerializer

class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('id')
    serializer_class = ArticleSerializer

    def create(self, request, *args, **kwargs):
        designation_id = request.data.get('designation_id')
        origine_nom = request.data.get('origine')
        quantite = request.data.get('quantite')
        famille_nom = request.data.get('famille')
        annee = request.data.get('annee_inventaire', datetime.now().year)

        if not all([designation_id, origine_nom, quantite, famille_nom]) or int(quantite) < 1:
            return Response({'error': 'Tous les champs doivent être remplis, et la quantité doit être positive.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            designation = Designation.objects.get(id=designation_id)
        except Designation.DoesNotExist:
            return Response({'error': 'La désignation spécifiée n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)

        origine, _ = Origine.objects.get_or_create(nom=origine_nom)
        famille, _ = Famille.objects.get_or_create(nom=famille_nom)
        inventaire, _ = Inventaire.objects.get_or_create(annee_inventaire=annee)

        articles = self.create_articles(designation, origine, inventaire, quantite, famille)

        return Response({'message': f'{quantite} articles créés', 'articles': ArticleSerializer(articles, many=True).data}, status=status.HTTP_201_CREATED)

    def create_articles(self, designation, origine, inventaire, quantite, famille):
        articles = []
        articles_existants = Article.objects.filter(designation=designation)
        dernier_numero = self.get_dernier_numero(articles_existants)

        for i in range(1, quantite + 1):
            numero_article = dernier_numero + i
            code_article = self.generate_code_article(designation, "emplacement-pas-defini", origine.nom, numero_article)
            
            article = Article(
                designation=designation,
                famille=famille
            )
            article.save()

            emplacement, _ = Emplacement.objects.get_or_create(nom="emplacement-par-defaut")

            detail_entree = DetailEntree.objects.create(
                article=article,
                quantite_entree=1,
                origine=origine,
                emplacement=emplacement,
                code_article=code_article,
                status=StatusArticle.objects.first() 
            )

            detail_inventaire = DetailInventaire.objects.create(
                article=article,
                inventaire=inventaire,
                quantite=1,  
                status_article=StatusArticle.objects.first() 
            )

            articles.append(article)

        return articles

    def update(self, request, *args, **kwargs):
        article = self.get_object()  
        emplacement_nom = request.data.get('emplacement').replace(' ', '-')
        annee = request.data.get('annee_inventaire', datetime.now().year)

        if emplacement_nom:
            emplacement, _ = Emplacement.objects.get_or_create(nom=emplacement_nom)

            detail_entree = DetailEntree.objects.filter(article=article).first()
            origine_nom = detail_entree.origine.nom if detail_entree else "origine-inconnue"

            if detail_entree:
                existing_code_article = detail_entree.code_article.split('/')[0]  
                code_article = f"{existing_code_article}/{emplacement_nom}/{origine_nom.lower()}"
                
                detail_entree.code_article = code_article
                detail_entree.save()

                return Response({
                    'message': 'Article mis à jour avec succès.',
                    'article': ArticleSerializer(article).data,
                    'code_article': code_article 
                }, status=status.HTTP_200_OK)

        return Response({'error': 'Le nom de l\'emplacement est requis.'}, status=status.HTTP_400_BAD_REQUEST)



    def get_dernier_numero(self, articles_existants):
        if articles_existants.exists():
            return articles_existants.count() 
        return 0

    def generate_code_article(self, designation, emplacement_nom, origine_nom, numero_article):
        return f"{designation.nom[:4].lower()}{numero_article}/{emplacement_nom.lower()}/{origine_nom.lower()}"
