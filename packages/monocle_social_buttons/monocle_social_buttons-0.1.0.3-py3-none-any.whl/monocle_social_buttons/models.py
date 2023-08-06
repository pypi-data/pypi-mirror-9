# -*- coding: utf-8 -*-
from django.db import models

class SocialButton(models.Model):
    name = models.CharField(max_length=255, verbose_name= 'Название социальной сети')
    icon = models.ImageField(upload_to='models/%Y/%m/%d', verbose_name= 'Иконка соцсети')
    url = models.URLField()
    position = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'Социальные кнопки'
        verbose_name = u'Социальная кнопка'
        ordering = ['position']


