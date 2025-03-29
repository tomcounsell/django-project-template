from django.db import migrations, models
import django.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PromptTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('template_text', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('version', models.CharField(blank=True, max_length=50)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Prompt Template',
                'verbose_name_plural': 'Prompt Templates',
                'ordering': ['-modified_at'],
            },
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('default_provider', models.CharField(max_length=100)),
                ('default_model', models.CharField(max_length=100)),
                ('default_temperature', models.FloatField(default=0.7)),
                ('max_tokens', models.IntegerField(default=4000)),
                ('system_prompt', models.TextField()),
                ('context_instructions', models.TextField(blank=True)),
                ('additional_context', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'AI Agent',
                'verbose_name_plural': 'AI Agents',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='AICompletion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('prompt_input', models.TextField()),
                ('prompt_variables', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('context_text', models.TextField(blank=True)),
                ('completion_text', models.TextField()),
                ('provider', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('temperature', models.FloatField(blank=True, null=True)),
                ('usage_tokens', models.IntegerField(default=0)),
                ('usage_cost', models.DecimalField(decimal_places=6, default=0, max_digits=10)),
                ('is_flagged', models.BooleanField(default=False)),
                ('flag_reason', models.CharField(blank=True, max_length=255)),
                ('prompt_template', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='completions', to='ai.prompttemplate')),
            ],
            options={
                'verbose_name': 'AI Completion',
                'verbose_name_plural': 'AI Completions',
                'ordering': ['-created_at'],
            },
        ),
    ]