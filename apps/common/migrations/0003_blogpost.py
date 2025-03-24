# Generated manually for demo purposes

import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blogposts', to='common.user')),
                ('is_author_anonymous', models.BooleanField(default=False)),
                ('authored_at', models.DateTimeField(auto_now_add=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('edited_at', models.DateTimeField(blank=True, null=True)),
                ('unpublished_at', models.DateTimeField(blank=True, null=True)),
                ('valid_at', models.DateTimeField(blank=True, null=True)),
                ('expired_at', models.DateTimeField(blank=True, null=True)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.address')),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True, validators=[django.core.validators.validate_slug])),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('subtitle', models.CharField(blank=True, default='', max_length=255)),
                ('content', models.TextField()),
                ('featured_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='featured_blog_posts', to='common.image')),
                ('reading_time_minutes', models.PositiveIntegerField(default=3)),
                ('tags', models.CharField(blank=True, default='', max_length=255)),
                ('notes', models.ManyToManyField(to='common.note')),
            ],
            options={
                'verbose_name': 'Blog Post',
                'verbose_name_plural': 'Blog Posts',
                'ordering': ['-published_at', '-created_at'],
            },
        ),
    ]