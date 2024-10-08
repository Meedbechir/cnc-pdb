from django.db import models
from datetime import datetime

class Inventaire(models.Model):
    annee = models.IntegerField(default=datetime.now().year, unique=True)

    def __str__(self):
        return str(self.annee)

class Famille(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom

class Origine(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom

class Emplacement(models.Model):
    nom = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nom

class Article(models.Model):
    designation = models.CharField(max_length=255)
    famille = models.ForeignKey(Famille, on_delete=models.CASCADE)
    origine = models.ForeignKey(Origine, on_delete=models.CASCADE)
    emplacement = models.ForeignKey(Emplacement, on_delete=models.CASCADE, blank=True, null=True)
    code_article = models.CharField(max_length=50, unique=True, blank=True, null=True)
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE, default=2024) 

    def __str__(self):
        return self.designation

class DetailInventaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    etat = models.CharField(max_length=50, default='Moyen')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.article.designation} - {self.date}"
