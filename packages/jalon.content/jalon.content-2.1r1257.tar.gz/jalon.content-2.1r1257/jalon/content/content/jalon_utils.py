# -*- coding: utf-8 -*-

from zope.component import getUtility

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from jalon.content.browser.config.jalonconfig import IJalonConfigControlPanel
from jalon.content.browser.config.jalonconfiguration import IJalonConfigurationControlPanel
from jalon.content import contentMessageFactory as _
from jalon.content.content import jalon_encode

from datetime import datetime
from DateTime import DateTime

import smtplib

from email import message_from_string
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Header import Header
import email.Utils

from urlparse import urlparse
import urllib
import urllib2
import feedparser
import locale
import json
import re
import copy

# Messages de debug :
from logging import getLogger
LOG = getLogger( '[jalon.content.jalon_utils]' )
"""
# Log examples :
LOG.debug('debug message')
LOG.info('info message')
LOG.warn('warn message')
LOG.error('error message')
LOG.critical('critical message')
"""


# AuthUser WIMS : permet d'authentifier "quser" dans une classe wims "qclass"
# request représente les parametres envoyés à la page (GET/POST)
# session_keep permet de définir si on réutilise une eventuelle session wims existante ou pas.
def authUser(context, quser=None, qclass=None, request=None, session_keep=False):
    remote_addr = None
    url_connexion = context.wims("getAttribut", "url_connexion")
    if request:
        # HTTP_X_REAL_IP n'existe que si la configuration de Nginx fournit bien ce parametre à Zope.
        remote_addr = request.get('HTTP_X_REAL_IP', None)
        if not remote_addr:
            remote_addr = request['REMOTE_ADDR']

        if session_keep == True:
            #Si session_keep=True et qu'une session wims était déjà ouverte, on la conserve.
            # Attention : ici il faudrait vérifier sur WIMS que la session ouverte était bien celle de l'utilisateur courant.
            wims_session = request.get('wims_session', None)
            if wims_session:
                return {'wims_session':wims_session,
                        'status':'OK',
                        'home_url':"%s?session=%s"%(url_connexion, wims_session)}
    dico = {"qclass": qclass, "quser": quser, "code": quser, "option": "lightpopup", "data1": remote_addr}
    rep = context.wims("authUser", dico)
    try:
        rep = json.loads(rep)
        #rep = context.wims("verifierRetourWims", {"rep": rep, "fonction": "jalon.content/jalon_utils.py/authUser", "message": "1ere identification de l'utilisateur %s." % quser, "requete": dico})
    except ValueError, e:
            rep = '{"status":"ERROR","exception_raised":"%s","message":"%s"}' % (string_for_json(rep), e)
            rep = json.loads(rep)

    if rep["status"] == "ERROR":
        # On prépare un éventuel message d'erreur à renvoyer
        message = _(u"Le serveur WIMS est actuellement injoignable. Merci de réessayer ultérieurement svp...")
        mess_type = "error"
        if quser != 'supervisor':
            # Sur une premiere erreur, on considere que l'utilisateur est inexistant. on tente alors de le créer.
            dico_ETU = getIndividu(quser, type="dict")
            if dico_ETU:
                firstname = dico_ETU["prenom"]
                lastname = dico_ETU["nom"]
            else:
                fullname = getDisplayName(quser, request)
                firstname, lastname = fullname.split(" ", 1)

            user = context.wims("creerUser", {"quser": quser, "qclass": qclass, "firstname": firstname, "lastname": lastname})
            if user["status"] == "ERROR":
                # Si la creation de l'utilisateur plante, alors WIMS doit être indisponible.
                context.plone_utils.addPortalMessage(message, type=mess_type)
                return None
            rep = context.wims("authUser", {"qclass": qclass, "quser": quser, "code": quser, "option": "lightpopup", "remote_addr": remote_addr})
            rep = context.wims("verifierRetourWims", {"rep": rep, "fonction": "jalon.content/jalon_utils.py/authUser", "message": "impossible d'authentifier l'utilisateur %s. (Sur 2e essai)" % quser, "requete": dico})
        else:
            # L'authentification du supervisor a planté => WIMS doit être indisponible.
            context.plone_utils.addPortalMessage(message, type=mess_type)
            return None
    rep["url_connexion"] = url_connexion
    return rep


# string_for_json : Supprime tous les caracteres indesirables d'une chaine pour l'integrer au format JSON (quotes, retour chariot, barre oblique )
def string_for_json(self, chaine):
    return chaine.replace('\"', "'").replace('\n', "").replace("\\", "")


# callUrl()
def callUrl(context, url, param):
    data = urllib.urlencode(param)
    req = urllib2.Request(url, data)
    return urllib2.urlopen(req)


# convertirDate()
def convertirDate(date):
    return DateTime(date, datefmt='international').strftime("%d/%m/%Y %H:%M")


# convertLangToWIMS : Converti un code de langue Plone en code de langue WIMS.
def convertLangToWIMS(portal_lang):
    if portal_lang == "zh-cn":
        # Sur Wims, "cn" doit remplacer le code "zh-cn" de Jalon
        portal_lang = "cn"
    return portal_lang


#encodeUTF8()
def encodeUTF8(itemAEncoder):
    try:
        return [str(encoder).encode("utf-8") for encoder in itemAEncoder]
    except:
        return itemAEncoder


######
#   envoyerMail(form)
#   envoie un email selon les parametres spécifiés
def envoyerMail(form):
    portal = getUtility(IPloneSiteRoot)
    jalon_properties = getToolByName(portal, "portal_jalon_properties")
    mail_properties = jalon_properties.getPropertiesCourriels()
    if "auteur" in form:
        message = "Message envoyé par %s depuis le cours %s\n\n%s" % (form["auteur"], form["cours"], form["message"])
    else:
        message = form["message"]

    if not "de" in form:
        form["de"] = portal.getProperty("email_from_address")
    if not "a" in form:
        if mail_properties["activer_email_erreur"]:
            form["a"] = mail_properties["adresse_email_erreur"]
        else:
            form["a"] = portal.getProperty("email_from_address")

    my_message = message_from_string(message)
    my_message.set_charset('utf-8')
    my_message['Subject'] = Header("[%s] %s" % (portal.Title(), form["objet"]), charset="utf-8")
    my_message['To'] = form["a"]
    my_message['From'] = portal.getProperty("email_from_address")
    my_message['Reply-To'] = form["de"]
    my_message['Date'] = email.Utils.formatdate(localtime=True)

    portal.MailHost.send(my_message,
                         mto=form["a"],
                         mfrom=portal.getProperty("email_from_address"),
                         subject="[%s] %s" % (portal.Title(), form["objet"]),
                         encode=None, immediate=False, charset='utf8', msg_type="text/html")


######
#   envoyerMailErreur(form)
#   envoie un email de signalement d'erreur à l'administrateur
def envoyerMailErreur(form):
    portal = getUtility(IPloneSiteRoot)
    jalon_properties = getToolByName(portal, "portal_jalon_properties")
    mail_properties = jalon_properties.getPropertiesCourriels()
    if mail_properties["activer_erreur"]:
        if not "de" in form:
            if mail_properties["activer_email_erreur"]:
                form["de"] = mail_properties["adresse_email_erreur"]
            else:
                form["de"] = portal.getProperty("email_from_address")
        if not "a" in form:
            if mail_properties["activer_email_erreur"]:
                form["a"] = mail_properties["adresse_email_erreur"]
            else:
                form["a"] = portal.getProperty("email_from_address")

        if "entry" in form:
            #error_log = portal.error_log
            #entries = error_log.getLogEntries()

            dico = {}
            entry = portal.error_log.getLogEntryById(form["entry"])
            if not entry:
                text = ""
            else:
                dico['date'] = DateTime(entry['time'])
                dico['username'] = "%s (%s)" % (entry['username'], entry['userid'])
                dico['url'] = entry['url']
                dico['type'] = entry['value']
                dico['value'] = entry['value']

                try:
                    dico['traceback'] = entry['tb_html']
                except:
                    dico['traceback'] = entry['tb_text']
                dico['request'] = entry['req_html']

                text = "\n\n".join(["Traceback", dico['traceback'], "Request", dico['request']])
            if (not "__ac" in text) or (not "__accas" in text):
                text = None
        else:
            text = form["message"]
        if text:
            # Create the enclosing (outer) message
            outer = MIMEMultipart()
            outer['Subject'] = Header(form["objet"], charset="utf-8")
            outer['To'] = form["a"]
            outer['From'] = form["de"]
            outer['Reply-To'] = form["de"]
            outer['Date'] = email.Utils.formatdate(localtime=True)
            outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
            # To guarantee the message ends with a newline
            outer.epilogue = ''

            # définition du message du mail
            msg = MIMEText(text, 'html', _charset="UTF-8")
            outer.attach(msg)

            # Now send the message
            s = smtplib.SMTP()
            s.connect(portal.MailHost.smtp_host, portal.MailHost.smtp_port)
            if portal.MailHost.smtp_uid:
                s.starttls()
                s.login(portal.MailHost.smtp_uid, portal.MailHost.smtp_pwd)

            s.sendmail(form["de"], form["a"], outer.as_string())

            s.close()


#fonction qui permet de recupérer un des liens url défini par l'administrateur dans les configs Jalon
#def getInfosJalonConfiguration(info):
#    portal = getUtility(IPloneSiteRoot)
#    jalon_conf = IJalonConfigurationControlPanel(portal)
#    return jalon_conf.getInfosConfiguration(info)


def getJalonProperty(key):
    portal = getUtility(IPloneSiteRoot)
    jalon_properties = getToolByName(portal, "portal_jalon_properties")
    if key.startswith("activer_"):
        return int(jalon_properties.getJalonProperty(key))
    return jalon_properties.getJalonProperty(key)


# flatten()
def flatten(lst):
    for elem in lst:
        if type(elem) in (tuple, list):
            for i in flatten(elem):
                yield i
        else:
            yield elem


#getClefsDico()
def getClefsDico(dico):
    clefs = dico.keys()
    clefs.sort()
    return clefs


#getDisplayName() permet d'obtenir le nom (+prenom) d'un utilisateur
# request est utilisé dans le cas d'utilisateurs sygefor
def getDisplayName(user_id, request=None, portal=None):
    if portal == None:
        portal = getUtility(IPloneSiteRoot)
    member = portal.portal_membership.getMemberById(user_id)
    fullname = None
    if member:
        if member.has_role(["Personnel", "Etudiant", "Manager"]):
            fullname = member.getProperty("fullname")
        if (not fullname) and member.has_role(["Personnel", "Etudiant"]):
            fullname = member.getProperty("displayName")
        if not fullname:
            sygefor = getattr(portal.acl_users, "sygefor", None)
            if sygefor:
                result = sygefor.getPropertiesForUser(user_id, request)
                if result:
                    fullname = result.getProperty("fullname")
            if not fullname:
                fullname = "%s %s" % (user_id, user_id)
    else:
        fullname = "utilisateur introuvable"
    return fullname


# getIndividu renvoie l'ensemble des infos disponibles (nom, prenom, mail, etc...) pour un sesame (login) en entree
# Si l'individu n'existe pas dans la base, il ne sera pas renvoyé.
# si type="dict", les infos sont retraitées sous forme de dico.
def getIndividu(sesame, type=None, portal=None):
    if portal is None:
        portal = getUtility(IPloneSiteRoot)
    bdd = getToolByName(portal, 'portal_jalon_bdd')
    # retour de  getIndividuLITE :[[IND.LIB_NOM_PAT_IND,
    #                               IND.LIB_PR1_IND,
    #                               IND.SESAME_ETU,
    #                               IND.COD_ETU,
    #                               IND.EMAIL_ETU]]
    individu = bdd.getIndividuLITE(sesame)
    if type == "dict":
        if individu:
            #individu = individu[0]
            dico = {"sesame": sesame,
                    "nom": individu["LIB_NOM_PAT_IND"],
                    "prenom": individu["LIB_PR1_IND"],
                    "num_etu": individu["COD_ETU"],
                    "email": individu["EMAIL_ETU"]}
            return dico
        return None

    return individu


# getIndividus renvoie l'ensemble des infos disponibles (nom, prenom, mail, etc...) pour la liste des sesames (logins) en entree
# Si un individu n'existe pas dans la base, il ne sera pas renvoyé.
# si type="dict", les infos sont retraitées sous forme de dico.
def getIndividus(listeSesames, type=None, portal=None):
    if portal is None:
        portal = getUtility(IPloneSiteRoot)
    bdd = getToolByName(portal, 'portal_jalon_bdd')
    #bdd = portal.portal_apogee
    recherche = bdd.getIndividus(listeSesames)
    if not type:
        return recherche
    if type == "dict":
        retour = {}
        for individu in recherche:
            retour[individu[2]] = {"nom":     individu[0],
                                   "prenom":  individu[1],
                                   "num_etu": individu[3],
                                   "email":   individu[4],
                                   "type":    individu[5]}
    if type == "listdict":
        retour = []
        for individu in recherche:
            retour.append({"sesame":  individu[2],
                           "nom":     individu[0],
                           "prenom":  individu[1],
                           "num_etu": individu[3],
                           "email":   individu[4],
                           "type":    individu[5]})
    return retour


def getLocaleDate(date, format="%d/%m/%Y"):
    locale.setlocale(locale.LC_ALL, 'fr_FR')
    return DateTime(date).strftime(format)


def getConnectDate(data, sortable=False):
    if not sortable:
        return data.split(' - ')[0].replace('.', '/')
    else:
        dateList = data.replace('h', '').split(' - ')
        return ''.join(dateList[0].split('.')[::-1]) + dateList[1]


# Renvoit TRUE si le serveur de l'url "url1" est identique à celui de l'URL "url2"
def isSameServer(url1, url2):
    server1 = urlparse(url1)
    server2 = urlparse(url2)
    return server1.netloc == server2.netloc


def getDepotDate( data, sortable = False ):
    if not sortable:
        return data.replace( ' -', '' )
    else:
        dateList = data.replace( 'h', '' ).split( ' - ' )
        return ''.join( dateList[0].split( '/' )[::-1])  + dateList[1]


def getPhotoTrombi(login):
    #here.portal_membership.getPersonalPortrait(creator)
    # à mettre en config admin
    req = urllib2.Request("http://camus.unice.fr/unicampus/images/Photos/%sApog0060931E.jpg" % login)
    req.add_header("Expires", "Mon, 26 Jul 1997 05:00:00 GMT")
    req.add_header("Last-Modified", datetime.today())
    req.add_header("Cache-Control", "no-store, no-cache, must-revalidate, post-check=0, pre-check=0")
    req.add_header("Pragma", "no-cache")
    req.add_header("Content-type", "image/jpeg")

    try:
        r = urllib2.urlopen(req)
        return r.read()
    except:
        return None


# getBaseAnnuaire :
def getBaseAnnuaire():
    portal = getUtility(IPloneSiteRoot)
    portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
    fiche_ldap = portal_jalon_properties.getPropertiesDonneesUtilisateurs("fiche_ldap")
    # fiche_ldap correspond au champ "Chemin vers une fiche de votre annuaire" des configs Jalon
    if "*-*" in fiche_ldap:
        liste = fiche_ldap.split("*-*")
        if len(liste) > 2:
            return {"base": liste[0],
                    "variable": liste[1],
                    "fin": liste[2]}
        return {"base": liste[0],
                "variable": liste[1],
                "fin": ""}

    return {"base": fiche_ldap,
            "variable": "",
            "fin": ""}


def getFicheAnnuaire(valeur, base=None):
    if not base:
        base = getBaseAnnuaire()
    return "".join([base['base'], valeur[base["variable"]], base["fin"]])


def getInfosConnexion():
    portal = getUtility(IPloneSiteRoot)
    jalon_configuration = IJalonConfigurationControlPanel(portal)
    return {"site":          portal.Title(),
            "lien_sesame":   jalon_configuration.get_lien_sesame(),
            "etablissement": jalon_configuration.get_etablissement()}


def getInfosMembre(username):
    portal = getUtility(IPloneSiteRoot)
    portal_membership = getToolByName(portal, "portal_membership")
    member = portal_membership.getMemberById(username)
    if member:
        fullname = member.getProperty("fullname")
        if not fullname:
            fullname = username
        email = member.getProperty("email")
        if not email:
            email = username
    else:
        fullname = email = str(username)
        """
        portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")
        individu = portal_jalon_bdd.getIndividuLITE(username)
        if individu:
            fullname = "%s %s" % (individu["LIB_NOM_PAT_IND"], individu["LIB_PR1_IND"])
            email = individu["EMAIL_ETU"]
        """
    #    member = rechercherUtilisateur(username, "supannAliasLogin", match=True, isJson=False)
    #    try:
    #        fullname = member[0]["name"]
    #        email = member[0]["email"]
    #    except:
    #        fullname = email = username
    try:
        fullname = fullname.encode('utf-8')
    except:
        pass
    return {"id":       username,
            "fullname": fullname,
            "email":    email,
            "nom":      fullname.strip().rsplit(" ", 1)[-1]}


def rechercherUtilisateur(username, typeUser, match=False, isJson=True):
    portal = getUtility(IPloneSiteRoot)
    retour = []
    """
    if isLDAP() and typeUser == "Personnel":
        portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
        schema = portal_jalon_properties.getJalonProperty("schema_ldap")
        if schema == "supann":
            ldap = "ldap-plugin"
            if typeUser == "Etudiant":
                ldap = "ldap-plugin-etu"
            retour = rechercherUserLDAPSupann(username, "displayName", ldap, match)
        if schema == "eduPerson":
            retour = rechercherUserLDAPEduPerson(username, "displayName", "ldap-plugin", match)
    else:
    """
    portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")
    retour = portal_jalon_bdd.rechercherUtilisateursByName(username, typeUser)
    if isJson:
        return json.dumps(retour)
    return retour


def rechercherUserLDAPSupann(username, attribut, ldap="ldap-plugin", match=False):
    retour = []
    portal = getUtility(IPloneSiteRoot)
    acl_users = getattr(getattr(getattr(portal, "acl_users"), ldap), "acl_users")
    for user in acl_users.findUser(search_param=attribut, search_term=username, exact_match=match):
        if "supannAliasLogin" in user:
            email = user["supannAliasLogin"]
            if "mail" in user:
                email = user["mail"].decode("iso-8859-1")
            retour.append({"id":    user["supannAliasLogin"],
                           "name":  user["displayName"].decode("iso-8859-1"),
                           "email": email})
    return retour


def rechercherUserLDAPEduPerson(username, attribut, ldap="ldap-plugin", match=False):
    retour = []
    portal = getUtility(IPloneSiteRoot)
    eduPersonAffiliation = ["employee", "faculty"]
    if ldap == "ldap-plugin-etu":
        eduPersonAffiliation = ["student"]
    acl_users = getattr(getattr(getattr(portal, "acl_users"), ldap), "acl_users")
    for user in acl_users.findUser(search_param=attribut, search_term=username, exact_match=match):
        if "login" in user and user["eduPersonAffiliation"] in eduPersonAffiliation:
            email = user["login"]
            if "mail" in user:
                email = user["mail"].decode("iso-8859-1")
            retour.append({"id":    user["login"],
                           "name":  user["displayName"].decode("iso-8859-1"),
                           "email": email})
    return retour


#def getPropertiesBIE(key=None):
#    portal = getUtility(IPloneSiteRoot)
#    portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
#    return portal_jalon_properties.getPropertiesMessages(key)


##
#   Troncature de texte :
#       - suppression des espaces multiples ;
#       - remplacement des sauts de ligne, retours chariot et tabulations par des espaces ;
#       - coupure entre les mots avec prise en compte de la ponctuation et des espaces insécables ;
#       - tronçonnage simple si la partie à conserver de la chaîne ne contient aucun espace.
#
def getShortText( text, limit = 75, suffix = '…'):
    text = re.sub( r'\s+', r' ', text.strip( ) )
    if len( text ) > limit:
        text = text[:limit+1]
        if text.find( ' ' ) > -1:
            text = ' '.join( text.split( ' ' )[0:-1] )
            limit = len( text )
        """
        En python v3 on pourra essayer  return re.sub( r'[?!:.,;\-"\'…“”«» ]+$', r'', text ) + suffix
        car ça crée des problèmes d'encodage en v2.
        En v2 on peut utiliser          return re.sub( r'[?!:.,;\-"\']+$', r'', text ) + suffix
        mais c'est incomplet d'où les quatre lignes suivantes.
        """
        punctSigns = [ '?', '!', ':', '.', ',', ';', '-', '…', '"', '“', '”', '«', '»', ' ' ]
        while ( text[limit-1:limit] in punctSigns ):
            limit = limit - 1
        return text[0:limit].strip( ) + suffix
    else:
        return text


def isLDAP():
    portal = getUtility(IPloneSiteRoot)
    portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
    return portal_jalon_properties.getPropertiesDonneesUtilisateurs("activer_ldap")


def setTag(context, tag):
    if not tag in context.Subject():
        tags = list(context.Subject())
        tags.append(tag)
        context.setSubject(tuple(tags))
        context.reindexObject()


#   Suppression marquage HTML
def supprimerMarquageHTML(chaine):
    return re.sub('<[^<]+?>', '', chaine)


#supprimerCaractereSpeciaux : renvoie une chaine ne comprenant que les caracteres alphanumeriques (avec ou sans accents ?).
def supprimerCaractereSpeciaux(chaine):
    return re.sub('[^\w]', '', chaine)


def test(condition, valeurVrai, valeurFaux):
    return valeurVrai if condition else valeurFaux


def tagFormat(tagSet):
    tagList = tagSet.split(',')
    if 'last' in tagList:
        tagList.remove('last')
    if len(tagList) > 0:
        return ','.join(tagList)
    else:
        return None


def jalon_quote(encode):
    return urllib.quote(encode)

"""
jalon_unquote
 Replace %xx escapes by their single-character equivalent.
 Example: unquote('/%7Econnolly/') yields '/~connolly/'.
"""
def jalon_unquote(decode):
    return urllib.unquote(decode)


def jalon_urlencode(chaine):
    return urllib.urlencode(chaine)


def jalon_rss():
    portal = getUtility(IPloneSiteRoot)
    jalon_conf = IJalonConfigControlPanel(portal)
    url_maj = jalon_conf.get_url_maj()
    #print url_maj
    #url  = "http://wiki.unice.fr/createrssfeed.action?types=blogpost&sort=created&showContent=true&showDiff=true&spaces=JALON&labelString=maj_jalon&rssType=rss2&maxResults=1000&timeSpan=1000&publicFeed=true&title=Mises+%C3%A0+jour+de+l%27Environnement+P%C3%A9dagogique+Jalon"
    try:
        f = feedparser.parse(url_maj)
    except:
        print "Une erreur"
        return None

    if len(f['entries']) > 0:
        return f['entries'][0]
    print "Aucune entrées"
    return None


def isAfficherElement(affElement, masquerElement):
    if not affElement:
        return {"val": 0, "icon": "fa-eye-slash", "icon2": "", "legende": "affichage non programmé"}
    if cmp(DateTime(), affElement) == -1:
        return {"val": 0, "icon": "fa-eye-slash", "icon2": "fa-calendar-o success", "legende": "affichage programmé au %s" % getLocaleDate(affElement, format="%d/%m/%Y à %Hh%M")}
    if not masquerElement:
        return {"val": 1, "icon": "", "icon2": "", "legende": "masquage non programmé"}
    if cmp(masquerElement, DateTime()) == -1:
        return {"val": 0, "icon": "fa-eye-slash", "icon2": "", "legende": "masquage programmé et depassé"}
    return {"val": 1, "icon": "", "icon2": "fa-calendar-o alert", "legende": "masquage programmé au %s" % getLocaleDate(masquerElement, format="%d/%m/%Y à %Hh%M")}


def retirerEspace(mot):
    motSansEspace = mot.strip()
    motSansEspace = motSansEspace.replace(" ", "")
    motSansEspace = motSansEspace.replace("%20", "")
    return motSansEspace


def getFilAriane(portal, folder, authMemberId, page=None):
    url_portal = portal.absolute_url()
    #print "jalon_utils/getFilAriane folder.getId() = %s" %folder.getId()

    if authMemberId != None:
        # Cas d'un utilisateur connecté
        dico_mes_cours = {"titre": _(u"Mes cours"),
                          "icone": "fa fa-university",
                          "url":   "%s/cours/%s" % (url_portal, authMemberId)}
    else:
        # Cas d'un utilisateur anonyme dans un cours public
        dico_mes_cours = {"titre": portal.Title(),
                          "icone": "fa fa-university",
                          "url":   url_portal}

    if folder.getId().startswith("Cours"):
        if not page:
            return [dico_mes_cours,
                    {"titre": folder.Title(),
                     "icone": "fa fa-book"}]
        if page == "pref":
            return [dico_mes_cours,
                    {"titre": folder.Title(),
                     "icone": "fa fa-book",
                     "url"  : folder.absolute_url()},
                    {"titre": "Accès et options",
                     "icone": "fa fa-cogs"}]
        if page == "annonces":
            return [dico_mes_cours,
                    {"titre": folder.Title(),
                     "icone": "fa fa-book",
                     "url"  : folder.absolute_url()},
                    {"titre": "Toutes les annonces",
                     "icone": "fa fa-bullhorn"}]
        if page == "actualites":
            return [dico_mes_cours,
                    {"titre": folder.Title(),
                     "icone": "fa fa-book",
                     "url"  : folder.absolute_url()},
                    {"titre": "Toutes les nouveautés",
                     "icone": "fa fa-bell-o"}]

    liste = [dico_mes_cours,
             {"titre": folder.aq_parent.title_or_id(),
              "icone": "fa fa-book",
               "url":   folder.aq_parent.absolute_url()}]

    if folder.getId().startswith("BoiteDepot"):
        liste.append({"titre": folder.Title(),
                      "icone": "fa fa-inbox"})
        return liste

    if folder.getId().startswith("AutoEvaluation"):
        if page == "auto":
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-gamepad",
                          "url"  : folder.absolute_url()})
            liste.append({"titre": "Exercice(s)",
                          "icone": "fa fa-random"})
        if not page:
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-gamepad"})
        return liste

    if folder.getId().startswith("Examen"):
        #print "jalon_utils/getFilAriane page = %s" % page
        if page in ["examen","auto"]:
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-graduation-cap",
                          "url"  : folder.absolute_url()})
            liste.append({"titre": "Examen en cours",
                          "icone": "fa fa-graduation-cap"})
        if not page:
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-graduation-cap"})
        return liste

    if folder.meta_type == "Ploneboard":
        if page == "jalon_forum_search":
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-comments",
                          "url":   folder.absolute_url()})
            liste.append({"titre": "Recherche",
                          "icone": "fa fa-search"})
            return liste
        if page == "ploneboard_recent":
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-comments",
                          "url":   folder.absolute_url()})
            liste.append({"titre": "Activité récente",
                          "icone": "fa fa-comment"})
            return liste
        if page == "ploneboard_unanswered":
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-comments",
                          "url":   folder.absolute_url()})
            liste.append({"titre": "Conversations sans réponse",
                          "icone": "fa fa-comment-o"})
            return liste
        liste.append({"titre": folder.Title(),
                      "icone": "fa fa-comments"})
        return liste

    if folder.meta_type == "PloneboardForum":
        if page == "ploneboard_unanswered":
            liste.append({"titre": folder.aq_parent.aq_parent.title_or_id(),
                          "icone": "fa fa-book",
                          "url"  : folder.aq_parent.aq_parent.absolute_url()})
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-comments",
                          "url"  : folder.absolute_url()})
            liste.append({"titre": "Conversations sans réponse",
                          "icone": "fa fa-comment-o"})
            return liste
        return [dico_mes_cours,
                {"titre": folder.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-book",
                 "url":   folder.aq_parent.aq_parent.absolute_url()},
                {"titre": folder.aq_parent.title_or_id(),
                 "icone": "fa fa-comments",
                 "url":   folder.aq_parent.absolute_url()},
                {"titre": folder.Title(),
                 "icone": "fa fa-comments"}]

    if folder.meta_type == "PloneboardConversation":
        return [dico_mes_cours,
                {"titre": folder.aq_parent.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-book",
                 "url":   folder.aq_parent.aq_parent.aq_parent.absolute_url()},
                {"titre": folder.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-comments",
                 "url":   folder.aq_parent.aq_parent.absolute_url()},
                {"titre": folder.aq_parent.title_or_id(),
                 "icone": "fa fa-comments",
                 "url":   folder.aq_parent.absolute_url()},
                {"titre": folder.Title(),
                 "icone": "fa fa-comments-o"}]

    if folder.meta_type == "PloneboardComment":
        return [dico_mes_cours,
                {"titre": folder.aq_parent.aq_parent.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-book",
                 "url":   folder.aq_parent.aq_parent.aq_parent.aq_parent.absolute_url()},
                {"titre": folder.aq_parent.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-comments",
                 "url":   folder.aq_parent.aq_parent.aq_parent.absolute_url()},
                {"titre": folder.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-comments",
                 "url":   folder.aq_parent.absolute_url()},
                {"titre": folder.Title(),
                 "icone": "fa fa-comments-o"}]

    if folder.meta_type == "JalonExerciceWims":
        return [{"titre": _(u"Mon espace"),
                 "icone": "fa fa-home",
                 "url":   url_portal},
                {"titre": _(u"Exercices Wims"),
                 "icone": "fa fa-random",
                 "url":   folder.aq_parent.absolute_url()},
                {"titre": folder.Title(),
                 "icone": "fa fa-random"}]

    if folder.getId() == "portal_jalon_properties":
        liste = []
        if not page:
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs"})
        if page == "gestion_connexion":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Connexion à Jalon"),
                          "icone": "fa fa-key"})
        if page == "gestion_mon_espace":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Gestion \"Mon Espace\""),
                          "icone": "fa fa-home"})
        if page == "gestion_mes_cours":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Gestion deses Cours"),
                          "icone": "fa fa-university"})
        if page == "gestion_infos":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Liens d'informations"),
                          "icone": "fa fa-external-link-square"})
        if page == "gestion_didacticiels":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Didacticiels"),
                          "icone": "fa fa-life-ring"})
        if page == "gestion_messages":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Diffusion de messages"),
                          "icone": "fa fa-newspaper-o"})
        if page == "gestion_email":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Courriels"),
                          "icone": "fa fa-envelope-o"})
        if page == "gestion_donnees_utilisateurs":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Données utilisateurs"),
                          "icone": "fa fa-users"})
        if page == "gestion_ga":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Google Analytics"),
                          "icone": "fa fa-line-chart"})
        if page == "gestion_maintenance":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Maintenance"),
                          "icone": "fa fa-fire-extinguisher"})
        return liste

    if folder.getId() == "portal_jalon_bdd":
        liste = []
        if page:
            liste.append({"titre": _(u"Gestion pédagogique"),
                          "icone": "fa fa-database",
                          "url"  : "%s/@@jalon-bdd?gestion=gestion_bdd" % folder.absolute_url()})
            liste.append({"titre": page.encode("utf-8"),
                          "icone": "fa fa-database"})
        if not page:
            liste.append({"titre": _(u"Gestion pédagogique"),
                          "icone": "fa fa-database"})
        return liste

    fil = {portal.getId():  [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home"}],
           "Fichiers":      [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Fichiers"),
                              "icone": "fa fa-files-o"}],
           "Sonorisation":  [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Présentations sonorisées"),
                              "icone": "fa fa-microphone"}],
           "Wims":          [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Exercices Wims"),
                              "icone": "fa fa-random"}],
           "Externes":      [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Ressources externes"),
                              "icone": "fa fa-external-link"}],
           "Glossaire":     [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Terme de glossaire"),
                              "icone": "fa fa-font"}],
           "Webconference": [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Webconférences"),
                              "icone": "fa fa-headphones"}],
           "Video":         [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Vidéos"),
                              "icone": "icone_video"}],
            authMemberId:   [{"titre": _(u"Mes cours"),
                              "icone": "fa fa-university"}],
            "etudiants":    [{"titre": _(u"Mes étudiants"),
                              "icone": "fa fa-users"}],
            "portal_jalon_properties": [{"titre": _(u"Configuration du site"),
                                         "icone": "fa fa-wrench"}]
          }
    if not folder.getId() in fil:
        return [dico_mes_cours]
    return fil[folder.getId()]


def getElementView(context, typeContext, idElement, createurElement=None, typeElement=None, indexElement=None, mode_etudiant=None):
    portal = context.portal_url.getPortalObject()
    retour = {"titreElement"       : "",
              "descriptionElement" : "",
              "urlElement"         : "",}

    if "*-*" in idElement:
        idElement = idElement.replace("*-*", ".")

    if typeContext == "Cours":
        retour["indexElement"] = indexElement

        typeElement = typeElement.replace("%20", "")
        typeElement = typeElement.replace(" ", "")

        if typeElement in ["AutoEvaluation", "BoiteDepot", "Examen", "Forum"]:
            boite = getattr(context, idElement)
            retour["titreElement"] = boite.Title()
            retour["descriptionElement"] = boite.Description().replace("\n", "<br/>")
            if typeElement == "AutoEvaluation":
                retour["urlElement"] = "%s/%s/cours_wims_view?mode_etudiant=%s" % (context.absolute_url(), idElement, mode_etudiant)
            if typeElement == "BoiteDepot":
                retour["urlElement"] = "%s/%s?mode_etudiant=%s" % (context.absolute_url(), idElement, mode_etudiant)
            if typeElement == "Examen":
                retour["urlElement"] = "%s/%s/cours_wims_view?mode_etudiant=%s" % (context.absolute_url(), idElement, mode_etudiant)
            if typeElement == "Forum":
                retour["urlElement"] = "%s/%s?section=forum" % (context.absolute_url(), idElement)
            return retour
        if typeElement == "SalleVirtuelle":
            infos_element = context.getElementCours(idElement)
            retour["titreElement"] = infos_element["titreElement"]
            retour["urlElement"] = context.getWebconferenceUrlById(createurElement, idElement)
            return retour
        if typeElement == "Glossaire":
            retour["idElement"] = context.getId()
            retour["titreElement"] = "Glossaire"
            retour["urlElement"] = "%s/cours_glossaire_view" % context.absolute_url()
            return retour

        dicoRep = {"File"                     : "Fichiers",
                   "Image"                    : "Fichiers",
                   "Page"                     : "Fichiers",
                   "ExercicesWims"            : "Wims",
                   "Lienweb"                  : "Externes",
                   "Lecteurexportable"        : "Externes",
                   "CatalogueBU"              : "Externes",
                   "Presentationssonorisees"  : "Sonorisation",
                   "TermeGlossaire"           : "Glossaire",
                  }

        if typeElement in dicoRep:
            rep = dicoRep[typeElement]
        else:
            rep = typeElement

        home = getattr(getattr(portal.Members, createurElement), rep, None)
    else:
        home = context

    if home:
        element = getattr(home, idElement, None)
        if not typeElement:
            typeElement = element.portal_type
            if typeElement == "JalonRessourceExterne":
                typeElement = element.getTypeRessourceExterne()
                typeElement = typeElement.replace("%20", "")
                typeElement = typeElement.replace(" ", "")
            if typeElement == "JalonTermeGlossaire":
                typeElement = "TermeGlossaire"
        if element:
            retour["idElement"] = element.getId()
            retour["titreElement"] = element.Title()
            retour["descriptionElement"] = element.Description().replace("\n", "<br/>")
            retour["urlElement"] = element.absolute_url()
            retour["typeElement"] = typeElement
            if typeElement == 'File':
                retour["urlElement"] = '%s/at_download/file' % element.absolute_url()
            if typeElement == 'Page':
                retour["urlElement"] = element.getText()
            if typeElement in ["Presentationssonorisees", "Webconference"]:
                retour["urlElement"] = element.getUrlEnr()
            if typeElement == "ExercicesWims":
                retour["urlElement"] = "cours_autoevaluation_view?qexo=%s" % (int(indexElement) + 1)
            if typeElement == "Lecteurexportable":
                retour["urlElement"] = element.getLecteurExportable()
            if typeElement == "Lienweb":
                urlWEB = element.getURLWEB()
                if not "://" in urlWEB:
                    urlWEB = "http://%s" % urlWEB
                retour["urlElement"] = urlWEB
            if typeElement == "CatalogueBU":
                ressource = element.getRessourceCatalogueBU()
                retour["image"] = ressource["image"]
                retour["publisher"] = ressource["publisher"]
                retour["creationdate"] = ressource["creationdate"]
                retour["urlcatalogue"] = ressource["urlcatalogue"]
    return retour


def getJalonMenu(context, portal_url, user, request):
    #context.plone_log("***** getJalonMenu")
    member_id = user.getId()
    is_etudiant = user.has_role(["Etudiant", "EtudiantJalon"])
    is_manager = user.has_role(["Manager"])

    jalon_properties = getToolByName(context, "portal_jalon_properties")
    jalon_categories =  dict(jalon_properties.getCategorie())
    liste_id_categorie = jalon_categories.keys()
    liste_id_categorie.sort()

    class_cours = ""
    sub_menu_mes_cours = []
    if is_etudiant:
        for id_categorie in liste_id_categorie:
            sub_menu_mes_cours.append({"id"   : "cat%s" % id_categorie,
                                       "icone": "fa fa-book",
                                       "title": jalon_categories[id_categorie]['title'],
                                       "href" : "%s/cours/%s?categorie=%s" % (portal_url, member_id, id_categorie),
                                       "activer": True,
                                      })
        if sub_menu_mes_cours:
            class_cours = "has-dropdown not-click"

    activer = jalon_properties.getPropertiesMonEspace()
    menu = {"left_menu" :[{"id"      : "mon_espace",
                           "class"   : "has-dropdown not-click",
                           "icone"   : "fa fa-home",
                           "title"   : _(u"Mon espace"),
                           "href"    : portal_url,
                           "sub_menu": [{"id"     : "fichiers",
                                         "icone"  : "fa fa-files-o",
                                         "title"  : _(u"Fichiers"),
                                         "href"   : "%s/Members/%s/Fichiers" % (portal_url, member_id),
                                         "activer": activer["activer_fichiers"]},
                                        {"id"   : "sonorisation",
                                         "icone": "fa fa-microphone",
                                         "title": _(u"Présentations sonorisées"),
                                         "href" : "%s/Members/%s/Sonorisation" % (portal_url, member_id),
                                         "activer": activer["activer_presentations_sonorisees"]},
                                        {"id"   : "wims",
                                         "icone": "fa fa-random",
                                         "title": _(u"Exercices Wims"),
                                         "href" : "%s/Members/%s/Wims" % (portal_url, member_id),
                                         "activer": activer["activer_exercices_wims"]},
                                        {"id"   : "liens",
                                         "icone": "fa fa-external-link",
                                         "title": _(u"Ressources externes"),
                                         "href" : "%s/Members/%s/Externes" % (portal_url, member_id),
                                         "activer": activer["activer_liens"]},
                                        {"id"   : "glossaire",
                                         "icone": "fa fa-font",
                                         "title": _(u"Termes de glossaire"),
                                         "href" : "%s/Members/%s/Glossaire" % (portal_url, member_id),
                                         "activer": activer["activer_termes_glossaire"]},
                                        {"id"   : "connect",
                                         "icone": "fa fa-headphones",
                                         "title": _(u"Webconférences"),
                                         "href" : "%s/Members/%s/Webconference" % (portal_url, member_id),
                                         "activer": activer["activer_webconferences"]}
                                       ],
                           "is_visible": not is_etudiant},
                          {"id"      : "mes-cours",
                           "class"   : class_cours,
                           "icone"   : "fa fa-university",
                           "title"   :  _(u"Mes cours"),
                           "href"    :   "%s/cours/%s" % (portal_url, member_id),
                           "sub_menu": sub_menu_mes_cours,
                           "is_visible": True},
                          {"id"      : "mes_etudiants",
                           "class"   : "",
                           "icone"   : "fa fa-users",
                           "title"   : _(u"Mes étudiants"),
                           "href"    : "%s/etudiants" % portal_url,
                           "sub_menu": [],
                           "is_visible": not is_etudiant},
                          {"id"      : "gestion_pedagogique",
                           "class"   : "has-dropdown not-click",
                           "icone"   : "fa fa-database",
                           "title"   : _(u"Gestion pédagogique"),
                           "href"    : "%s/portal_jalon_bdd/@@jalon-bdd" % portal_url,
                           "sub_menu": [{"id"     : "gestion_bdd",
                                         "icone"  : "fa fa-list",
                                         "title"  : _(u"Offre de formations"),
                                         "href"   : "%s/portal_jalon_bdd/@@jalon-bdd?gestion=gestion_bdd" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_utilisateurs",
                                         "icone"  : "fa fa-users",
                                         "title"  : _(u"Utilsateurs"),
                                         "href"   : "%s/portal_jalon_bdd/@@jalon-bdd?gestion=gestion_utilisateurs" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_connexion_bdd",
                                         "icone"  : "fa fa-key",
                                         "title"  : _(u"Connexion"),
                                         "href"   : "%s/portal_jalon_bdd/@@jalon-bdd?gestion=gestion_connexion_bdd" % portal_url,
                                         "activer": True},
                                       ],
                          "is_visible": is_manager},
                          {"id"      : "configuration",
                           "class"   : "has-dropdown not-click",
                           "icone"   : "fa fa-cogs",
                           "title"   : _(u"Configuration"),
                           "href"    : "%s/portal_jalon_properties/@@jalon-configuration" % portal_url,
                           "sub_menu": [{"id"   : "gestion_connexion",
                                         "icone": "fa fa-key",
                                         "title": _(u"Connexion à Jalon"),
                                         "href" : "%s/portal_jalon_properties/gestion_connexion" % portal_url,
                                         "activer": True},
                                        {"id"   : "gestion_mon_espace",
                                         "icone": "fa fa-home",
                                         "title": _(u"Gestion \"Mon Espace\""),
                                         "href" : "%s/portal_jalon_properties/gestion_mon_espace" % portal_url,
                                         "activer": True},
                                        {"id"   : "gestion_mes_cours",
                                         "icone": "fa fa-university",
                                         "title": _(u"Gestion des cours"),
                                         "href" : "%s/portal_jalon_properties/gestion_mes_cours" % portal_url,
                                         "activer": True},
                                        {"id"   : "gestion_infos",
                                         "icone": "fa fa-external-link-square",
                                         "title": _(u"Liens d'informations"),
                                         "href" : "%s/portal_jalon_properties/gestion_infos" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_didacticiels",
                                         "icone"  : "fa fa-life-ring",
                                         "title"  : _(u"Didacticiels"),
                                         "href"   : "%s/portal_jalon_properties/gestion_didacticiels" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_messages",
                                         "icone"  : "fa fa-newspaper-o",
                                         "title"  : _(u"Diffusion de messages"),
                                         "href"   : "%s/portal_jalon_properties/gestion_messages" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_email",
                                         "icone"  : "fa fa-envelope-o",
                                         "title"  : _(u"Courriels"),
                                         "href"   : "%s/portal_jalon_properties/gestion_email" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_donnees_utilisateurs",
                                         "icone"  : "fa fa-users",
                                         "title"  : _(u"Données utilisateurs"),
                                         "href"   : "%s/portal_jalon_properties/gestion_donnees_utilisateurs" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_ga",
                                         "icone"  : "fa fa-line-chart",
                                         "title"  : _(u"Google Analytics"),
                                         "href"   : "%s/portal_jalon_properties/gestion_ga" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_maintenance",
                                         "icone"  : "fa fa-fire-extinguisher",
                                         "title"  : _(u"Maintenance"),
                                         "href"   : "%s/portal_jalon_properties/gestion_maintenance" % portal_url,
                                         "activer": True}
                                       ],
                          "is_visible": is_manager},
                         ],
            "right_menu" : [{"id"      : "deconnexion",
                             "class"   : "",
                             "icone"   : "fa fa-sign-out fa-fw",
                             "title"   : _(u"Deconnexion"),
                             "href"    : "%s/logout" % portal_url,
                             "sub_menu": []}
                           ]
           }
    request.SESSION.set("topBar", menu)
    return menu


def getFooter():
    portal = getUtility(IPloneSiteRoot)
    jalon_properties = getToolByName(portal, "portal_jalon_properties")
    dico = copy.copy(jalon_properties.getPropertiesInfos())
    dico["site"] = portal.Title()
    dico["activer_aide"] = jalon_properties.getJalonProperty("activer_aide")
    dico["lien_aide"] = jalon_properties.getJalonProperty("lien_aide")
    return dico


def gaEncodeTexte(chemin, texte):
    return jalon_encode.encodeTexte(chemin, texte)


"""
def setFullname(member, fullname):
    LOG.info('setFullname')
    LOG.info(fullname)
    portal = getUtility(IPloneSiteRoot)
    modMember = portal.portal_membership.getMemberById(member)
    modMember.setMemberProperties(mapping={"fullname" : fullname})
"""


def traductions_fil(key):
    textes = {"Mon espace":               _(u"Mon espace"),
              "Mes cours":                _(u"Mes cours"),
              "Mes étudiants":            _(u"Mes étudiants"),
              "Présentations sonorisées": _(u"Présentations sonorisées"),
              "Webconférences":           _(u"Webconférences"),
              "Vidéo":                    _(u"Vidéo"),
              "Fichiers":                 _(u"Fichiers"),
              "Liens":                    _(u"Liens"),
              "Podcast":                  _(u"Podcast"),
              "PositionCours":            _(u"Définir la position dans le cours"),
              "Configuration du site":    _(u"Configuration du site"),
              "Utilisateurs":             _(u"Utilisateurs"),
              "Catégories":               _(u"Catégories"),
              "configsite":               _(u"Configuration du site"),
              "portal_jalon_properties":  _(u"Configuration de Jalon")
              }
    if key in textes:
        return textes[key]
    else:
        return key
