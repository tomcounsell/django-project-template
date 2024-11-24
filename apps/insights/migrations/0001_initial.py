# Generated by Django 5.1.3 on 2024-11-24 15:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateField(help_text='Start date of the data period.')),
                ('end_date', models.DateField(help_text='End date of the data period.')),
                ('dataset_summary', models.TextField(help_text='A concise English summary of the dataset.')),
                ('data_source', models.CharField(blank=True, help_text='File path or identifier of the data source.', max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': 'Summaries',
                'ordering': ['-start_date'],
                'unique_together': {('start_date', 'end_date')},
            },
        ),
        migrations.CreateModel(
            name='Comparison',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('comparison_summary', models.TextField(help_text='A concise summary of differences and similarities between the two summaries.')),
                ('start_date', models.DateField(editable=False, help_text='Start date of the comparison, derived from summary1.')),
                ('end_date', models.DateField(editable=False, help_text='End date of the comparison, derived from summary2.')),
                ('summary1', models.ForeignKey(help_text='The first summary being compared.', on_delete=django.db.models.deletion.CASCADE, related_name='comparisons_as_summary1', to='insights.summary')),
                ('summary2', models.ForeignKey(help_text='The second summary being compared.', on_delete=django.db.models.deletion.CASCADE, related_name='comparisons_as_summary2', to='insights.summary')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('summary1', 'summary2')},
            },
        ),
        migrations.CreateModel(
            name='KeyMetricComparison',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Name of the metric being compared.', max_length=100)),
                ('value1', models.FloatField(help_text='Value from the first summary.')),
                ('value2', models.FloatField(help_text='Value from the second summary.')),
                ('description', models.TextField(blank=True, help_text='Description of the observed difference or trend.', null=True)),
                ('percentage_difference', models.FloatField(blank=True, help_text='Percentage difference between the two values.', null=True)),
                ('comparison', models.ForeignKey(help_text='The comparison this key metric comparison belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='key_metrics_comparison', to='insights.comparison')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('comparison', 'name')},
            },
        ),
        migrations.CreateModel(
            name='KeyMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Name of the metric.', max_length=100)),
                ('value', models.FloatField(help_text='Numeric value of the metric.')),
                ('summary', models.ForeignKey(help_text='The summary this key metric belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='key_metrics', to='insights.summary')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('summary', 'name')},
            },
        ),
    ]
