# Generated by Django 3.1.7 on 2021-09-13 16:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('user_description', models.CharField(blank=True, max_length=500, null=True)),
                ('nft_profile_link', models.CharField(blank=True, max_length=100, null=True)),
                ('behance_profile_link', models.CharField(blank=True, max_length=100, null=True)),
                ('instagram_profile_link', models.CharField(blank=True, max_length=100, null=True)),
                ('twitter_profile_link', models.CharField(blank=True, max_length=100, null=True)),
                ('facebook_profile_link', models.CharField(blank=True, max_length=100, null=True)),
                ('telegram_profile_link', models.CharField(blank=True, max_length=100, null=True)),
                ('number_of_user_subscribers', models.CharField(blank=True, max_length=100, null=True)),
                ('user_online_status', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='users')),
                ('time_zone', models.CharField(default='UTC', max_length=200)),
                ('default_currency', models.CharField(default='USD', max_length=10)),
                ('currency_symbol', models.CharField(default='$', max_length=10)),
                ('terms_of_use', models.BooleanField(default=True)),
                ('privacy_policy', models.BooleanField(default=True)),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('stripe_id', models.CharField(blank=True, max_length=200, null=True)),
                ('login_code', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_method', models.CharField(blank=True, max_length=400, null=True)),
                ('subscribed', models.BooleanField(default=False)),
                ('subscription_msg', models.TextField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('recommended_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ref_by', to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuthCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Cookies_Policy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cookies_content', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Privacy_Policy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('privacy_content', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.TextField(blank=True, null=True)),
                ('source', models.CharField(blank=True, max_length=500, null=True)),
                ('ip_address', models.CharField(max_length=500)),
                ('location', models.CharField(max_length=500)),
                ('when', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='API_KEY',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_key', models.CharField(max_length=500, unique=True)),
                ('secret_key', models.CharField(max_length=500, unique=True)),
                ('exchange', models.CharField(max_length=500)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AllLogin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('browser', models.CharField(max_length=500)),
                ('ip_address', models.CharField(max_length=500)),
                ('near', models.CharField(max_length=500)),
                ('signed_in', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
