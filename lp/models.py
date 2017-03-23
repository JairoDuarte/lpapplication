from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from . import models as m
from .utils import Countries

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
    is_active = models.BooleanField(default=True)
    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    class Meta:
        verbose_name = 'utilisateur'
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
    def is_staff(self):
        return self.is_admin

class Settings(models.Model):
    age_max = models.PositiveSmallIntegerField('âge max.', default=25)
    age_bac_max = models.PositiveSmallIntegerField('âge max. du bac', default=4)

class BaremeAge(models.Model):
    age_max = models.PositiveSmallIntegerField('âge max.', unique=True)
    note_preselection = models.DecimalField('note de préselection', max_digits=4, decimal_places=2)
    def __str__(self):
        return 'Âge %i (Note: %g)' % (self.age_max, self.note_preselection)
    class Meta:
        verbose_name = "barème d'âge"
        verbose_name_plural = "barème d'âge"

class BaremeAnneesDiplome(models.Model):
    nb_redoublements = models.PositiveSmallIntegerField('nombre de redoublements', unique=True)
    note_preselection = models.DecimalField('note de préselection', max_digits=4, decimal_places=2)
    def __str__(self):
        return 'Années %i (Note: %g)' % (self.nb_redoublements, self.note_preselection)
    class Meta:
        verbose_name = "barème d'années de diplôme"
        verbose_name_plural = "barème d'années de diplôme"

class TypeDiplome(models.Model):
    libelle = models.CharField('libellé', max_length=100, unique=True)
    def __str__(self):
        return self.libelle
    class Meta:
        verbose_name = 'type de diplôme'
        verbose_name_plural = 'types de diplôme'

class FiliereDiplome(models.Model):
    libelle = models.CharField('libellé', max_length=100, unique=True)
    type_diplome = models.ForeignKey(TypeDiplome, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.type_diplome) + ' » ' + self.libelle
    def type_diplome_libelle(self):
        return self.type_diplome.libelle
    type_diplome_libelle.short_description = 'Type de diplôme'
    class Meta:
        verbose_name = 'filière de diplôme'
        verbose_name_plural = 'filières de diplôme'

class OptionDiplome(models.Model):
    libelle = models.CharField('libellé', max_length=100, unique=True)
    filiere_diplome = models.ForeignKey(FiliereDiplome, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.filiere_diplome) + ' » ' + self.libelle
    def type_diplome_libelle(self):
        return self.filiere_diplome.type_diplome_libelle()
    type_diplome_libelle.short_description = 'Type de diplôme'
    def filiere_diplome_libelle(self):
        return self.filiere_diplome.libelle
    filiere_diplome_libelle.short_description = 'Filière de diplôme'
    class Meta:
        verbose_name = 'option de diplôme'
        verbose_name_plural = 'options de diplôme'

class TypeBac(models.Model):
    libelle = models.CharField('libellé', max_length=100, unique=True)
    def __str__(self):
        return self.libelle
    class Meta:
        verbose_name = 'type de Bac'
        verbose_name_plural = 'types de Bac'

class MentionBac(models.Model):
    libelle = models.CharField('libellé', max_length=100, unique=True)
    note_preselection = models.DecimalField('note de préselection', max_digits=4, decimal_places=2)
    def __str__(self):
        return self.libelle
    class Meta:
        verbose_name = 'mention de Bac'
        verbose_name_plural = 'mentions de Bac'

class Filiere(models.Model):
    libelle = models.CharField('libellé', max_length=100, unique=True)
    libelle_court = models.CharField('libellé court', max_length=100, blank=True, default='')
    types_diplome = models.ManyToManyField(TypeDiplome, blank=True)
    filieres_diplome = models.ManyToManyField(FiliereDiplome, blank=True)
    options_diplome = models.ManyToManyField(OptionDiplome, blank=True)
    def __str__(self):
        return self.libelle
    class Meta:
        verbose_name = 'filière'

class Candidat(models.Model):
    NB_REDOUBLEMENTS_CHOIX = (
        (0, 'Sans redoublement'),
        (1, 'Un redoublement'),
        (2, 'Deux redoublements ou plus...'),
    )
    cin = models.CharField("code d'Identification National (CIN)", max_length=50)
    cne = models.CharField("code National d'Étudiant (CNE)", max_length=50)
    nom = models.CharField(max_length=100)
    prenom = models.CharField('prénom', max_length=100)
    nationalite = models.CharField('nationalité', max_length=100)
    ville_naissance = models.CharField('ville de naissance', max_length=100)
    pays_naissance = models.CharField('pays de naissance', max_length=100)
    date_naissance = models.DateField('date de naissance')
    email = models.CharField(max_length=80, unique=True)
    telephone_gsm = models.CharField('no. de téléphone GSM', max_length=20)
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
    filiere_diplome = models.ForeignKey(FiliereDiplome, on_delete=models.SET_NULL, null=True, blank=True)
    option_diplome = models.ForeignKey(OptionDiplome, on_delete=models.SET_NULL, null=True, blank=True)
    nb_redoublements = models.PositiveSmallIntegerField('nombre de redoublements', choices=NB_REDOUBLEMENTS_CHOIX, default=0)
    type_bac = models.ForeignKey(TypeBac, on_delete=models.SET_NULL, null=True)
    type_bac_autre = models.CharField('autre', max_length=100, blank=100)
    annee_bac = models.PositiveSmallIntegerField("année d'obtention du bac")
    mention_bac = models.ForeignKey(MentionBac, on_delete=models.SET_NULL, null=True, verbose_name='mention du Bac')
    filiere_choisie = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True, verbose_name='filière choisie')
    jeton_validation = models.CharField(max_length=32, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    note_preselection = models.DecimalField('note de préselection', max_digits=4, decimal_places=2)
    def short_cin(self):
        return self.cin
    short_cin.admin_order_field = 'cin'
    short_cin.short_description = 'CIN'
    def short_cne(self):
        return self.cne
    short_cne.admin_order_field = 'cne'
    short_cne.short_description = 'CNE'
    def short_filiere(self):
        filiere = self.filiere_choisie
        return filiere.libelle_court if len(filiere.libelle_court) != 0 else filiere.libelle
    short_filiere.admin_order_field = 'filiere_choisie'
    short_filiere.short_description = 'Filière choisie'
    def afficher_nationalite(self):
        return Countries.LIST[self.nationalite]
    def afficher_pays_naissance(self):
        return Countries.LIST[self.pays_naissance]
    def afficher_pays_residence(self):
        return Countries.LIST[self.pays_residence]
    def afficher_date_naissance(self):
        mois = [
            'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet',
            'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ]
        date = self.date_naissance
        return str(date.day) + ' ' + mois[date.month - 1] + ' ' + str(date.year)
    def afficher_telephone_fixe(self):
        if self.telephone_fixe and self.telephone_fixe != '':
            return self.telephone_fixe
        return 'Aucun'
    def afficher_annee_s1(self):
        annee = self.annee_s1
        return str(annee - 1) + '/' + str(annee)
    def afficher_annee_s2(self):
        annee = self.annee_s2
        return str(annee - 1) + '/' + str(annee)
    def afficher_annee_s3(self):
        annee = self.annee_s3
        return str(annee - 1) + '/' + str(annee)
    def afficher_annee_s4(self):
        annee = self.annee_s4
        return str(annee - 1) + '/' + str(annee)
    def afficher_nb_redoublements(self):
        labels = {
            0: 'Sans redoublement',
            1: 'Un redoublement',
            2: 'Deux redoublements ou plus...',
        }
        return labels[self.nb_redoublements]
    def afficher_type_diplome(self):
        return self.type_diplome.libelle if self.type_diplome else self.type_diplome_autre
    def afficher_filiere_diplome(self):
        return self.filiere_diplome.libelle if self.filiere_diplome else 'Aucune'
    def afficher_option_diplome(self):
        return self.option_diplome.libelle if self.option_diplome else 'Aucune'
    def afficher_type_bac(self):
        return self.type_bac.libelle if self.type_bac else self.type_bac_autre
    def afficher_annee_bac(self):
        annee = self.annee_bac
        return str(annee - 1) + '/' + str(annee)
    def afficher_mention_bac(self):
        return self.mention_bac.libelle
    def afficher_filiere_choisie(self):
        return self.filiere_choisie.libelle if self.filiere_choisie else 'Aucune'
    def age(self):
        now = timezone.now()
        born = self.date_naissance
        return now.year - born.year - ((now.month, now.day) < (born.month, born.day))
    def note_age(self):
        age = self.age()
        bareme_age_set = m.BaremeAge.objects.order_by('-age_max').all()
        note_age = bareme_age_set[len(bareme_age_set) - 1].note_preselection
        for bareme_age in bareme_age_set:
            if age >= bareme_age.age_max:
                note_age = bareme_age.note_preselection
                break
        return note_age
    def note_validation(self):
        nb_redoublements = self.nb_redoublements
        bareme_set = m.BaremeAnneesDiplome.objects.order_by('-nb_redoublements').all()
        note_validation = bareme_set[len(bareme_set) - 1].note_preselection
        for bareme_annee in bareme_set:
            if nb_redoublements >= bareme_annee.nb_redoublements:
                note_validation = bareme_annee.note_preselection
                break
        return note_validation
    def email_valide(self):
        return self.user != None
    email_valide.admin_order_field = 'user'
    email_valide.short_description = 'Email valide?'
    email_valide.boolean = True
    def __str__(self):
        return self.prenom + ' ' + self.nom
