#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .models import SeoAdmin

'''	
	Return all content 
	from model SEO ADMIN
'''
def get_contect_seo_admin():

	data = SeoAdmin.objects.all()
	return data
