## Controller Python Script "trombinoscope_pdf"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=login=None
##title=
##

request = context.REQUEST

trombino = context.genererPDF(request['code'], request['type'])

request.RESPONSE.setHeader('content-type', 'application/pdf')
request.RESPONSE.setHeader('content-length', trombino["length"])
request.RESPONSE.setHeader('Content-Disposition',' attachment; filename=Trombino%s-%s.zip' % (request['type'], request['code']))

return trombino["data"]