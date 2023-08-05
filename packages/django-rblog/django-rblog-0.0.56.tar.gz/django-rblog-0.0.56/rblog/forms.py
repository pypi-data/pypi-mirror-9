# -*- coding: utf-8 -*-

from django import forms

from models import Post


class LinkForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['canonical']
