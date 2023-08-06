## Controller Python Script "ajouterressource_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

param = {}
REQUEST = context.REQUEST
redirection = context.absolute_url()
#dans le cas ou ça n'est pas une ressource Bu
if not REQUEST.form.has_key("recordsid"):
    #si la ressource n'existe pas on la creer
   if not REQUEST.form.has_key("idobj"):
      idobj = context.invokeFactory(type_name='JalonRessourceExterne', id="Externe-%s-%s" % (REQUEST["authMember"], DateTime().strftime("%Y%m%d%H%M%S")))
      obj = getattr(context, idobj)
      if REQUEST["formulaire"] == "ajout-web":
         param = {"Title"                : REQUEST["title"]
                 ,"TypeRessourceExterne" : "Lien web"
                 ,"Description"          : REQUEST["description"]
                 ,"Urlbiblio"            : REQUEST["urlbiblio"]}
      else:
         param = {"Title"                : REQUEST["title"]
                 ,"TypeRessourceExterne" : "Lecteur exportable"
                 ,"Description"          : REQUEST["description"]
                 ,"Lecteur"            : REQUEST["lecteur"]}
    #sinon on la modifie juste
   else:
      obj = context
      dicoAttribut = obj.getAttributsTypeMod()
      for attribut in REQUEST.form.keys():
          if dicoAttribut.has_key(attribut): param[dicoAttribut[attribut]] = REQUEST.form[attribut]
      redirection = "%s/" % context.aq_parent.absolute_url()
   obj.setProperties(param)
else:
   for recordid in REQUEST.form["recordsid"]:
       idobj = context.invokeFactory(type_name='JalonRessourceExterne', id="Externe-%s-%s-%s" % (REQUEST["authMember"], recordid, DateTime().strftime("%Y%m%d%H%M%S")))
       obj = getattr(context, idobj)
       obj.majCatalogueBU(recordid)

context.REQUEST.RESPONSE.redirect(redirection)