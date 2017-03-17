# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-16 15:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lp', '0002_auto_20170316_1436'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaremeAge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age_max', models.PositiveSmallIntegerField(unique=True, verbose_name='age max.')),
                ('note_preselection', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='BaremeAnnesDiplome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annees_max', models.PositiveSmallIntegerField(unique=True, verbose_name='années diplome max.')),
                ('note_preselection', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='Candidat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cin', models.CharField(max_length=50, unique=True, verbose_name="code d'identification national (CIN)")),
                ('cne', models.CharField(max_length=50, unique=True, verbose_name="code national d'étudiant (CNE)")),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100, verbose_name='prénom')),
                ('nationalite', models.CharField(max_length=100, verbose_name='nationalité')),
                ('ville_naissance', models.CharField(max_length=100, verbose_name='ville de naissance')),
                ('pays_naissance', models.CharField(max_length=100, verbose_name='pays de naissance')),
                ('date_naissance', models.DateField(verbose_name='date de naissance')),
                ('email', models.CharField(max_length=80, unique=True)),
                ('telephone_gsm', models.CharField(max_length=20, unique=True, verbose_name='no. téléphone GSM')),
                ('telephone_fixe', models.CharField(blank=True, max_length=20, verbose_name='no. téléphone fixe')),
                ('adresse_residence', models.CharField(max_length=255, verbose_name='adresse de résidence')),
                ('ville_residence', models.CharField(max_length=100, verbose_name='ville de résidence')),
                ('pays_residence', models.CharField(max_length=100, verbose_name='pays de résidence')),
                ('note_s1', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='note S1')),
                ('annee_s1', models.PositiveSmallIntegerField(verbose_name='année S1')),
                ('note_s2', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='note S2')),
                ('annee_s2', models.PositiveSmallIntegerField(verbose_name='année S2')),
                ('note_a1', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='note de la première année')),
                ('note_s3', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='note S3')),
                ('annee_s3', models.PositiveSmallIntegerField(verbose_name='année S3')),
                ('note_s4', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='note S4')),
                ('annee_s4', models.PositiveSmallIntegerField(verbose_name='année S4')),
                ('note_a2', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='note de la deuxième année')),
                ('type_diplome_autre', models.CharField(blank=True, max_length=100, verbose_name='autre')),
                ('type_bac_autre', models.CharField(blank=100, max_length=100, verbose_name='autre')),
                ('annee_bac', models.PositiveSmallIntegerField(verbose_name="année d'obtention du bac")),
                ('jeton_validation', models.CharField(max_length=16, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Filiere',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='FiliereDiplome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MentionBac',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=100, unique=True)),
                ('note_preselection', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='OptionDiplome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=100, unique=True)),
                ('filiere_dipolme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lp.FiliereDiplome')),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TypeBac',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TypeDiplome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='filierediplome',
            name='type_diplome',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lp.TypeDiplome'),
        ),
        migrations.AddField(
            model_name='candidat',
            name='filiere_choisie',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lp.Filiere'),
        ),
        migrations.AddField(
            model_name='candidat',
            name='filiere_diplome',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lp.FiliereDiplome'),
        ),
        migrations.AddField(
            model_name='candidat',
            name='mention_bac',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lp.MentionBac'),
        ),
        migrations.AddField(
            model_name='candidat',
            name='option_diplome',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lp.OptionDiplome'),
        ),
        migrations.AddField(
            model_name='candidat',
            name='type_bac',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lp.TypeBac'),
        ),
        migrations.AddField(
            model_name='candidat',
            name='type_diplome',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lp.TypeDiplome'),
        ),
        migrations.AddField(
            model_name='candidat',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lp.User'),
        ),
    ]