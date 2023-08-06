# -*- coding: utf-8 -*-
from django.db import models

class Review(models.Model):
    reviewer = models.CharField(max_length=255, verbose_name= 'Имя клиента')
    image = models.ImageField(upload_to='reviews/%Y/%m/%d', verbose_name= 'Фото клиента')
    text = models.TextField(verbose_name='Текст отзыва')
    isShown = models.BooleanField(default=True, verbose_name= 'Показывать отзыв')
    position = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.reviewer
    name = models.CharField(max_length=255, verbose_name= 'Название партнера')
    image = models.ImageField(upload_to='parntners/%Y/%m/%d', verbose_name= 'Логотип')
    position = models.PositiveIntegerField(default=0)
    isShown = models.BooleanField(default=True, verbose_name= 'Показывать партнера')

    def __unicode__(self):
        return self.name

    def image_admin(self):
        return u'<img src="%s" height="200" />' % self.image.url

    image_admin.short_description = u'Изображение'
    image_admin.allow_tags = True

    class Meta:
        verbose_name_plural = u'Партнеры'
        verbose_name = u'Партнер'
        ordering = ['position']

    class Meta:
        verbose_name_plural = u'Отзывы'
        verbose_name = u'Отзыв'
        ordering = ['position']


