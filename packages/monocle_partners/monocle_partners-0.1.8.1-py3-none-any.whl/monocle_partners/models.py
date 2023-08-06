# -*- coding: utf-8 -*-
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField

class Partner(models.Model):
    name = models.CharField(max_length=255, verbose_name= 'Название партнера')
    image = models.ImageField(upload_to='partners/%Y/%m/%d', verbose_name= 'Логотип')
    position = models.PositiveIntegerField(default=0)
    isShown = models.BooleanField(default=True, verbose_name= 'Показывать партнера')

    def __str__(self):
        return self.name

    def image_admin(self):
        return u'<img src="%s" height="200" />' % self.image.url

    image_admin.short_description = u'Изображение'
    image_admin.allow_tags = True

    class Meta:
        verbose_name_plural = u'Партнеры'
        verbose_name = u'Партнер'
        ordering = ['position']
