# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.folder import ATFolder, ATFolderSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonFolder
from jalon.content.browser.config.jalonconfig import IJalonConfigControlPanel
#from jalon.content.browser.config.jalonconfiguration import IJalonConfigurationControlPanel

from Acquisition import aq_inner
from DateTime import DateTime

import locale
import json
import urllib
import urllib2
import random
import jalon_utils
import string
import jalonressourceexterne
import ldap
import cStringIO
import os
import copy


JalonFolderSchema = ATFolderSchema.copy() + atpublic.Schema((
    atpublic.StringField("password",
                         required=False,
                         accessor="getPassword",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Mot de passe"),
                                                      description=_(u"Le mot de passe du dossier"),)
                         ),
    atpublic.StringField("complement",
                         required=False,
                         accessor="getComplement",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Complement propre a chaque dossier"),
                                                      description=_(u"Le complement du dossier"),)
                         ),
))

listeSubJalonFolder = [["Fichiers", "Fichiers"],
                       ["Sonorisation", u"Présentations sonorisées".encode("utf-8")],
                       ["Wims", "Exercices Wims"],
                       ["Externes", "Liens"],
                       ["Glossaire", "Termes de glossaire"],
                       ["Webconference", u"Webconférences".encode("utf-8")],
                       ["CatalogueBU", "Catalogue BU"],
                       ["Video", "Vidéos"]]

SIZE_CONST = {'KB': 1024, 'MB': 1024 * 1024, 'GB': 1024 * 1024 * 1024}

def addSubJalonFolder(obj, event):
    #portal = getSite()
    #jalon_conf = IJalonConfigControlPanel(portal)
    #allActif = jalon_conf.getAllActiver()
    for subfolder in listeSubJalonFolder:
        obj.invokeFactory(type_name='JalonFolder', id=subfolder[0])
        rep = getattr(obj, subfolder[0])
        rep.setDefaultPage("jalonfolder_view")
        rep.setTitle(subfolder[1])
        #if subfolder[0] == "SessionC2I":
        #    rep.setExcludeFromNav(True)
        #elif not allActif[subfolder[0].lower()]:
        #    rep.setExcludeFromNav(True)
        rep.setPortlets()
        rep.reindexObject()


class JalonFolder(ATFolder):
    """ Un dossier Jalon
    """

    implements(IJalonFolder)
    meta_type = 'JalonFolder'
    schema = JalonFolderSchema

    def __init__(self, *args, **kwargs):
        super(JalonFolder, self).__init__(*args, **kwargs)
        self.uploader_id = self._uploader_id()

    def addSubJalonFolder(self, memberid):
        addSubJalonFolder(self, memberid)

    def callUrl(self, url, param):
        jalon_utils.callUrl(self, url, param)

    def getAjout(self):
        dico = {"Wims": "JalonExerciceWims", "Externes": "JalonRessourceExterne", "Glossaire": "JalonTermeGlossaire", "didacticiels": "JalonRessourceExterne", "Sonorisation": "Sonorisation", "Webconference": "Webconference", "CatalogueBU": "CatalogueBU"}
        if self.getId() in dico:
            return dico[self.getId()]

    def getAttributConf(self, attribut):
        portal = self.portal_url.getPortalObject()
        jalon_conf = IJalonConfigControlPanel(portal)
        return jalon_conf.__getattribute__("get_%s" % attribut)()

    """
        Convert "Human friendly" file size into original size, in bytes.
    """
    def getItemSize(self, item_size):

        # Get size as stored in catalog
        #display_size = item.getObjSize()
        display_size = item_size.split(" ")

        # if the size is a float, then make it an int
        # happens for large files
        try:
            size = float(display_size[0])
        except (ValueError, TypeError):
            size = 0
        units = display_size[-1]
        if units in SIZE_CONST:
            size = size * SIZE_CONST[units]
        return size

    def getContents(self, subject, typeR, authMember, repertoire, categorie=None):
        """#DEBUG start
        print "\n••• getContents •••\n"
        print "self.id ->", self.getId()
        print "subject ->", subject
        print "\n"
        # DEBUG end"""
        dico = {"portal_type": typeR}
        if typeR == "Fichiers":
            dico["portal_type"] = ["File", "Image", "Document"]
        if typeR == "JalonExerciceWims" and subject in ["", None, "last"]:
            # en prod, supprimer "a".
            #mail_erreur = {"objet":"Erreur WIMS (jalonfolder/getContents)","a":"bado@unice.fr"}
            #dico["portal_type"] = "JalonExerciceWims"
            classe = self.getComplement()
            #print "---- getContents JalonWims ---"
            if not classe:
                #1er  cas : Aucune classe n'existe pour cet utilisateur
                #print "not Classe"
                member = self.portal_membership.getMemberById(authMember)
                auth_email = member.getProperty("email")
                fullname = member.getProperty("fullname")
                if not fullname:
                    fullname = member.getProperty("displayName")
                if not auth_email:
                    auth_email = str(member.getProperty("mail"))
                groupement = self.wims("creerClasse", {"authMember": authMember, "fullname": fullname, "auth_email": auth_email, "type": "2", "qclass": ""})
                if groupement["status"] == "OK":
                    idClasse = self.wims("creerClasse", {"authMember": authMember, "fullname": fullname, "auth_email": auth_email, "type": "0", "titre_classe": "Mes exercices", "qclass": groupement["class_id"]})
                    if idClasse:
                        self.complement = str(groupement["class_id"])
                        return []
                else:
                    #print "*****    Mauvais parametrage de votre connexion WIMS  *****"
                    #print "[jalonfolder.py/getContents] Creation du groupement impossible"
                    #print " Reponse WIMS : %s" % groupement
                    #print "*****                                                 *****"
                    return {"erreur": "wims_bad_conf"}
            else:
                #2e  cas : l'utilisateur courant dispose deja d'une classe. on liste ses exercices.
                #print "Classe %s" % self.getComplement()
                #exercices={}
                #try:
                exercices = self.wims("getExercicesWims",
                                      {"authMember": authMember,
                                       "qclass": "%s_1" % self.getComplement(),
                                       "jalon_URL": self.absolute_url()
                                      })
                if exercices["status"] == "ERROR":
                    #en cas d'indisponibilite, le code retour de WIMS donne un type "HTTPError"
                    if "type" in exercices:
                        return {"erreur": "wims_unavailable"}
                    else:
                        return {"erreur": "wims_bad_conf"}
                #except:
                #   mail_body = "*****    WIMS indisponible ou Mauvais parametrage de La connexion WIMS  *****\n"
                #   mail_body += "[jalonfolder.py/getContents] getExercicesWims\n"
                #   mail_body += "#2e  cas : l'utilisateur courant dispose deja d'une classe. on liste ses exercices.\n\n"
                #   mail_body += " authMember : %s \n" % authMember
                #   mail_body += " qclass : %s_1 \n" % self.getComplement()
                #   mail_body += "*****                                                                   *****\n"
                #   print mail_body
                #   mail_erreur["message"] = mail_body
                #   self.envoyerMailErreur(mail_erreur)
                #   Si getExercicesWIMS plante, c'est :
                #   soit une mauvaise configuration de WIMS  par l'admin (elle a du etre changee entre temps, puisqu'il dispose d'une classe ici)
                #   soit que wims est actuellement indisponible. (cas un peu plus probable que le 1er)
                #   return {"erreur" : "wims_unavailable" }

                exercices_jalon = self.objectIds()
                if "exocount" in exercices:
                    if exercices["exocount"] == 0:
                        exercices_wims = []
                    else:
                        exercices_wims = exercices["exotitlelist"]
                    if len(exercices_jalon) < len(exercices_wims):
                        liste_modeles = self.getListeModelesWims()
                        #On recupere les exos de wims pour les créer sur jalon
                        for exo_wims in exercices_wims:
                            exo_ok = False
                            for exo_jalon in exercices_jalon:
                                if exo_wims["id"] == exo_jalon:
                                    exo_ok = True
                            if not exo_ok:
                                modele = exo_wims["id"].split("-")[0]
                                if modele not in liste_modeles:
                                    modele = "exercicelibre"
                                #CREATION de l'exercice %s sur Jalon " % exo_wims["id"]
                                idobj = self.invokeFactory(type_name='JalonExerciceWims', id=exo_wims["id"])
                                obj = getattr(self, idobj)
                                obj.setProperties({"Title": exo_wims["title"],
                                                   "Modele": modele})
                else:
                    #*****serveur WIMS indisponible ou mauvaise configuration de l'acces WIMS"
                    # Si WIMS est indisponible, on ignore simplement sa liste d'exercices et on affiche celle de Jalon uniquement.
                    #print "*****    Mauvais parametrage de votre connexion WIMS  *****"
                    #print "[jalonfolder.py] getExercicesWims : %s" % exercices
                    #print "*****                                                *****"
                    return "wims_unavailable"

        idreunion = None
        if "-" in repertoire:
            repertoire, idreunion = repertoire.split("-")
        if repertoire in ["Webconference", "Sonorisation"] and subject in ["", None, "last"]:
            if not idreunion:
                idreunion = self.getReunion(authMember, None)["idreunion"]
            #self.plone_log(idreunion)
            enregistrements_connect = self.connect('rechercherEnregistrements', {'id': idreunion})
            setConnect = set([o["id"] for o in enregistrements_connect])
            #self.plone_log(setConnect)
            enregistrements_jalon = self.getFolderContents(contentFilter=dico)
            listeIdJalon = [o.getId for o in enregistrements_jalon]
            #self.plone_log(listeIdJalon)
            for enregistrement in enregistrements_connect:
                if not enregistrement["id"] in listeIdJalon:
                    idobj = self.invokeFactory(type_name='JalonConnect', id=enregistrement["id"])
                    obj = getattr(self, idobj)
                    obj.setProperties({"Title":     enregistrement["title"],
                                       "DateAjout": str(enregistrement["created"]),
                                       "DateUS":    enregistrement["dateUS"],
                                       "Duree":     enregistrement["duration"],
                                       "UrlEnr":    enregistrement["url"]})
                    obj.reindexObject()
                self.reindexObject()
            return self.getFolderContents(contentFilter=dico)

        if repertoire == "Cours":
            portal_catalog = getToolByName(self, "portal_catalog")
            #if categorie == "1":
                #dico["getCategorieCours"] = "1"
            if subject == "favori":
                try:
                    dico['Subject'] = authMember.encode("utf-8")
                    authMember = authMember.encode("utf-8")
                except:
                    dico["Subject"] = authMember
            liste = list(self.getFolderContents(contentFilter=dico))
            liste_id = [x.getId for x in liste]
            if subject == "favori":
                auteurPrincipal = list(portal_catalog.searchResults(portal_type=typeR, getAuteurPrincipal=authMember, Subject=authMember))
            else:
                auteurPrincipal = list(portal_catalog.searchResults(portal_type=typeR, getAuteurPrincipal=authMember))
            if auteurPrincipal:
                for brain in auteurPrincipal:
                    if not brain.getId in liste_id:
                       liste.append(brain)
                       liste_id.append(brain.getId)
            if subject == "favori":
                coauteurs = list(portal_catalog.searchResults(portal_type=typeR, getCoAuteurs=authMember, Subject=authMember))
            else:
                coauteurs = list(portal_catalog.searchResults(portal_type=typeR, getCoAuteurs=authMember))
            if coauteurs:
                for brain in coauteurs:
                    if not brain.getId in liste_id:
                       liste.append(brain)
                       liste_id.append(brain.getId)
            if subject == "favori":
                colecteurs = list(portal_catalog.searchResults(portal_type=typeR, getCoLecteurs=authMember, Subject=authMember))
            else:
                colecteurs = list(portal_catalog.searchResults(portal_type=typeR, getCoLecteurs=authMember))
            if colecteurs:
                for brain in colecteurs:
                    if not brain.getId in liste_id:
                       liste.append(brain)
                       liste_id.append(brain.getId)
            return list(liste)

        if subject not in ["", None, "last"]:
            last = False
            subjects = []
            tags = subject.split(',')
            if "last" in tags:
                tags.remove("last")
                last = True
            for tag in tags:
                subjects.append(urllib.quote(tag))
            if len(subjects) > 1:
                dico['Subject'] = {'query': subjects, 'operator': 'and'}
            else:
                dico['Subject'] = subjects[0]
            if last:
                dico["sort_on"] = "modified"
                dico["sort_order"] = "descending"
                return self.getFolderContents(contentFilter=dico, batch=True, b_size=20)
            else:
                return self.getFolderContents(contentFilter=dico)
        elif subject == "last":
            dico["sort_on"] = "modified"
            dico["sort_order"] = "descending"
            return self.getFolderContents(contentFilter=dico, batch=True, b_size=20)
        else:
            dico["sort_on"] = "modified"
            dico["sort_order"] = "descending"
            return self.getFolderContents(contentFilter=dico)

    def getEmailUser(self, login):
        portal = self.portal_url.getPortalObject()
        portal_membership = getToolByName(portal, "portal_membership")
        member = portal_membership.getMemberById(login)
        auth_email = member.getProperty("email")
        if not auth_email:
            auth_email = str(member.getProperty("mail"))
        return auth_email

    def getInfosApogee(self, code, type):
        portal = self.portal_url.getPortalObject()
        #apogee = getToolByName(portal, "portal_apogee")
        bdd = getToolByName(portal, "portal_jalon_bdd")
        if type == "etape":
            #suite au probleme de DAEU-B ce conditionnement à été creer pour cette fonction
            #COD_ETP, COD_VRS_VET = code.rsplit("-", 1)
            #return list(self.encodeUTF8(apogee.getInfosEtape(COD_ETP, COD_VRS_VET)))
            retour = self.encodeUTF8(bdd.getInfosEtape(code))
            if not retour:
                return ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
            return list(retour)
        if type in ["ue", "uel"]:
            retour = self.encodeUTF8(bdd.getInfosELP2(code))
            if not retour:
                return ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
            return list(retour)
        if type == "groupe":
            retour = self.encodeUTF8(bdd.getInfosGPE(code))
            if not retour:
                return ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
            return list(retour)

    # getInfosMembre recupere les infos sur les personnes.
    def getInfosMembre(self, username):
        #self.plone_log("getInfosMembre")
        return jalon_utils.getInfosMembre(username)

    """
    def getInfosMembre(self, username):
        portal_membership = self.portal_membership
        authMember = portal_membership.getMemberById(username)
        if authMember:
            fullname = authMember.getProperty("fullname")
            if not fullname:
                fullname = authMember.getProperty("displayName")
            email = authMember.getProperty("email")
            if not email:
                email = authMember.getProperty("mail")
        else:
            authMember = self.rechercherUserLDAP(username, "supannAliasLogin", True)
            fullname = authMember["name"]
            email = authMember["email"]
        return {"id":       username,
                "fullname": fullname,
                "email":    email,
                "nom":     fullname.strip().rsplit(" ", 1)[-1]}
    """

    #getDisplayName() permet d'obtenir le nom (+prenom) d'un utilisateur
    def getDisplayName(self, user_id, request=None, portal=None):
        return jalon_utils.getDisplayName(user_id, request, portal)

    def getItem(self, idItem):
        return getattr(self, idItem)

    def getPropertiesMessages(self, key=None):
        jalon_properties = self.portal_jalon_properties
        return jalon_properties.getPropertiesMessages(key)

    def getCamaradesEtudiant(self, member_id=None):
        listeDiplome = []
        portal = self.portal_url.getPortalObject()
        portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")

        if idMember:
            authMember = portal_membership.getMemberById(idMember)
        else:
            authMember = portal_membership.getAuthenticatedMember()

    def getCours(self, categorie="1", authMember=None):
        if authMember.has_role("EtudiantJalon"):
            return self.getCoursEtudiantJalon(categorie, authMember.getId())
        else:
            return self.getCoursEtudiant(categorie, authMember.getId())

    def getCoursEtudiant(self, categorie="1", idMember=None):
        listeDiplome = []
        dicoAuteur = {}
        portal = self.portal_url.getPortalObject()
        portal_catalog = getToolByName(portal, "portal_catalog")
        portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")
        portal_membership = getToolByName(portal, "portal_membership")

        if idMember:
            authMember = portal_membership.getMemberById(idMember)
        else:
            authMember = portal_membership.getAuthenticatedMember()

        diplomes = []
        #isLDAP = self.isLDAP()
        COD_ETU = authMember.getId()
        """
        if isLDAP:
            ldapplugin = getattr(getattr(portal.acl_users, "ldap-plugin"), "acl_users")

            user = ldapplugin._binduid
            password = ldapplugin._bindpwd
            infosServer = ldapplugin.getServers()

            try:
                server = "%s://%s:%s" % (infosServer[0]["protocol"], infosServer[0]["host"], infosServer[0]["port"])
                ldapserver = ldap.initialize(server)
                ldapserver.simple_bind_s(user, password)
            except:
                server = "%s://%s:%s" % (infosServer[1]["protocol"], infosServer[1]["host"], infosServer[1]["port"])
                ldapserver = ldap.initialize(server)
                ldapserver.simple_bind_s(user, password)
            diplomes = authMember.getProperty("unsdiplomes")
            if portal_jalon_bdd.getTypeBDD() == "apogee":
                COD_ETU = authMember.getProperty("supannEtuId", authMember.getProperty("supannAliasLogin"))
        else:
        """
        for diplome in portal_jalon_bdd.getInscriptionIND(COD_ETU, "etape"):
            diplomes.append(diplome["COD_ELP"])

        if categorie == "1":
            dicoUE = {}
            #groupes = portal_jalon_bdd.getGroupesEtudiant(COD_ETU)
            #pour les nouveaux étudiant qui n'ont pas encore de diplome
            if not diplomes:
                listeCours = []
                liste = list(portal_catalog.searchResults(portal_type="JalonCours", getRechercheAcces=authMember.getId()))
                for cours in liste:
                    auteur = cours.getAuteurPrincipal
                    if not auteur:
                        auteur = cours.Creator
                    if not auteur in dicoAuteur:
                        dicoAuteur[auteur] = {"nom": auteur, "email": ""}
                        """
                        if isLDAP:
                            ldapfilter = "(&(%s=%s))" % (ldapplugin._login_attr, auteur)
                            result = ldapserver.search_s(ldapplugin.users_base, ldap.SCOPE_SUBTREE, ldapfilter, None)
                            if result:
                                dicoAuteur[auteur]["nom"] = result[0][1].get("cn", auteur)[0]
                                dicoAuteur[auteur]["email"] = result[0][1].get("mail", auteur)[0]
                        else:
                        """
                        #individu = portal_jalon_bdd.getIndividuLITE(auteur)
                        #if individu:
                        #    dicoAuteur[auteur]["nom"] = "%s %s" % (individu["LIB_NOM_PAT_IND"], individu["LIB_PR1_IND"])
                        #    dicoAuteur[auteur]["email"] = individu["EMAIL_ETU"]
                        infosMembre = self.getInfosMembre(auteur)
                        dicoAuteur[auteur]["nom"] = infosMembre["fullname"]
                        dicoAuteur[auteur]["email"] = infosMembre["email"]
                    listeCours.append({"id":     cours.getId,
                                       "title":  cours.Title,
                                       "description":  cours.Description,
                                       "auteur": dicoAuteur[auteur]["nom"],
                                       "createur": cours.Creator,
                                       "idauteur": auteur,
                                       "email":  dicoAuteur[auteur]["email"],
                                       "url":    "%s" % cours.getURL(),
                                       "modified":  cours.modified,
                                       "acces":  ["Invité"]})
                listeDiplome.append({"libelle": "Mes cours", "listeCours": listeCours})
                return listeDiplome
            for COD_ELP in diplomes:
                listeUE = []
                etape = portal_jalon_bdd.getVersionEtape(COD_ELP)
                if etape:
                    dicoUE["etape*-*%s" % COD_ELP] = {"type": "etape", "libelle": etape[0]}
                    listeUE.append("etape*-*%s" % COD_ELP)

                    inscription_pedago = portal_jalon_bdd.getInscriptionPedago(COD_ETU, COD_ELP)
                    if not inscription_pedago:
                        inscription_pedago = portal_jalon_bdd.getUeEtape(COD_ELP)
                    for inscription in inscription_pedago:
                        ELP = "*-*".join([inscription["TYP_ELP"], inscription["COD_ELP"]])
                        if not ELP in dicoUE:
                            dicoUE[ELP] = {"type": inscription["TYP_ELP"], "libelle": inscription["LIB_ELP"]}
                            listeUE.append(ELP)

                    listeUE.append(authMember.getId())
                    query = {'query': listeUE, 'operator': 'or'}
                    listeCours = []
                    liste = list(portal_catalog.searchResults(portal_type="JalonCours", getRechercheAcces=query))
                    for cours in liste:
                        listeAcces = []
                        auteur = cours.getAuteurPrincipal
                        if not auteur:
                            auteur = cours.Creator
                        if not auteur in dicoAuteur:
                            dicoAuteur[auteur] = {"nom": auteur, "email": ""}
                            """
                            if isLDAP:
                                ldapfilter = "(&(%s=%s))" % (ldapplugin._login_attr, auteur)
                                result = ldapserver.search_s(ldapplugin.users_base, ldap.SCOPE_SUBTREE, ldapfilter, None)
                                if result:
                                    dicoAuteur[auteur]["nom"] = result[0][1].get("cn", auteur)[0]
                                    dicoAuteur[auteur]["email"] = result[0][1].get("mail", auteur)[0]
                            else:
                                result = portal_jalon_bdd.getIndividuLITE(auteur)
                                if result:
                                    dicoAuteur[auteur]["nom"] = "%s %s" % (result["LIB_PR1_IND"], result["LIB_NOM_PAT_IND"])
                                    dicoAuteur[auteur]["email"] = result["EMAIL_ETU"]
                            """
                            infosMembre = self.getInfosMembre(auteur)
                            dicoAuteur[auteur]["nom"] = infosMembre["fullname"]
                            dicoAuteur[auteur]["email"] = infosMembre["email"]

                        for acces in cours.getListeAcces:
                            if acces in dicoUE:
                                listeAcces.append("%s : %s" % (dicoUE[acces]['type'], dicoUE[acces]['libelle']))
                        if authMember.getId() in cours.getGroupe:
                            listeAcces.append("Invité")
                        try:
                            if authMember.getId() in cours.getInscriptionsLibres:
                                listeAcces.append("Inscription par mot de passe")
                        except:
                            pass
                        listeCours.append({"id":     cours.getId,
                                           "title":  cours.Title,
                                           "description":  cours.Description,
                                           "auteur": dicoAuteur[auteur]["nom"],
                                           "createur": cours.Creator,
                                           "idauteur": auteur,
                                           "email":  dicoAuteur[auteur]["email"],
                                           "url":    cours.getURL(),
                                           "modified":  cours.modified,
                                           "acces":  listeAcces})
                    listeDiplome.append({"libelle":  etape[0], "listeCours": listeCours})

            #if isLDAP:
            #    ldapserver.unbind_s()
        else:
            listeCours = []
            liste = list(portal_catalog.searchResults(portal_type="JalonCours", getCategorieCours=categorie))
            for cours in liste:
                auteur = cours.getAuteurPrincipal
                if not auteur:
                    auteur = cours.Creator
                if not auteur in dicoAuteur:
                    dicoAuteur[auteur] = {"nom": auteur, "email": ""}
                    """
                    if isLDAP:
                        ldapfilter = "(&(%s=%s))" % (ldapplugin._login_attr, auteur)
                        result = ldapserver.search_s(ldapplugin.users_base, ldap.SCOPE_SUBTREE, ldapfilter, None)
                        if result:
                            dicoAuteur[auteur]["nom"] = result[0][1].get("cn", auteur)[0]
                            dicoAuteur[auteur]["email"] = result[0][1].get("mail", auteur)[0]
                    else:
                        result = portal_jalon_bdd.getIndividuLITE(auteur)
                        if result:
                            dicoAuteur[auteur]["nom"] = "%s %s" % (result["LIB_PR1_IND"], result["LIB_NOM_PAT_IND"])
                            dicoAuteur[auteur]["email"] = result["EMAIL_ETU"]
                    """
                    infosMembre = self.getInfosMembre(auteur)
                    dicoAuteur[auteur]["nom"] = infosMembre["fullname"]
                    dicoAuteur[auteur]["email"] = infosMembre["email"]
                listeCours.append({"id":       cours.getId,
                                   "title":    cours.Title,
                                   "description":  cours.Description,
                                   "auteur":   dicoAuteur[auteur]["nom"],
                                   "createur": cours.Creator,
                                   "email":    dicoAuteur[auteur]["email"],
                                   "idauteur": auteur,
                                   "modified":  cours.modified,
                                   "url":      "%s" % cours.getURL()})
            listeDiplome.append({"listeCours": listeCours})
        return listeDiplome

    def getCoursEtudiantJalon(self, categorie="1", idMember=None):
        portal = self.portal_url.getPortalObject()
        portal_catalog = getToolByName(portal, "portal_catalog")
        portal_membership = getToolByName(portal, "portal_membership")
        portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")

        dicoAuteur = {}
        if idMember:
            authMember = portal_membership.getMemberById(idMember)
        else:
            authMember = portal_membership.getAuthenticatedMember()

        """
        isLDAP = self.isLDAP()
        if isLDAP:
            ldapplugin = getattr(getattr(portal.acl_users, "ldap-plugin"), "acl_users")

            user = ldapplugin._binduid
            password = ldapplugin._bindpwd
            infosServer = ldapplugin.getServers()

            try:
                server = "%s://%s:%s" % (infosServer[0]["protocol"], infosServer[0]["host"], infosServer[0]["port"])
                ldapserver = ldap.initialize(server)
                ldapserver.simple_bind_s(user, password)
            except:
                server = "%s://%s:%s" % (infosServer[1]["protocol"], infosServer[1]["host"], infosServer[1]["port"])
                ldapserver = ldap.initialize(server)
                ldapserver.simple_bind_s(user, password)
        """

        dicoAuteur = {}
        listeCours = []
        listeDiplome = []
        if categorie == "1":
            liste = list(portal_catalog.searchResults(portal_type="JalonCours", getRechercheAcces=authMember.getId()))
            for cours in liste:
                auteur = cours.getAuteurPrincipal
                if not auteur:
                    auteur = cours.Creator
                if not auteur in dicoAuteur:
                    dicoAuteur[auteur] = {"nom": auteur, "email": ""}
                    """
                    if isLDAP:
                        ldapfilter = "(&(%s=%s))" % (ldapplugin._login_attr, auteur)
                        result = ldapserver.search_s(ldapplugin.users_base, ldap.SCOPE_SUBTREE, ldapfilter, None)
                        if result:
                            dicoAuteur[auteur]["nom"] = result[0][1].get("cn", auteur)[0]
                            dicoAuteur[auteur]["email"] = result[0][1].get("mail", auteur)[0]
                    else:
                        individu = portal_jalon_bdd.getIndividuLITE(auteur)
                        if individu:
                            dicoAuteur[auteur]["nom"] = "%s %s" % (individu["LIB_NOM_PAT_IND"], individu["LIB_PR1_IND"])
                            dicoAuteur[auteur]["email"] = individu["EMAIL_ETU"]
                    """
                    infosMembre = self.getInfosMembre(auteur)
                    dicoAuteur[auteur]["nom"] = infosMembre["fullname"]
                    dicoAuteur[auteur]["email"] = infosMembre["email"]
                listeCours.append({"id"          : cours.getId,
                                   "title"       : cours.Title,
                                   "description" : cours.Description,
                                   "auteur"      : dicoAuteur[auteur]["nom"],
                                   "idauteur"    : auteur,
                                   "createur"    : cours.Creator,
                                   "email"       : dicoAuteur[auteur]["email"],
                                   "url"         : "%s" % cours.getURL(),
                                   "modified"    : cours.modified,
                                   "acces"       : ["Invité"]})
            listeDiplome.append({"libelle": "Mes cours", "listeCours": listeCours})
        else:
            listeCours = []
            liste = list(portal_catalog.searchResults(portal_type="JalonCours", getCategorieCours=categorie))
            for cours in liste:
                auteur = cours.getAuteurPrincipal
                if not auteur:
                    auteur = cours.Creator
                if not auteur in dicoAuteur:
                    dicoAuteur[auteur] = {"nom": auteur, "email": ""}
                    """
                    if isLDAP:
                        ldapfilter = "(&(%s=%s))" % (ldapplugin._login_attr, auteur)
                        result = ldapserver.search_s(ldapplugin.users_base, ldap.SCOPE_SUBTREE, ldapfilter, None)
                        if result:
                            dicoAuteur[auteur]["nom"] = result[0][1].get("cn", auteur)[0]
                            dicoAuteur[auteur]["email"] = result[0][1].get("mail", auteur)[0]
                    else:
                        result = portal_jalon_bdd.getIndividuLITE(auteur)
                        if result:
                            dicoAuteur[auteur]["nom"] = "%s %s" % (result["LIB_PR1_IND"], result["LIB_NOM_PAT_IND"])
                            dicoAuteur[auteur]["email"] = result["EMAIL_ETU"]
                    """
                    infosMembre = self.getInfosMembre(auteur)
                    dicoAuteur[auteur]["nom"] = infosMembre["fullname"]
                    dicoAuteur[auteur]["email"] = infosMembre["email"]
                listeCours.append({"id"          : cours.getId,
                                   "title"       : cours.Title,
                                   "description" :  cours.Description,
                                   "auteur"      : dicoAuteur[auteur]["nom"],
                                   "idauteur"    : auteur,
                                   "createur"    : cours.Creator,
                                   "email"       : dicoAuteur[auteur]["email"],
                                   "idauteur"    : auteur,
                                   "url"         : "%s" % cours.getURL(),
                                   "modified"    : cours.modified,})
            listeCours.sort(lambda x,y: cmp(x["auteur"], y["auteur"]))
            listeDiplome.append({"listeCours": listeCours})
        return listeDiplome

    def getClefsDico(self, dico):
        return jalon_utils.getClefsDico(dico)

    def getJalonCategories(self):
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return dict(jalon_properties.getCategorie())

    def getListeCours(self, authMember):
        portal = self.portal_url.getPortalObject()
        portal_catalog = getToolByName(portal, "portal_catalog")
        listeCours = list(portal_catalog.searchResults(portal_type="JalonCours", Creator=authMember))
        listeCoursAuteur = list(portal_catalog.searchResults(portal_type="JalonCours", getAuteurPrincipal=authMember))
        if listeCoursAuteur:
            listeCours.extend(listeCoursAuteur)
        listeCoursCoAuteur = list(portal_catalog.searchResults(portal_type="JalonCours", getCoAuteurs=authMember))
        if listeCoursCoAuteur:
            listeCours.extend(listeCoursCoAuteur)

        dicoAccess = {}
        #apogee = getToolByName(portal, "portal_apogee")
        bdd = getToolByName(portal, "portal_jalon_bdd")
        for cours in listeCours:
            #print cours
            for acces in cours.getListeAcces:
                type, code = acces.split("*-*")
                if not code in dicoAccess:
                    if type == "etape":
                        #suite au probleme de DAEU-B ce conditionnement à été creer pour cette fonction
                        #retour = apogee.getInfosEtape(*code.rsplit("-", 1))
                        retour = bdd.getInfosEtape(code)
                        if not retour:
                            elem = ["Le code %s n'est plus valide pour ce diplôme." % code, code, "0"]
                        else:
                            #elem = list(self.encodeUTF8(retour))
                            elem = list(retour)
                    if type in ["ue", "uel"]:
                        retour = bdd.getInfosELP2(code)
                        if not retour:
                            elem = ["Le code %s n'est plus valide pour cette UE / UEL." % code, code, "0"]
                        else:
                            #elem = list(self.encodeUTF8(retour))
                            elem = list(retour)
                    if type == "groupe":
                        retour = bdd.getInfosGPE(code)
                        if not retour:
                            elem = ["Le code %s n'est plus valide pour ce groupe." % code, code, "0"]
                        else:
                            #elem = list(self.encodeUTF8(retour))
                            elem = list(retour)
                    #intracursus = getToolByName(portal, "portal_jalon_intracursus")
                    #retour = intracursus.getNbSeances(code)
                    #if retour["status"] == "REUSSITE":
                    #    nbSeances = retour["nombreSeance"]
                    #else:
                    #    nbSeances = 0
                    nbSeances = 0
                    dicoAccess[code] = {"titre":      elem[0],
                                        "codegpe":    elem[-1],
                                        "type":       type,
                                        "nbetu":      elem[2],
                                        "nbseances":  nbSeances,
                                        "listeCours": [cours.Title]}
                else:
                    dicoAccess[code]["listeCours"].append(cours.Title)
        return dicoAccess

    def getListeEtudiants(self, code, typeCode):
        portal = self.portal_url.getPortalObject()
        #apogee = getToolByName(portal, "portal_apogee")
        bdd = getToolByName(self, "portal_jalon_bdd")
        listeEtudiant = bdd.rechercherUtilisateurs(code, "Etudiant", True)

        if bdd.getTypeBDD() == "sqlite":
            #temp = [self.encodeUTF8(etudiant) for etudiant in listeEtudiant]
            #print listeEtudiant
            return listeEtudiant

        """
        if bdd.getTypeBDD() == "apogee":
            liste = []
            ldapplugin = getattr(getattr(portal.acl_users, "ldap-plugin-etu"), "acl_users")

            user = ldapplugin._binduid
            password = ldapplugin._bindpwd
            infosServer = ldapplugin.getServers()
            try:
                server = "%s://%s:%s" % (infosServer[0]["protocol"], infosServer[0]["host"], infosServer[0]["port"])
                ldapserver = ldap.initialize(server)
                ldapserver.simple_bind_s(user, password)
            except:
                server = "%s://%s:%s" % (infosServer[1]["protocol"], infosServer[1]["host"], infosServer[1]["port"])
                ldapserver = ldap.initialize(server)
                ldapserver.simple_bind_s(user, password)

            for etudiant in listeEtudiant:
                auth_email = None
                infos = self.encodeUTF8(etudiant)
                login = '%s%s%s' % (infos[1][0].lower(), infos[2][0].lower(), infos[3][2:])

                ldapfilter = "(&(cptcree=1)(%s=%s))" % (ldapplugin._login_attr, login)
                result = ldapserver.search_s(ldapplugin.users_base, ldap.SCOPE_SUBTREE, ldapfilter, None)
                if result:
                    auth_email = result[0][1].get("mail", [""])[0]

                liste.append([infos[1], infos[2], login, infos[3], auth_email])
            ldapserver.unbind_s()
            liste.sort(lambda x, y: cmp(x[0], y[0]))
            return liste
        """

    def getListeEtudiantsTSV(self, cod_etp, cod_vrs_vet):
        listeEtudiant = self.getListeEtudiants(cod_etp, cod_vrs_vet)
        TSV = ["\t".join(["NOM", "PRENOM", "SESAME", "NUMERO ETUDIANT", "COURRIEL"])]
        for etudiant in listeEtudiant:
            TSV.append("\t".join([etudiant["LIB_NOM_PAT_IND"], etudiant["LIB_PR1_IND"], etudiant["SESAME_ETU"], str(etudiant["COD_ETU"]), etudiant["EMAIL_ETU"]]))

        return "\n".join(TSV)

    def getListeModelesWims(self):
        modeles = []
        modeles_conf = self.getAttributConf("wims_modele")
        for element in modeles_conf:
            try:
                idmodele, titremodele, catmodele = element.split("*-*")
                modeles.append(idmodele)
            except:
                pass
        return modeles

    def getLocaleDate( self, date, format = "%d/%m/%Y" ):
        return jalon_utils.getLocaleDate( date, format )

    def getConnectDate(self, data, sortable = False):
        return jalon_utils.getConnectDate( data, sortable )

    def getDepotDate(self, data, sortable = False):
        return jalon_utils.getDepotDate( data, sortable )

    def getModelesWims(self):
        #wims = getToolByName(self, "portal_jalon_wims")
        #return wims.getModelesWims()

        modeles = {}
        modeles_conf = self.getAttributConf("wims_modele")
        for element in modeles_conf:
            try:
                idmodele, titremodele, catmodele = element.split("*-*")
                if not catmodele in modeles:
                    modeles[catmodele] = [{"value": idmodele, "title": titremodele}]
                else:
                    modeles[catmodele].append({"value": idmodele, "title": titremodele})
            except:
                pass
        return modeles

    def getMotsClefs(self, search, objet):
        mots = []
        catalog = getToolByName(self, 'portal_catalog')
        keywords = list(catalog.uniqueValuesFor("Subject"))
        for mot in keywords:
            if search in mot:
                mots.append(mot)
        mots.sort()
        """# DEBUG start
        print "\n••• getMotsClefs •••\n"
        print "self.id ->", self.getId()
        print "catalog ->", catalog
        print "mots ->", mots
        print "\n"
        # DEBUG end"""
        return json.dumps(dict(keywords=mots))

    def getPhotoTrombi(self, login):
        return jalon_utils.getPhotoTrombi(login)

    def getRessourceType(self):
        return jalonressourceexterne.ressourceType

    def getTypeLien(self):
        portal = self.portal_url.getPortalObject()
        jalon_conf = IJalonConfigControlPanel(portal)
        externe = jalon_conf.get_activer_externes()
        cataloguebu = jalon_conf.get_activer_cataloguebu()
        typeLien = []
        if externe:
            typeLien.append({"macro":     "ajout-web",
                             "affichage": _(u"Lien web"),
                             "aide":      _(u"Créer un lien à partir d'une URL"),
                             "checked":   "checked"})
            typeLien.append({"macro":     "ajout-video",
                             "affichage": _(u"Lien vidéo"),
                             "aide":      _(u"Créer un lien à partir d'un lecteur exportable comme Youtube, Dailymotion, WIMS"),
                             "checked":   ""})
        if cataloguebu:
            checked = ""
            if len(typeLien) == 0:
                checked = "checked"
            typeLien.append({"macro":     "ajout-catalogue",
                             "affichage": _(u"Lien catalogue"),
                             "aide":      _(u"Trouver une oeuvre ou une revue dans le catalogue de la BU"),
                             "checked":   checked})
        return typeLien

    def getAttributsLien(self, typeLien):
        dico = {"ajout-web":   ["title", "description", "urlbiblio"],
                "ajout-video": ["title", "description", "lecteur"]}
        return dico[typeLien]

    def getShortText( self, text, limit = 75 ):
        #self.plone_log("----- getShortText -----")
        #self.plone_log("**** text : %s" % str(text))
        return jalon_utils.getShortText( text, limit )

    def getSelectedTab( self, cle = "onglet", defaut = "" ):
        # Init
        tabs = {}
        url = self.REQUEST.get( 'URL' )
        spaceName = url[ url.rfind( '/' ) + 1 : ]
        if self.REQUEST.SESSION.has_key( 'tabs' ):
            tabs = self.REQUEST.SESSION.get( 'tabs' )
        # Traitement
        if self.REQUEST.form.has_key( cle ):
            # Enregistrement de la sélection
            defaut = self.REQUEST.form[ cle ]
            tabs[ spaceName ] = defaut
            self.REQUEST.SESSION.set( 'tabs' , tabs )
        else:
            # Pas de sélection
            if tabs.has_key( spaceName ):
                # Enregistrement existant -> chargement
                defaut = tabs[ spaceName ]
        #self.plone_log( self.REQUEST.SESSION.get( 'tabs' ) )
        return defaut

    def getSelectedTags( self ):
        # Init
        tags = {}
        subjects = ""
        spaceName = self.getId().lower( )
        if self.REQUEST.SESSION.has_key( 'tags' ):
            tags = self.REQUEST.SESSION.get( 'tags' )
        # Traitement
        if self.REQUEST.form.has_key( 'subject' ):
            # Enregistrement de la sélection
            subjects = self.REQUEST.form[ 'subject' ]
            tags[ spaceName ] = subjects
            self.REQUEST.SESSION.set( 'tags' , tags )
        else:
            # Pas de sélection
            if tags.has_key( spaceName ):
                # Enregistrement existant -> chargement
                subjects = tags[ spaceName ]
            else:
                # Pas d'enregistrement -> défaut
                subjects = "last"
        #self.plone_log( self.REQUEST.SESSION.get( 'tags' ) )
        return subjects

    """
    def getSelectedTags(self):
        # Retourne le contenu du cookie ou "last" si inexistant
        return self.REQUEST.cookies.get('tags_' + self.getId().lower(), "last")
    """

    def getTag(self):
        retour = []
        mots = list(self.Subject())
        mots.sort()

        if self.getId() in ["Webconference", "Sonorisation"]:
            for mot in mots:
                locale.setlocale(locale.LC_ALL, 'fr_FR')
                try:
                    retour.append({"tag": urllib.quote(mot), "titre": DateTime(mot).strftime("%B %Y")})
                except:
                    retour.append({"tag": urllib.quote(mot), "titre": mot})

        if self.getId() == "Wims":
            tags = self.getTagsWims()
            for mot in mots:
                try:
                    retour.append({"tag": urllib.quote(mot), "titre": tags[mot]})
                except:
                    retour.append({"tag": urllib.quote(mot), "titre": mot})

        if not self.getId() in ["Webconference", "Sonorisation", "Wims"]:
            for mot in mots:
                retour.append({"tag": urllib.quote(mot), "titre": mot})

        """# DEBUG start
        print "\n••• getTag •••\n"
        print "self.id ->", self.getId()
        print "tag ->", tag
        print "mots ->", mots
        print "retour ->", retour
        print "\n"
        # DEBUG end"""

        #self.plone_log( retour )

        return retour

    def getTagsWims(self):
        tags = {"groupe": "Groupe d'exercices"}
        modeles_conf = self.getAttributConf("wims_modele")
        for element in modeles_conf:
            try:
                idmodele, titremodele, catmodele = element.split("*-*")
                if not idmodele in tags:
                    tags[idmodele] = titremodele
            except:
                pass
        return tags

    def setPortlets(self):
        manager = getUtility(IPortletManager, name=u"plone.leftcolumn")
        blacklist = getMultiAdapter((self, manager), ILocalPortletAssignmentManager)
        blacklist.setBlacklistStatus("context", True)
        self.reindexObject()

    def isWebconference(self):
        portal = self.portal_url.getPortalObject()
        jalon_conf = IJalonConfigControlPanel(portal)
        return jalon_conf.get_activer_webconference()

    def _uploader_id(self):
        return 'uploader%s' % str(random.random()).replace('.', '')

    def affTagConnect(selfself, tag):
        return DateTime(tag).strftime('%B %Y')

    def ajouterTag(self, tag):
        if not tag in self.Subject():
            tags = list(self.Subject())
            tags.append(tag)
            self.setSubject(tuple(tags))
            self.reindexObject()

    def connect(self, methode, param):
        connect = getToolByName(self, self.getAttributConf("%s_connecteur" % self.getId().lower()))
        return connect.__getattribute__(methode)(param)

    def encodeUTF8(self, itemAEncoder):
        return jalon_utils.encodeUTF8(itemAEncoder)

    def getSessionConnect(self, authMember):
        motdepasse = self.getComplement()
        self.connect('connexion', {})
        if not motdepasse:
            motdepasse = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(8)])
            self.setComplement(motdepasse)
            liste = ["Webconference", "Sonorisation"]
            liste.remove(self.getId())
            idrep = liste[0]
            getattr(self.aq_parent, idrep).setComplement(motdepasse)
            member = self.portal_membership.getMemberById(authMember)
            auth_email = member.getProperty("email")
            fullname = member.getProperty("fullname")
            if not fullname:
                fullname = member.getProperty("displayName")
            if not auth_email:
                auth_email = member.getProperty("mail")
            self.connect('creerUser', {'userid': authMember, "password": motdepasse, "fullname": fullname, "email": auth_email})
        else:
            self.connect('majPasswordUser', {'userid': authMember, "password": motdepasse})
        return self.connect('genererSessionUser', {'userid': authMember, "password": motdepasse})

    def getReunion(self, authMember, request):
        dossiers = self.connect("getAttribut", {"attribut": "dossiers"})
        if dossiers:
            modele = ""
            for ligne in dossiers.split("\n"):
                if self.getId() in ligne:
                    modele = ligne.split(":")[-1]
                    break
            if modele == "":
                return []
            else:
                modele = modele.replace("\r", "")
        else:
            return {"idreunion": "", "urlreunion": ""}
        reunions = self.connect("rechercherReunions", {"login": authMember, "modele": modele})
        if not reunions:
            motdepasse = self.getComplement()
            if motdepasse:
                member = self.portal_membership.getMemberById(authMember)
                fullname = member.getProperty("fullname")
                if not fullname:
                    fullname = member.getProperty("displayName")
                reunion = self.connect('creerReunion', {'userid': authMember, "password": motdepasse, "fullname": fullname, "modele": modele, "repertoire": self.getId()})
                self.plone_log("reunion")
                self.plone_log(reunion)
            else:
                reunion = {"id": "", "url": ""}
        else:
            reunion = reunions[0]
        if request:
            request.SESSION.set("idreunion", reunion["id"])
        return {"idreunion": reunion["id"], "urlreunion": reunion["url"]}

    def ajouterUtilisateurJalon(self, form):
        portal = self.portal_url.getPortalObject()
        portal_registration = getToolByName(portal, 'portal_registration')
        portal_membership = getToolByName(portal, 'portal_membership')

        password = portal_registration.generatePassword()
        portal_membership.addMember(form["login"], password, ("EtudiantJalon", "Member",), "", {"fullname": form["fullname"], "email": form["email"]})
        portal_registration.registeredNotify(form["login"])

    def addJalonMember(self, form):
        portal = self.portal_url.getPortalObject()
        portal_membership = getToolByName(portal, 'portal_membership')
        portal_membership.addMember(form["login"], form["password"], ("Personnel", "Member",), "", {"fullname": form["fullname"], "email": form["email"]})

    def delEnregistrementConnect(self, paths):
        for path in paths:
            idEnregistrement = path.split("/")[-1]
            idConnect = idEnregistrement.split("-")[0]
            self.connect("supprimerEnregistrement", {"idEnregistrement": idConnect})

    def delClassesWims(self, listClasses):
        for classe in listClasses:
            dico = {"job": "delclass", "code": self.portal_membership.getAuthenticatedMember().getId(), "qclass": classe}
            rep_wims = self.wims("callJob", dico)
            self.wims("verifierRetourWims", {"rep": rep_wims, "fonction": "jalonfolder.py/delClassesWims", "message": "parametres de la requete : %s" % dico})

    # delExoWims() : suppression (coté wims) de la liste des exercices donné en "paths"
    def delExoWims(self, paths):
        for path in paths:
            exo_id = path.split("/")[-1]
            exo = self.getItem(exo_id)
            exo.delExoWims()

    def header_upload(self, request):
        session = request.get('SESSION', {})
        medialabel = session.get('mediaupload', request.get('mediaupload', 'files'))
        # to improve
        if '*.' in medialabel:
            medialabel = ''
        if not medialabel:
            return _('Files Quick Upload')
        if medialabel == 'image':
            return _('Images Quick Upload')
        return _('%s Quick Upload' % medialabel.capitalize())

    def genererPDF(self, code, type):
        template = getattr(self, "page_pdf")(code=code, type=type).encode("utf-8")

        import tempfile
        dest, chemin = tempfile.mkstemp('.trombinoPDF')

        #chemin = "/Users/firos/pdf/%s.pdf" % code
        #dest = file(chemin, "wb")
        pdf = pisa.CreatePDF(src=cStringIO.StringIO(template), dest=dest, encoding="utf-8")
        if pdf.err:
            print pdf.err
        dest.close()

        fp = open(chemin, 'rb')
        data = fp.read()
        fp.close()
        return {"length": str(os.stat(chemin)[6]), "data": data}

    def rechercherCatalogueBU(self, termeRecherche, typeRecherche):
        portal_primo = getToolByName(self, "portal_primo")
        if typeRecherche == "liste":
            resultat = portal_primo.rechercherCatalogueBU(termeRecherche)
        elif typeRecherche == "BU":
            resultat = portal_primo.BUResult(termeRecherche)
        elif typeRecherche == "suggestion":
            resultat = portal_primo.BUacquisition()
        else:
            pass
        return resultat

    def rechercherUserLDAP(self, username, attribut, match=False):
        retour = []
        acl_users = getattr(getattr(getattr(self, "acl_users"), "ldap-plugin"), "acl_users")
        for user in acl_users.findUser(search_param=attribut, search_term=username, exact_match=match):
            if "supannAliasLogin" in user:
                retour.append({"id":    user["supannAliasLogin"],
                               "name":  user["displayName"].decode("iso-8859-1"),
                               "email": user["mail"].decode("iso-8859-1")})
        return json.dumps(retour)

    def setRoleUtilisateurExterieur(self, utilisateur, role, value):
        portal = self.portal_url.getPortalObject()
        if value == "Non":
            portal.acl_users.portal_role_manager.assignRoleToPrincipal(role_id=role, principal_id=utilisateur)
        else:
            portal.acl_users.portal_role_manager.removeRoleFromPrincipal(role_id=role, principal_id=utilisateur)
        #portal_membership = getToolByName(portal, 'portal_membership')
        #portal_registration = getToolByName(portal, 'portal_registration')
        #password = portal_registration.generatePassword()
        #portal_membership.addMember(utilisateur, password, ("EtudiantJalon",), "", {"fullname": "%s %s" % (fullname[0], fullname[1]), "email": form["invitation"]})

    def majFichier(self, fichier):
        items = fichier.getRelatedItems()
        for item in items:
            if item.portal_type in ["JalonCours"]:
                #print "dans if : %s" % fichier.getId()
                #modification du titre dans le cours
                element_cours = copy.deepcopy(item.getElementCours())
                idFichier = fichier.getId()
                if "." in idFichier:
                    idFichier = idFichier.replace(".", "*-*")
                if idFichier in element_cours:
                    element_cours[idFichier]["titreElement"] = fichier.Title()
                    item.setElementsCours(element_cours)
            if item.portal_type in ["JalonBoiteDepot", "JalonCoursWims"]:
                #modification du titre dans les boite de depots
                dico = copy.deepcopy(item.getInfosElement())
                idFichier = fichier.getId()
                if "." in idFichier:
                    idFichier = idFichier.replace(".", "*-*")
                if idFichier in dico:
                    dico[idFichier]["titreElement"] = fichier.Title()
                    #item.setInfos_element(dico)
                    item.setInfosElement(dico)

    def dupliquerCours(self, idcours, creator, manager):
        import time
        home = self
        if manager:
            home = getattr(self.aq_parent, manager)
        try:
           idobj = home.invokeFactory(type_name='JalonCours', id="Cours-%s-%s" % (self.Creator(), DateTime().strftime("%Y%m%d%H%M%S")))
        except:
           time.sleep(1)
           idobj = home.invokeFactory(type_name='JalonCours', id="Cours-%s-%s" % (self.Creator(), DateTime().strftime("%Y%m%d%H%M%S")))
        duplicata = getattr(home, idobj)
        if self.Creator() == creator:
            cours = getattr(self, idcours)
        else:
            cours = getattr(getattr(self.aq_parent, creator), idcours)
        infos_element = copy.deepcopy(cours.getElementCours())

        # On duplique chaque classe de la liste getListeClasses() coté Wims,
        # et on assigne les identifiants des nouvelles classes au cours dupliqué
        listeClasses = cours.getListeClasses()
        new_listeClasses = []
        for dico in listeClasses:
            for auteur in dico:
                classe_id = dico[auteur]
                dico_wims = {"job": "copyclass", "code": self.portal_membership.getAuthenticatedMember().getId(), "qclass": classe_id}
                rep_wims = self.wims("callJob", dico_wims)
                rep_wims = self.wims("verifierRetourWims", {"rep": rep_wims, "fonction": "jalonfolder.py/dupliquerCours", "message": "parametres de la requete : %s" % dico_wims})
                if rep_wims["status"] == "OK":
                    new_listeClasses.append({auteur: rep_wims["new_class"]})

        param = {"Title":                  "%s (Duplicata du %s)" % (cours.Title(), DateTime().strftime("%d/%m/%Y - %H:%M:%S")),
                 "Description":            cours.Description(),
                 "Elements_glossaire":     cours.getGlossaire(),
                 "Elements_bibliographie": cours.getBibliographie(),
                 "ListeClasses":           new_listeClasses
                 }

        duplicata.setProperties(param)
        duplicata.setElementsCours(infos_element)
        duplicata.invokeFactory(type_name='Folder', id="annonce")
        duplicata.invokeFactory(type_name='Ploneboard', id="forum")
        forum = getattr(duplicata, "forum")
        forum.setTitle("Liste des forums du cours")
        duplicata.setPlanCours(copy.deepcopy(cours.getPlan()))

        dicoRep = {"Image":                    "Fichiers",
                   "File":                     "Fichiers",
                   "Page":                     "Fichiers",
                   "Lienweb":                  "Externes",
                   "Lecteurexportable":        "Externes",
                   "Referencebibliographique": "Externes",
                   "CatalogueBU":              "Externes",
                   "Catalogue BU":             "Externes",
                   "TermeGlossaire":           "Glossaire",
                   "Presentationssonorisees":  "Sonorisation"}
        for key in infos_element:
            duplicataObjet = None

            if key.startswith("BoiteDepot"):
                boite = getattr(cours, key, None)
                if boite:
                    duplicata.invokeFactory(type_name="JalonBoiteDepot", id=key)
                    duplicataObjet = getattr(duplicata, key)
                    param = {"Title":            boite.Title(),
                             "Description":      boite.Description(),
                             "DateDepot":        boite.getDateDepot(),
                             "DateRetard":       boite.getDateRetard(),
                             "ListeSujets":      copy.deepcopy(boite.getListeSujets()),
                             "ListeCorrections": copy.deepcopy(boite.getListeCorrections()),
                             "InfosElement":     copy.deepcopy(boite.getInfosElement()),
                             "DateAff":          boite.getDateAff(),
                             "DateMasq":         boite.getDateMasq()}
                    duplicataObjet.setProperties(param)
                else:
                    duplicataObjet = "Invalide"

            # Cas des activités WIMS
            if key.startswith("AutoEvaluation") or key.startswith("Examen"):
                activite = getattr(cours, key, None)
                if activite:
                    duplicata.invokeFactory(type_name="JalonCoursWims", id=key)
                    duplicataObjet = getattr(duplicata, key)
                    duplicataObjet.setJalonProperties(activite.getDicoProperties())
                else:
                    duplicataObjet = "Invalide"

            """
            if key.startswith("Forum"):
                forum = getattr(cours, key, None)
                if forum:
                    duplicata.invokeFactory(type_name="JalonForum", id=key)
                    duplicataObjet = getattr(duplicata, key)
                    param = {"Title":       forum.Title(),
                             "Description": forum.Description(),
                             "DateAff":     forum.getDateAff(),
                             "DateMasq":    forum.getDateMasq()}
                    duplicataObjet.setProperties(param)
                else:
                    duplicataObjet = "Invalide"
            """

            if not duplicataObjet:
                if infos_element[key]["typeElement"] in dicoRep and cours.isInPlan(key):
                    repertoire = dicoRep[infos_element[key]["typeElement"]]
                    if "*-*" in key:
                        ressource = key.replace("*-*", ".")
                    else:
                        ressource = key
                    try:
                        duplicataObjet = getattr(getattr(getattr(getattr(self.portal_url.getPortalObject(), "Members"), infos_element[key]["createurElement"]), repertoire), ressource)
                        relatedItems = duplicataObjet.getRelatedItems()
                        relatedItems.append(duplicata)
                        duplicataObjet.setRelatedItems(relatedItems)
                        duplicataObjet.reindexObject()
                    except:
                        pass

        relatedItems = cours.getRelatedItems()
        duplicata.setRelatedItems(relatedItems)
        duplicata.reindexObject()
        return duplicata.getId()

    #recupére differents éléments génériques defini par l'administrateur dans les configs Jalon
    def getInfosJalonConfiguration(self, info):
        return jalon_utils.getInfosJalonConfiguration(info)

    def getJalonProperty(self, info):
        return jalon_utils.getJalonProperty(info)

    def script_content(self):
        context = aq_inner(self)
        return context.restrictedTraverse('@@quick_upload_init')(for_id=self.uploader_id)

    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

    def tagFormat(self, tagSet):
        return jalon_utils.tagFormat(tagSet)

    def jalon_quote(self, encode):
        return jalon_utils.jalon_quote(encode)

    def jalon_unquote(self, decode):
        return jalon_utils.jalon_unquote(decode)

    def envoyerMail(self, form):
        jalon_utils.envoyerMail(form)

    def envoyerMailErreur(self, form):
        jalon_utils.envoyerMailErreur(form)

    def traductions_fil(self, key):
        return jalon_utils.traductions_fil(key)

    def getInfosConnexion(self):
        return jalon_utils.getInfosConnexion()

    def getFilAriane(self, portal, folder, authMemberId, pageCours=None):
        return jalon_utils.getFilAriane(portal, folder, authMemberId, pageCours)

    def getElementView(self, idElement):
        return jalon_utils.getElementView(self, "MonEspace", idElement)

    ##################
    # transfererExosWIMS()
    # Transfert des exercices WIMS d'un prof "user_source" vers le jalonfolder courant
    # Exemple de script a créer dans la ZMI pour pouvoir utiliser cette fonction par l'admin :
    #       portal = context.portal_url.getPortalObject()
    #       dossierWIMS = getattr(getattr(portal.Members, "id_destination"), "Wims")
    #       return dossierWIMS.transfererExosWIMS("id_source")
    def transfererExosWIMS(self, user_source):
        #On verifie que self est bien un dossier wims.
        if self.getId() != "Wims":
            return {"status": "ERROR", "message": "Cette fonction doit etre appelee depuis un dossier WIMS"}
        portal = self.portal_url.getPortalObject()
        source = getattr(getattr(portal.Members, user_source), "Wims")

        # On demande la liste des exercices WIMS, ce qui aura pour conséquence la création du groupement si celui-ci n'existait pas.
        listeExos = source.objectValues("JalonExerciceWims")

        """
        # Procedure liee aux images WIMS :
        # TODO : Si un dossier d'images existe sur WIMS, il faudrait le transferer également.
        """

        listeSubject = list(self.Subject())
        etiquette = jalon_utils.getDisplayName(user_source)
        etiquette = etiquette.encode("utf-8")
        authMember = self.aq_parent.getId()
        nbExos = 0
        listeSeries = []
        # Une fois le groupement existant, on peut alors y ajouter les exercices.
        for exercice in listeExos:
            idExo = exercice.getId()
            modele = exercice.getModele()
            # Ajout de l'exercice côté Jalon
            self.invokeFactory(type_name='JalonExerciceWims', id=idExo)
            newExo = getattr(self, idExo)
            newExo.manage_setLocalRoles(authMember, ["Owner"])
            newExo.setProperties({"Title": exercice.Title(),
                                  "Modele": modele})

            if modele == "externe":
                newExo.setProperties({"Permalink": exercice.getPermalink()})

            elif modele == "groupe":
                newExo.setProperties({"Qnum":         exercice.getQnum(),
                                      "ListeIdsExos": exercice.getListeIdsExos()})
                listeSeries.append(idExo)
                # on reporte le traitement à plus tard. il faut d'abord que tous les exos soient importés.

            # Cas classique : on ajoute l'exercice côté WIMS
            else:
                fichierWims = self.wims("callJob", {"job": "getexofile", "qclass": "%s_1" % source.getComplement(), "qexo": idExo, "code": authMember})
                try:
                    retourWIMS = json.loads(fichierWims)
                    # Si json arrive a parser la reponse, c'est une erreur. WIMS doit être indisponible.
                    return {"status": "ERROR", "message": "jalonfolder/transfererExosWIMS : Impossible d'ajouter un exercice", "nbExos": nbExos, "user_source": user_source, "user_dest": authMember, "retourWIMS": retourWIMS}
                except:
                    pass
                fichierWims = fichierWims.decode("utf-8").encode("iso-8859-1")
                dico = {"job":    "addexo",
                        "code":   authMember,
                        "data1":  fichierWims,
                        "qexo":   idExo,
                        "qclass": "%s_1" % self.getComplement()}
                json.loads(self.wims("callJob", dico))

            self.setTagDefaut(newExo)
            subject = list(newExo.Subject())
            subject.append(urllib.quote(etiquette))
            newExo.setSubject(subject)

            #Mise à jour des étiquettes du parent
            if not etiquette in listeSubject:
                listeSubject.append(etiquette)
            newExo.reindexObject()

            nbExos = nbExos + 1

        # on reparcourt uniquement les groupes d'exercices, pour pouvoir mettre a jour les "relatedItems"
        for groupe in listeSeries:
            objetGroupe = getattr(self, groupe)
            listeExosGroupe = objetGroupe.getListeIdsExos()

            if len(listeExosGroupe) > 0:
                for exoIdGroupe in listeExosGroupe:
                    exo = getattr(self, exoIdGroupe, None)
                    if exo:
                        relatedItems = exo.getRelatedItems()
                        relatedItems.append(objetGroupe)
                        exo.setRelatedItems(relatedItems)
                        exo.reindexObject()

        self.setSubject(tuple(listeSubject))
        self.reindexObject()

        return {"status": "OK", "message": "import reussi", "nbExos": nbExos, "user_source": user_source, "user_dest": authMember}

    # Lien vers la fonction wims du connecteur dédié
    def wims(self, methode, param):
        #wims = getToolByName(self, "portal_jalon_wims")
        #return wims.call_wims(methode, param)
        wims = getToolByName(self, self.getAttributConf("wims_connecteur"))
        return wims.__getattribute__(methode)(param)

    # Lien vers la fonction wims du connecteur dédié
    def jalonBDD(self, methode, param):
        bdd = getToolByName(self, "portal_jalon_bdd")
        return bdd.__getattribute__(methode)(**param)

    def getIndividu(self, sesame, return_type=None):
        return jalon_utils.getIndividu(sesame, return_type)

    def getIndividus(self, sesame_list, return_type=None):
        return jalon_utils.getIndividus(sesame_list, return_type)

    def isLDAP(self):
        return jalon_utils.isLDAP()

    def getJalonPhoto(self, user_id):
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        return jalon_properties.getJalonPhoto(user_id)

    #   Suppression marquage HTML
    def supprimerMarquageHTML(self, chaine):
        return jalon_utils.supprimerMarquageHTML(chaine)

    #supprimerCaractereSpeciaux
    def supprimerCaractereSpeciaux(self, chaine):
        return jalon_utils.supprimerCaractereSpeciaux(chaine)

    #Intracursus
    def creationSeance(self, codeMatiere, annee, periode, publiable, intitule, typeseance, dateseance, heureseance, dureeseance, avecnote, coefficient):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        return intracursus.creationSeanceServer(codeMatiere, annee, periode, publiable, intitule, typeseance, dateseance, heureseance, dureeseance, avecnote, coefficient)

    def listerSeance(self, codeMatiere):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        retour = intracursus.listerSeanceServer(codeMatiere)
        if retour["status"] == "REUSSITE":
            return retour["listeSeances"]
        return []

    def affichageSeance(self, dico):
        dicoType = {"":         "A définir",
                    "TD":       "Travaux Dirigés",
                    "TP":       "Travaux pratiques",
                    "CM":       "Cours Magistral",
                    "EXAM":     "Examen",
                    "EVAL":     "Evaluation",
                    "PART":     "Partiel",
                    "QCM":      "QCM",
                    "ORAL":     "Oral",
                    "CCI":      "CCI",
                    "CCT":      "CTT",
                    "SOUT":     "Soutenance",
                    "MPART":    "Moyenne Partielle",
                    "CCTEXAM":  "CCT ou Examen Terminal",
                    "EXAMTERM": "Examen Terminal"}
        dico["type"] = dicoType[dico["type"]]
        dico["date"] = DateTime(dico["date"], datefmt='international').strftime("%d/%m/%Y")
        if dico["avecnote"] == '0':
            dico["avecnote"] = False
        else:
            dico["avecnote"] = True
        if dico["publiable"] == '0':
            dico["publiable"] = False
        else:
            dico["publiable"] = True
        return dico

    def connecterPlone(self):
        param = {}
        param["__ac_name"] = "admin1"
        param["__ac_password"] = "azerty1"
        param["ajax_load"] = 1
        data = urllib.urlencode(param)
        try:
            req = urllib2.Request("http://localhost:8081/Plone/zzz_echange/logged_in", data)
            handle = urllib2.urlopen(req, timeout=50)
            rep = handle.read()
        except IOError:
            rep = "ERROR"
        return rep

    def ajouterDossierPlone(self):
        param = {}
        param["__ac_name"] = "admin1"
        param["__ac_password"] = "azerty1"
        param["login"] = "bordonad"
        data = urllib.urlencode(param)
        try:
            req = urllib2.Request("http://localhost:8081/Plone/zzz_echange/ajouterDossier", data)
            handle = urllib2.urlopen(req, timeout=50)
            rep = handle.read()
        except IOError:
            rep = "ERROR"
        return rep

    def isNouveau(self, idcours):
        portal = self.portal_url.getPortalObject()
        portal_catalog = getToolByName(portal, "portal_catalog")
        liste = list(portal_catalog.searchResults(portal_type="JalonCours", id=idcours))
        member = self.portal_membership.getAuthenticatedMember()
        for cours in liste:
            if member.getId() == cours.Creator:
                if cmp(cours.getDateDerniereActu, member.getProperty('login_time', None)) > 0:
                    return True
                return False
            elif cmp(cours.getDateDerniereActu, self.getLastLogin()) > 0:
                return True
        return False

    def isSameServer(self, url1, url2):
        return jalon_utils.isSameServer(url1, url2)

    def isPersonnel(self, user, mode_etudiant="false"):
        #self.plone_log("isPersonnel")
        if mode_etudiant == "true":
            return False
        if user.has_role(["Manager", "Personnel"]):
            return True
        return False

    def getLastLogin(self):
        member = self.portal_membership.getAuthenticatedMember()
        last_login = member.getProperty('last_login_time', None)
        if isinstance(last_login, basestring):
            last_login = DateTime(last_login)
        return last_login

    def getJalonMenu(self, portal_url, user, request):
        return jalon_utils.getJalonMenu(self, portal_url, user, request)

    def getFooter(self):
        return jalon_utils.getFooter()

    def gaEncodeTexte(self, chemin, texte):
        return jalon_utils.gaEncodeTexte(chemin, texte)

    #def setFullname(self, member, fullname):
    #    jalon_utils.setFullname(member, fullname)

# enregistrement dans la registery Archetype
registerATCT(JalonFolder, PROJECTNAME)
