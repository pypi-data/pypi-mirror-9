# -*- coding: utf-8 -*-
from django.db import models

class SampleModel(models.Model):
    name = models.CharField(max_length=255, verbose_name= 'Имя')
    image = models.ImageField(upload_to='models/%Y/%m/%d', verbose_name= 'Фото')
    text = models.TextField(verbose_name='Текст')
    isShown = models.BooleanField(default=True, verbose_name= 'Показывать')
    position = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'Модели'
        verbose_name = u'Модель'
        ordering = ['position']


