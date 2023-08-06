# -*- coding: utf-8 -*-
from django.db import models

class Review(models.Model):
    reviewer = models.CharField(max_length=255, verbose_name= 'Имя клиента')
    image = models.ImageField(upload_to='reviews/%Y/%m/%d', verbose_name= 'Фото клиента')
    text = models.TextField(verbose_name='Текст отзыва')
    isShown = models.BooleanField(default=True, verbose_name= 'Показывать отзыв')
    position = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.reviewer

    class Meta:
        verbose_name_plural = u'Отзывы'
        verbose_name = u'Отзыв'
        ordering = ['position']


