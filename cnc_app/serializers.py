from rest_framework import serializers
from .models import Article, Famille, DetailInventaire, Designation

class DesignationSerializer(serializers.ModelSerializer):
    famille = serializers.CharField(max_length=50)

    class Meta:
        model = Designation
        fields = ['id', 'nom', 'famille']

    def create(self, validated_data):
        famille_nom = validated_data.pop('famille')
        famille, _ = Famille.objects.get_or_create(nom=famille_nom)
        return Designation.objects.create(famille=famille, **validated_data)


class DetailInventaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailInventaire
        fields = ['id', 'quantite', 'etat', 'article', 'inventaire', 'date']


class ArticleSerializer(serializers.ModelSerializer):
    famille_nom = serializers.CharField(source='designation.famille.nom', read_only=True)
    origine_nom = serializers.CharField(source='origine.nom', read_only=True)
    emplacement_nom = serializers.CharField(source='emplacement.nom', read_only=True)
    etat = serializers.SerializerMethodField()
    date_ajout = serializers.SerializerMethodField()
    designation_nom = serializers.CharField(source='designation.nom', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'designation_nom', 'famille_nom', 'origine_nom', 'emplacement_nom', 'code_article', 'inventaire', 'etat', 'date_ajout']

    def get_etat(self, obj):
        etat = DetailInventaire.objects.filter(article=obj).values_list('etat', flat=True).first()
        return etat or 'Non défini'

    def get_date_ajout(self, obj):
        date_ajout = DetailInventaire.objects.filter(article=obj).values_list('date', flat=True).first()
        return date_ajout or 'Non défini'
