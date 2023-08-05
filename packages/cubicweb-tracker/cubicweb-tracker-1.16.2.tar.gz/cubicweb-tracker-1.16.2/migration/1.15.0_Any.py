## Add assigned_to for Tickets
add_relation_definition('Ticket', 'assigned_to', 'CWUser')
rset = rql('Any TI,TN WHERE TG name ILIKE "todoby_%", TG name TN, TG tags TI, TG is Tag, TI is Ticket')
for ticketeid, tagname in rset:
    user_login = tagname.split('_', 1)[1]
    rql('SET T assigned_to U WHERE U is CWUser, U login %(user)s, T eid %(ticket)s',
        {'user': user_login, 'ticket': ticketeid})
commit()
