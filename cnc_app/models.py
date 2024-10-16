from django.db import models

class Inventaire(models.Model):
    annee_inventaire = models.IntegerField(default=2024,unique=True) 

    def __str__(self):
        return str(self.annee_inventaire)

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

class Designation(models.Model):
    nom = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nom

class StatusArticle(models.Model):
    status_article = models.CharField(max_length=50) 

    def __str__(self):
        return self.status_article

class Article(models.Model):
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    famille = models.ForeignKey(Famille, on_delete=models.CASCADE)

    def __str__(self):
        return self.designation.nom

class DetailInventaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    status_article = models.ForeignKey(StatusArticle, on_delete=models.CASCADE, default=1)
    
    def __str__(self):
        return f"{self.article.designation.nom} - {self.inventaire} - {self.quantite}"

class DetailEntree(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite_entree = models.IntegerField()
    origine = models.ForeignKey(Origine, on_delete=models.CASCADE)
    emplacement = models.ForeignKey(Emplacement, on_delete=models.CASCADE)
    code_article = models.CharField(max_length=50, blank=True, null=True)
    status = models.ForeignKey(StatusArticle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.article.designation.nom} - {self.quantite_entree} - {self.origine.nom}"
