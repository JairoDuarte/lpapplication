from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Créé et enregistre un utilisateur avec un email et un mot de passe
        """
        if not email:
            raise ValueError('Un utilisateur doit avoir une addresse email')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Créé et enregistre un administrateur avec un email et un mot de passe
        """
        if not email:
            raise ValueError('Un administrateur doit avoir une addresse email')

        user = self.create_user(email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.CharField(max_length=100, unique=True)
    is_admin = models.BooleanField(default=False)
    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    def get_full_name(self):
        return self.email
    def get_short_name(self):
        return self.email
    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        # Won't be asking for permission for anything not admin related
        return self.is_admin
    def has_module_perms(self, app_label):
        # Won't be asking for permission for anything not admin related
        return self.is_admin
    @property
    def is_active(self):
        return True
    @property
    def is_staff(self):
        return self.is_admin

class Settings(models.Model):
    age_max = models.PositiveSmallIntegerField('age max.', default=25)
    age_bac_max = models.PositiveSmallIntegerField('age max. du bac', default=4)

class BaremeAge(models.Model):
    age_max = models.PositiveSmallIntegerField('age max.', unique=True)
    note_preselection = models.DecimalField(max_digits=4, decimal_places=2)

class BaremeAnneesDiplome(models.Model):
    annees_max = models.PositiveSmallIntegerField('années diplome max.', unique=True)
    note_preselection = models.DecimalField(max_digits=4, decimal_places=2)

class TypeDiplome(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.libelle

class FiliereDiplome(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    type_diplome = models.ForeignKey(TypeDiplome, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.type_diplome) + ' » ' + self.libelle

class OptionDiplome(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    filiere_diplome = models.ForeignKey(FiliereDiplome, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.filiere_diplome) + ' » ' + self.libelle

class TypeBac(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.libelle

class MentionBac(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    note_preselection = models.DecimalField(max_digits=4, decimal_places=2)
    def __str__(self):
        return self.libelle

class Filiere(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    types_diplome = models.ManyToManyField(TypeDiplome, blank=True)
    filieres_diplome = models.ManyToManyField(FiliereDiplome, blank=True)
    options_diplome = models.ManyToManyField(OptionDiplome, blank=True)
    def __str__(self):
        return self.libelle

class Candidat(models.Model):
    cin = models.CharField("code d'Identification National (CIN)", max_length=50, unique=True)
    cne = models.CharField("code National d'Étudiant (CNE)", max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField('prénom', max_length=100)
    nationalite = models.CharField('nationalité', max_length=100)
    ville_naissance = models.CharField('ville de naissance', max_length=100)
    pays_naissance = models.CharField('pays de naissance', max_length=100)
    date_naissance = models.DateField('date de naissance')
    email = models.CharField(max_length=80, unique=True)
    telephone_gsm = models.CharField('no. de téléphone GSM', max_length=20, unique=True)
    telephone_fixe = models.CharField('no. de téléphone fixe', max_length=20, blank=True)
    adresse_residence = models.CharField('adresse de résidence', max_length=255)
    ville_residence = models.CharField('ville de résidence', max_length=100)
    pays_residence = models.CharField('pays de résidence', max_length=100)
    note_s1 = models.DecimalField('note S1', max_digits=4, decimal_places=2, null=True, blank=True)
    annee_s1 = models.PositiveSmallIntegerField('année S1')
    note_s2 = models.DecimalField('note S2', max_digits=4, decimal_places=2, null=True, blank=True)
    annee_s2 = models.PositiveSmallIntegerField('année S2')
    note_a1 = models.DecimalField('note de la première année', max_digits=4, decimal_places=2)
    note_s3 = models.DecimalField('note S3', max_digits=4, decimal_places=2, null=True, blank=True)
    annee_s3 = models.PositiveSmallIntegerField('année S3')
    note_s4 = models.DecimalField('note S4', max_digits=4, decimal_places=2, null=True, blank=True)
    annee_s4 = models.PositiveSmallIntegerField('année S4')
    note_a2 = models.DecimalField('note de la deuxième année', max_digits=4, decimal_places=2)
    type_diplome = models.ForeignKey(TypeDiplome, on_delete=models.SET_NULL, null=True)
    type_diplome_autre = models.CharField('autre', max_length=100, blank=True)
    filiere_diplome = models.ForeignKey(FiliereDiplome, on_delete=models.SET_NULL, null=True)
    option_diplome = models.ForeignKey(OptionDiplome, on_delete=models.SET_NULL, null=True)
    type_bac = models.ForeignKey(TypeBac, on_delete=models.SET_NULL, null=True)
    type_bac_autre = models.CharField('autre', max_length=100, blank=100)
    annee_bac = models.PositiveSmallIntegerField("année d'obtention du bac")
    mention_bac = models.ForeignKey(MentionBac, on_delete=models.SET_NULL, null=True)
    filiere_choisie = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True)
    jeton_validation = models.CharField(max_length=16, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def note_preselection(self):
        """
        Retourne la note calculée de préselection
        TODO: FIXER les baremes
        """
        return 0.25 * self.note_a1 + 0.25 * self.note_a2 + 0.15 * self.mention_bac.note_preselection * 0.15 * 20 + 0.20 * 20
    def age(self):
        """
        Retourne l'age actuel du candidat
        """
        now = timezone.now()
        born = self.date_naissance
        return now.year - born.year - ((now.month, now.day) < (born.month, born.day))
    def __str__(self):
        return self.prenom + ' ' + self.nom
