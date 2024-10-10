from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Article, Designation, Origine, Emplacement, Inventaire, DetailInventaire, Famille
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
    queryset = Article.objects.all().order_by('id')
    serializer_class = ArticleSerializer

    valid_familles = [
        'materiel_informatique',
        'materiel_bureautique',
        'materiel_medical',
        'materiel_transport',
        'equipement_medical',
        'autre_materiel_technique',
    ]

    def create(self, request, *args, **kwargs):
        designation_id = request.data.get('designation_id')
        origine_nom = request.data.get('origine')
        quantite = request.data.get('quantite')
        famille_nom = request.data.get('famille')
        annee = request.data.get('annee', datetime.now().year)

        # Validation des champs requis
        if not all([designation_id, origine_nom, quantite, famille_nom]) or quantite < 1:
            return Response({'error': 'Les champs désignation, origine, famille, et quantité doivent être remplis, et la quantité doit être positive.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            designation = Designation.objects.get(id=designation_id)
        except Designation.DoesNotExist:
            return Response({'error': 'La désignation spécifiée n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)

        origine, _ = Origine.objects.get_or_create(nom=origine_nom)

        # Créer ou obtenir la famille
        famille, _ = Famille.objects.get_or_create(nom=famille_nom)

        inventaire, _ = Inventaire.objects.get_or_create(annee=annee)

        articles = self.create_articles(designation, origine, inventaire, quantite, famille)

        return Response({'message': f'{quantite} articles créés', 'articles': ArticleSerializer(articles, many=True).data}, status=status.HTTP_201_CREATED)

    def create_articles(self, designation, origine, inventaire, quantite, famille):
        articles = []
        articles_existants = Article.objects.filter(designation=designation)

        dernier_numero = self.get_dernier_numero(articles_existants, designation)

        for i in range(1, quantite + 1):
            code_article = self.generate_code_article(designation, origine, dernier_numero + i)

            article = Article(
                designation=designation,
                origine=origine,
                inventaire=inventaire,
                code_article=code_article,
                famille=famille  # Utiliser l'instance de famille ici
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


    

    def update(self, request, *args, **kwargs):
        article = self.get_object()
        emplacement_nom = request.data.get('emplacement')

        if not emplacement_nom:
            return Response({'error': 'L\'emplacement ne peut pas être vide.'}, status=status.HTTP_400_BAD_REQUEST)

        emplacement, _ = Emplacement.objects.get_or_create(nom=emplacement_nom)

        article.emplacement = emplacement

        numero_article = int(article.code_article.split('/')[0][len(article.designation.nom[:4].lower()):])

        article.code_article = self.generate_code_article(article.designation, article.origine, numero_article, emplacement.nom)

        article.save()

        return Response(ArticleSerializer(article).data, status=status.HTTP_200_OK)

    def get_dernier_numero(self, articles_existants, designation):
        if articles_existants.exists():
            dernier_article = articles_existants.order_by('-code_article').first()
            dernier_code_article = dernier_article.code_article.split('/')[0]
            return int(dernier_code_article[len(designation.nom[:4].lower()):])
        return 0

    def generate_code_article(self, designation, origine, numero_article, emplacement_nom=None):
        emplacement_part = emplacement_nom.replace(' ', '-') if emplacement_nom else "emplacement-pas-defini"
        origine_part = origine.nom.replace(' ', '-').lower() 

        code_article = f"{designation.nom[:4].lower()}{numero_article}/{emplacement_part.lower()}/{origine_part}"

        while Article.objects.filter(code_article=code_article).exists():
            numero_article += 1 
            code_article = f"{designation.nom[:4].lower()}{numero_article}/{emplacement_part}/{origine_part}"

        return code_article
