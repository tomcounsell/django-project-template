# apps/insights/admin.py
from django.contrib import admin
from .models.summary import Summary, KeyMetric
from .models.comparison import Comparison, KeyMetricComparison

# Registering all models without custom admin configurations
admin.site.register(Summary)
admin.site.register(KeyMetric)
admin.site.register(Comparison)
admin.site.register(KeyMetricComparison)
