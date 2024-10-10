from rest_framework import serializers
from .models import Article, Famille, DetailInventaire, Designation

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'nom'] 

class DetailInventaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailInventaire
        fields = ['id', 'quantite', 'etat', 'article', 'inventaire', 'date']

class ArticleSerializer(serializers.ModelSerializer):
    famille = serializers.ChoiceField(choices=[ 
        ('materiel_informatique', 'Matériel Informatique'),
        ('materiel_bureautique', 'Matériel Bureautique'),
        ('materiel_medical', 'Matériel Médical'),
        ('materiel_transport', 'Matériel Transport'),
        ('equipement_medical', 'Équipement Médical'),
        ('autre_materiel_technique', 'Autre Matériel Technique'),
    ], write_only=True)

    famille_nom = serializers.CharField(source='famille', read_only=True)
    origine_nom = serializers.CharField(source='origine.nom', read_only=True)
    emplacement_nom = serializers.CharField(source='emplacement.nom', read_only=True)
    etat = serializers.SerializerMethodField()
    date_ajout = serializers.SerializerMethodField()
    designation_nom = serializers.CharField(source='designation.nom', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'designation_nom', 'famille_nom', 'origine_nom', 'emplacement_nom', 'code_article', 'inventaire', 'etat', 'date_ajout', 'famille']

    def get_etat(self, obj):
        etat = DetailInventaire.objects.filter(article=obj).values_list('etat', flat=True).first()
        return etat or 'Non défini'

    def get_date_ajout(self, obj):
        date_ajout = DetailInventaire.objects.filter(article=obj).values_list('date', flat=True).first()
        return date_ajout or 'Non défini'
