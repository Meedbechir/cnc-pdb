from rest_framework import serializers
from .models import Article, DetailInventaire, Designation, StatusArticle, DetailEntree, Famille


class FamilleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Famille
        fields = ['id', 'nom']

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'nom']

class StatusArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusArticle
        fields = ['id', 'status_article']


class DetailInventaireSerializer(serializers.ModelSerializer):
    status_article = StatusArticleSerializer() 

    class Meta:
        model = DetailInventaire
        fields = ['id', 'article', 'inventaire', 'quantite', 'status_article']

class DetailEntreeSerializer(serializers.ModelSerializer):
    status = StatusArticleSerializer()  

    class Meta:
        model = DetailEntree
        fields = ['id', 'article', 'quantite_entree', 'origine', 'emplacement', 'code_article', 'status']
        
class ArticleSerializer(serializers.ModelSerializer):
    famille_nom = serializers.CharField(source='famille.nom', read_only=True)
    designation_nom = serializers.CharField(source='designation.nom', read_only=True)
    details_entree = DetailEntreeSerializer(many=True, source='detailentree_set', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'designation', 'designation_nom', 'famille', 'famille_nom', 'details_entree']

