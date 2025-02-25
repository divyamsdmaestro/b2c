# Generated by Django 4.0.10 on 2024-07-09 11:42

import apps.common.helpers
import apps.common.model_fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('idp_user_id', models.UUIDField(unique=True)),
                ('full_name', models.CharField(max_length=512)),
                ('socail_oauth', models.BooleanField(default=False)),
                ('social_provider', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('status', models.CharField(choices=[('active', 'active'), ('inactive', 'inactive')], default='active', max_length=512)),
                ('user_name', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('idp_email', models.EmailField(blank=True, default=None, max_length=254, null=True)),
                ('alternative_email', models.EmailField(blank=True, default=None, max_length=254, null=True)),
                ('phone_number', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('enable_education', models.BooleanField(default=False)),
                ('enable_address', models.BooleanField(default=False)),
                ('enable_profile_picture', models.BooleanField(default=False)),
                ('enable_social_handles', models.BooleanField(default=False)),
                ('enable_pause_notification', models.BooleanField(default=False)),
                ('enable_font_style', models.BooleanField(default=False)),
                ('enable_autoplay_video', models.BooleanField(default=False)),
                ('current_reward_points', models.IntegerField(default=0)),
                ('total_reward_points', models.IntegerField(default=0)),
                ('used_reward_points', models.IntegerField(default=0)),
                ('first_name', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('middle_name', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('last_name', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('admission_id', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('birth_date', models.DateField(blank=True, default=None, null=True)),
                ('identification_number', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('address', models.TextField(blank=True, default=None, null=True)),
                ('pincode', models.PositiveIntegerField(blank=True, default=None, null=True, validators=[apps.common.helpers.validate_pincode])),
                ('job_role', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('experience_years', models.PositiveIntegerField(blank=True, default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmployerDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('identity', models.CharField(max_length=512)),
                ('description', models.TextField()),
                ('contact_email_id', models.EmailField(blank=True, default=None, max_length=254, null=True)),
                ('alternative_conatct_email_id', models.EmailField(blank=True, default=None, max_length=254, null=True)),
                ('contact_number', models.CharField(max_length=512)),
                ('locality_street_address', models.TextField(blank=True, default=None, null=True)),
                ('pincode', models.PositiveIntegerField(blank=True, default=None, null=True, validators=[apps.common.helpers.validate_pincode])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmployerLogoImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('file', apps.common.model_fields.AppSingleFileField(max_length=512, upload_to='files/employer_logo/image/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GuestUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstitutionBannerImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('file', apps.common.model_fields.AppSingleFileField(max_length=512, upload_to='files/institution_banner/image/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstitutionDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('identity', models.CharField(max_length=512)),
                ('contact_email_id', models.EmailField(blank=True, default=None, max_length=254, null=True)),
                ('alternative_conatct_email_id', models.EmailField(blank=True, default=None, max_length=254, null=True)),
                ('contact_number', models.CharField(max_length=512)),
                ('locality_street_address', models.TextField(blank=True, default=None, null=True)),
                ('pincode', models.PositiveIntegerField(blank=True, default=None, null=True, validators=[apps.common.helpers.validate_pincode])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstitutionUserGroupContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('identity', models.CharField(max_length=512)),
                ('description', models.TextField()),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstitutionUserGroupDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('identity', models.CharField(max_length=512)),
                ('description', models.TextField()),
                ('status', models.BooleanField(default=True)),
                ('admin_created', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('institution', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='access.institutiondetail')),
                ('user', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('identity', models.CharField(max_length=512)),
                ('description', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReportFilterParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('identity', models.CharField(max_length=512)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('to_create', models.BooleanField(default=False)),
                ('to_view', models.BooleanField(default=False)),
                ('to_edit', models.BooleanField(default=False)),
                ('to_delete', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('permission', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='access.permission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('identity', models.CharField(max_length=512)),
                ('description', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('role_permissions', models.ManyToManyField(to='access.rolepermission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StudentReportFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('file', apps.common.model_fields.AppSingleFileField(max_length=512, upload_to='files/student/report/')),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StudentReportDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('identity', models.CharField(max_length=512)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('content_group', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='access.institutionusergroupcontent')),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('filter_parameters', models.ManyToManyField(blank=True, to='access.reportfilterparameter')),
                ('report', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='access.studentreportfile')),
                ('user_group', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='access.institutionusergroupdetail')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PermissionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('identity', models.CharField(max_length=512)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('permissions', models.ManyToManyField(to='access.permission')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
