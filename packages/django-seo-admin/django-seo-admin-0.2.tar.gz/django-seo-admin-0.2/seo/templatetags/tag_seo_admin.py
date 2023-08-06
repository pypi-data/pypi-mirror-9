#encoding:utf-8
import sys

from django import template

from seo.utils import get_contect_seo_admin

register = template.Library()

'''
	Set all objects from model SEOADMIN to html.
	Now, support all tag meta and tag title. Nothing more
'''
@register.simple_tag
def get_metadata(**kwargs):

	#Get all objects from model 
	data_seo = get_contect_seo_admin()

	html = ""
	for seo_obj in data_seo:
		type_admin = seo_obj.type.lower().strip()

		if type_admin == "meta":

			if seo_obj.is_property == True:
				html = html + '<' + type_admin + " " + "property='" + seo_obj.field.strip() 
				html = html + "' content='" + seo_obj.content.strip() + "'>"
			else:
				html = html + '<' + type_admin + " " + "name='" + seo_obj.field.strip() 
				html = html + "' content='" + seo_obj.content.strip() + "'>"

		elif type_admin == "title":

			html = html + "<" + type_admin + ">" +  seo_obj.content.strip() + "</" + type_admin + ">"

	return html 



