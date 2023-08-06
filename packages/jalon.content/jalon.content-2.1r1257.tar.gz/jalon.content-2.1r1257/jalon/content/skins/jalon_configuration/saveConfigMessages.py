## Controller Python Script "saveConfigBIE"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
del form["form.button.save"]
context.setPropertiesMessages(form)
context.REQUEST.RESPONSE.redirect("%s/gestion_messages" % context.absolute_url())
