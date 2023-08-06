##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFPlone import PloneMessageFactory as _

#return context.REQUEST
code = context.setGroupePerso(context.REQUEST)

HTTP_X_REQUESTED_WITH = False
if context.REQUEST.form["typeGroupe"] == "email":
    if context.REQUEST.HTTP_X_REQUESTED_WITH == 'XMLHttpRequest':
        HTTP_X_REQUESTED_WITH = True

if not HTTP_X_REQUESTED_WITH:
    context.REQUEST.RESPONSE.redirect("%s/cours_acces_view?onglet=gestion-acces-etu" % context.absolute_url())
else:
    return "%s/cours_acces_view?onglet=gestion-acces-etu" % context.absolute_url()