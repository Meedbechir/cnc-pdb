from rest_framework import serializers
from .models import Article, Famille, Origine, Emplacement, Inventaire, DetailInventaire

class DetailInventaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailInventaire
        fields = ['id', 'quantite', 'etat', 'article', 'inventaire', 'date']

class ArticleSerializer(serializers.ModelSerializer):
    famille_name = serializers.SerializerMethodField()
    origine_name = serializers.SerializerMethodField()
    etat = serializers.SerializerMethodField()
    emplacement_name = serializers.SerializerMethodField()
    date_ajout = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'designation', 'famille_name', 'origine_name', 'emplacement_name', 'code_article', 'inventaire', 'etat', 'date_ajout']
        
    def get_famille_name(self, obj):
        return obj.famille.nom 
    
    def get_origine_name(self, obj):
        return obj.origine.nom 
    
    def get_emplacement_name(self, obj):  
        return obj.emplacement.nom if obj.emplacement else None

    def get_etat(self, obj):
        return DetailInventaire.objects.filter(article=obj).values_list('etat', flat=True).first()
    
    def get_date_ajout(self, obj):
        return DetailInventaire.objects.filter(article=obj).values_list('date', flat=True).first()

    
