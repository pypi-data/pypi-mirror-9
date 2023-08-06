##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

#return context.REQUEST
context.setAuteurs(context.REQUEST.form)
return context.REQUEST.RESPONSE.redirect("%s/cours_acces_view?onglet=gestion-acces-ens" % context.absolute_url())
