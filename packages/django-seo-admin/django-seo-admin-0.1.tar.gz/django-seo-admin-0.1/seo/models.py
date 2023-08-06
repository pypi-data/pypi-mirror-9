from django.db import models

'''
	Model that have the records
	for SEO
'''
class SeoAdmin(models.Model):

	type = models.CharField(max_length=100, null=False)
	is_property = models.BooleanField(default=False)
	field = models.CharField(max_length=100, null=True, blank=True)
	content = models.CharField(max_length=500, null=False)

	def __unicode__(self):
		if self.field == "":
			return '%s - %s' % (self.type, self.content)
		else:
			return '%s - %s - %s' % (self.type, self.field, self.content)