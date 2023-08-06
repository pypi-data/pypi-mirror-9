from django.db import models

class PluginConfiguration(models.Model):
    name         = models.CharField(max_length=100)
    verbose_name = models.CharField(max_length=200, blank=True, null=True)
    plugin_type  = models.CharField(max_length=200)
    order        = models.IntegerField(default=-1)
    options      = models.TextField(default="{}")
    enabled      = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.order == -1:
            max_ordered_plugin = PluginConfiguration.objects.filter(plugin_type=self.plugin_type).order_by('order').first()
            self.order         = max_ordered_plugin.order + 1 if (max_ordered_plugin and max_ordered_plugin.order != -1) else 0

        super(PluginConfiguration, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.verbose_name or self.name