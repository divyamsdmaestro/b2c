# Generated by Django 4.0.10 on 2024-07-09 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learning', '0001_initial'),
        ('forums', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='zone',
            name='categories',
            field=models.ManyToManyField(blank=True, to='learning.category'),
        ),
        migrations.AddField(
            model_name='zone',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='zone',
            name='forums',
            field=models.ManyToManyField(blank=True, to='forums.forum'),
        ),
        migrations.AddField(
            model_name='zone',
            name='image',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forums.zoneimage'),
        ),
        migrations.AddField(
            model_name='zone',
            name='skills',
            field=models.ManyToManyField(blank=True, to='learning.skill'),
        ),
        migrations.AddField(
            model_name='zone',
            name='zone_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forums.zonetype'),
        ),
        migrations.AddField(
            model_name='subjectivepostimage',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='posttype',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postreport',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postreport',
            name='post',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forums.post'),
        ),
        migrations.AddField(
            model_name='postreply',
            name='comment',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forums.postcomment'),
        ),
        migrations.AddField(
            model_name='postreply',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postpolloptionclick',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postpolloptionclick',
            name='poll_option',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clicks', to='forums.postpolloption'),
        ),
        migrations.AddField(
            model_name='postpolloptionclick',
            name='post',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='poll_option_clicks', to='forums.post'),
        ),
        migrations.AddField(
            model_name='postpolloption',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postlike',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postlike',
            name='post',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='likes', to='forums.post'),
        ),
        migrations.AddField(
            model_name='postimage',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='post',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='forums.post'),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='replies',
            field=models.ManyToManyField(blank=True, to='forums.postreply'),
        ),
        migrations.AddField(
            model_name='post',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='post',
            name='forum',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forums.forum'),
        ),
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forums.postimage'),
        ),
        migrations.AddField(
            model_name='post',
            name='poll_options',
            field=models.ManyToManyField(blank=True, to='forums.postpolloption'),
        ),
        migrations.AddField(
            model_name='post',
            name='post_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forums.posttype'),
        ),
        migrations.AddField(
            model_name='post',
            name='subjective_image',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forums.subjectivepostimage'),
        ),
        migrations.AddField(
            model_name='forumimage',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='forum',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='forum',
            name='image',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forums.forumimage'),
        ),
    ]
