# Generated by Django 4.0.10 on 2024-07-09 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learning', '0001_initial'),
        ('meta', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blendedlearningpathscheduledetails',
            name='address',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.blpaddress'),
        ),
        migrations.AddField(
            model_name='blendedlearningpathscheduledetails',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blendedlearningpathscheduledetails',
            name='mode',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='learning.blendedlearningpathcoursemode'),
        ),
        migrations.AddField(
            model_name='blendedlearningpathpricedetails',
            name='blended_learning',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning.blendedlearningpath'),
        ),
        migrations.AddField(
            model_name='blendedlearningpathpricedetails',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blendedlearningpathpricedetails',
            name='mode',
            field=models.ManyToManyField(blank=True, to='learning.blendedlearningpathcoursemode'),
        ),
        migrations.AddField(
            model_name='blendedlearningpathpricedetails',
            name='schedule_details',
            field=models.ManyToManyField(blank=True, to='learning.blendedlearningpathscheduledetails'),
        ),
        migrations.AddField(
            model_name='blendedlearningpathlevel',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blendedlearningpathlearningtype',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blendedlearningpathimage',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blendedlearningpathcustomerenquiry',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blendedlearningpathcustomerenquiry',
            name='mode',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='learning.blendedlearningpathcoursemode'),
        ),
        migrations.AddField(
            model_name='blendedlearningpathcoursemodesandfee',
            name='blended_learning',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_blended_learning_path_courses', to='learning.blendedlearningpath'),
        ),
        migrations.AddField(
            model_name='blendedlearningpathcoursemodesandfee',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_blended_learning_path_courses', to='learning.course'),
        ),
        migrations.AddField(
            model_name='blendedlearningpathcoursemodesandfee',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blendedlearningpathcoursemodesandfee',
            name='mode_details',
            field=models.ManyToManyField(to='learning.blendedlearningpathcoursemode'),
        ),
        migrations.AddField(
            model_name='blendedlearningpathcoursemode',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blendedlearningpath',
            name='accreditation',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='learning.accreditation'),
        ),
        migrations.AddField(
            model_name='blendedlearningpath',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blendedlearningpath',
            name='image',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='learning.blendedlearningpathimage'),
        ),
        migrations.AddField(
            model_name='blendedlearningpath',
            name='language',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='learning.language'),
        ),
        migrations.AddField(
            model_name='blendedlearningpath',
            name='learning_path_category',
            field=models.ManyToManyField(blank=True, to='learning.category'),
        ),
        migrations.AddField(
            model_name='blendedlearningpath',
            name='learning_path_level',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='learning.courselevel'),
        ),
        migrations.AddField(
            model_name='blendedlearningpath',
            name='learning_role',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='learning.learningrole'),
        ),
        migrations.AddField(
            model_name='blendedlearningpath',
            name='learning_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='learning.blendedlearningpathlearningtype'),
        ),
        migrations.AddField(
            model_name='blendedlearningpath',
            name='mode_details',
            field=models.ManyToManyField(to='learning.blendedlearningpathcoursemode'),
        ),
        migrations.AddField(
            model_name='blendedlearningpath',
            name='skills',
            field=models.ManyToManyField(blank=True, to='learning.skill'),
        ),
        migrations.AddField(
            model_name='blendedlearningclassroomandvirtualdetails',
            name='blended_learning',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning.blendedlearningpath'),
        ),
        migrations.AddField(
            model_name='blendedlearningclassroomandvirtualdetails',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning.course'),
        ),
        migrations.AddField(
            model_name='blendedlearningclassroomandvirtualdetails',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='authorimage',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='author',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='author',
            name='image',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='learning.authorimage'),
        ),
        migrations.AddField(
            model_name='author',
            name='vendor',
            field=models.ManyToManyField(blank=True, related_name='related_vendors', to='learning.vendor'),
        ),
        migrations.AddField(
            model_name='accreditation',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
    ]
