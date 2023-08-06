##parameters=search
context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
return context.aq_parent.getMotsClefs(search, context.getId())