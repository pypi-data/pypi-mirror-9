"""Map file definitions for postfix."""

from modoboa.core.commands.postfix_maps import registry


class DomainsMap(object):

    """Map to list all domains."""

    filename = 'sql-domains.cf'
    mysql = "SELECT name FROM admin_domain WHERE name='%s' AND enabled=1"
    postgres = "SELECT name FROM admin_domain WHERE name='%s' AND enabled"
    sqlite = "SELECT name FROM admin_domain WHERE name='%s' AND enabled=1"


class DomainsAliasesMap(object):

    """Map to list all domain aliases."""

    filename = 'sql-domain-aliases.cf'
    mysql = (
        "SELECT dom.name FROM admin_domain dom "
        "INNER JOIN admin_domainalias domal ON dom.id=domal.target_id "
        "WHERE domal.name='%s' AND domal.enabled=1 AND dom.enabled=1"
    )
    postgres = (
        "SELECT dom.name FROM admin_domain dom "
        "INNER JOIN admin_domainalias domal ON dom.id=domal.target_id "
        "WHERE domal.name='%s' AND domal.enabled AND dom.enabled"
    )
    sqlite = (
        "SELECT dom.name FROM admin_domain dom "
        "INNER JOIN admin_domainalias domal ON dom.id=domal.target_id "
        "WHERE domal.name='%s' AND domal.enabled=1 AND dom.enabled=1"
    )


class AliasesMap(object):

    """A map to list all mailbox aliases."""

    filename = 'sql-aliases.cf'
    mysql = (
        "(SELECT concat(mb.address, '@', dom.name) FROM admin_mailbox mb "
        "INNER JOIN admin_domain dom ON mb.domain_id=dom.id "
        "WHERE mb.id IN (SELECT al_mb.mailbox_id FROM admin_alias_mboxes al_mb "
        "INNER JOIN admin_alias al ON al_mb.alias_id=al.id "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE dom.name='%d' AND dom.enabled=1 AND al.address='%u' "
        "AND al.enabled=1)) "
        "UNION (SELECT concat(al.address, '@', dom.name) FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id WHERE al.id "
        "IN (SELECT al_al.to_alias_id FROM admin_alias_aliases al_al "
        "INNER JOIN admin_alias al ON al_al.from_alias_id=al.id "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE dom.name='%d' AND dom.enabled=1 AND al.address='%u' "
        "AND al.enabled=1)) UNION (SELECT al.extmboxes FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE dom.name='%d' AND dom.enabled=1 AND al.address='%u' "
        "AND al.enabled=1 AND al.extmboxes<>'')"
    )
    postgres = (
        "(SELECT mb.address || '@' || dom.name FROM admin_mailbox mb "
        "INNER JOIN admin_domain dom ON mb.domain_id=dom.id "
        "WHERE mb.id IN (SELECT al_mb.mailbox_id FROM admin_alias_mboxes al_mb "
        "INNER JOIN admin_alias al ON al_mb.alias_id=al.id "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE dom.name='%d' AND dom.enabled AND al.address='%u' "
        "AND al.enabled)) "
        "UNION (SELECT al.address || '@' || dom.name FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id WHERE al.id "
        "IN (SELECT al_al.to_alias_id FROM admin_alias_aliases al_al "
        "INNER JOIN admin_alias al ON al_al.from_alias_id=al.id "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE dom.name='%d' AND dom.enabled AND al.address='%u' "
        "AND al.enabled)) UNION (SELECT al.extmboxes FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE dom.name='%d' AND dom.enabled AND al.address='%u' "
        "AND al.enabled AND al.extmboxes<>'')"
    )
    sqlite = (
        "(SELECT (mb.address || '@' || dom.name) FROM admin_mailbox mb "
        "INNER JOIN admin_domain dom ON mb.domain_id=dom.id "
        "WHERE mb.id IN (SELECT al_mb.mailbox_id FROM admin_alias_mboxes al_mb "
        "INNER JOIN admin_alias al ON al_mb.alias_id=al.id "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE dom.name='%d' AND dom.enabled=1 AND al.address='%u' "
        "AND al.enabled=1)) "
        "UNION (SELECT (al.address || '@' || dom.name) FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id WHERE al.id "
        "IN (SELECT al_al.to_alias_id FROM admin_alias_aliases al_al "
        "INNER JOIN admin_alias al ON al_al.from_alias_id=al.id "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE dom.name='%d' AND dom.enabled=1 AND al.address='%u' "
        "AND al.enabled=1)) UNION (SELECT al.extmboxes FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE dom.name='%d' AND dom.enabled=1 AND al.address='%u' "
        "AND al.enabled=1 AND al.extmboxes<>'')"
    )


class DomainAliasesMailboxesMap(object):

    """Map file to list all domain aliases mailboxes."""

    filename = 'sql-domain-aliases-mailboxes.cf'
    mysql = (
        "(SELECT concat(mb.address, '@', dom.name) FROM admin_domainalias "
        "domal "
        "INNER JOIN admin_domain dom ON domal.target_id=dom.id "
        "INNER JOIN admin_mailbox mb ON mb.domain_id=dom.id "
        "WHERE domal.name='%d' AND dom.enabled=1 AND mb.address='%u') "
        "UNION (SELECT concat(al.address, '@', dom.name) "
        "FROM admin_domainalias domal INNER JOIN admin_domain dom "
        "ON domal.target_id=dom.id INNER JOIN admin_alias al "
        "ON al.domain_id=dom.id WHERE domal.name='%d' AND dom.enabled=1 "
        "AND al.address='%u')"
    )
    postgres = (
        "(SELECT mb.address || '@' || dom.name FROM admin_domainalias domal "
        "INNER JOIN admin_domain dom ON domal.target_id=dom.id "
        "INNER JOIN admin_mailbox mb ON mb.domain_id=dom.id "
        "WHERE domal.name='%d' AND dom.enabled AND mb.address='%u') "
        "UNION (SELECT al.address || '@' || dom.name "
        "FROM admin_domainalias domal INNER JOIN admin_domain dom "
        "ON domal.target_id=dom.id INNER JOIN admin_alias al "
        "ON al.domain_id=dom.id WHERE domal.name='%d' AND dom.enabled "
        "AND al.address='%u')"
    )
    sqlite = (
        "(SELECT mb.address || '@' || dom.name FROM admin_domainalias domal "
        "INNER JOIN admin_domain dom ON domal.target_id=dom.id "
        "INNER JOIN admin_mailbox mb ON mb.domain_id=dom.id "
        "WHERE domal.name='%d' AND dom.enabled=1 AND mb.address='%u') "
        "UNION (SELECT al.address || '@' || dom.name "
        "FROM admin_domainalias domal INNER JOIN admin_domain dom "
        "ON domal.target_id=dom.id INNER JOIN admin_alias al "
        "ON al.domain_id=dom.id WHERE domal.name='%d' AND dom.enabled=1 "
        "AND al.address='%u')"
    )


class MailboxesSelfAliasesMap(object):

    """A map to list regular mailboxes as aliases (catcall requirement)."""

    filename = "sql-mailboxes-self-aliases.cf"
    mysql = (
        "SELECT email FROM core_user u INNER JOIN admin_mailbox mb "
        "ON mb.user_id=u.id WHERE u.email='%s' AND u.is_active=1"
    )
    postgres = (
        "SELECT email FROM core_user u INNER JOIN admin_mailbox mb "
        "ON mb.user_id=u.id WHERE u.email='%s' AND u.is_active"
    )
    sqlite = (
        "SELECT email FROM core_user u INNER JOIN admin_mailbox mb "
        "ON mb.user_id=u.id WHERE u.email='%s' AND u.is_active=1"
    )


class CatchallAliasesMap(object):

    """A map to list all catchall aliases."""

    filename = 'sql-catchall-aliases.cf'
    mysql = (
        "(SELECT concat(mb.address, '@', dom.name) FROM admin_mailbox mb "
        "INNER JOIN admin_domain dom ON mb.domain_id=dom.id "
        "WHERE mb.id IN (SELECT al_mb.mailbox_id FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "INNER JOIN admin_alias_mboxes al_mb ON al.id=al_mb.alias_id "
        "WHERE al.enabled=1 AND al.address='*' AND dom.name='%d' AND "
        "dom.enabled=1)) UNION (SELECT al.extmboxes FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE al.enabled='1' AND al.extmboxes<>'' AND al.address='*' "
        "AND dom.name='%d' AND dom.enabled=1)"
    )
    postgres = (
        "(SELECT mb.address || '@' || dom.name FROM admin_mailbox mb "
        "INNER JOIN admin_domain dom ON mb.domain_id=dom.id "
        "WHERE mb.id IN (SELECT al_mb.mailbox_id FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "INNER JOIN admin_alias_mboxes al_mb ON al.id=al_mb.alias_id "
        "WHERE al.enabled AND al.address='*' AND dom.name='%d' AND "
        "dom.enabled)) UNION (SELECT al.extmboxes FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE al.enabled AND al.extmboxes<>'' AND al.address='*' "
        "AND dom.name='%d' AND dom.enabled)"
    )
    sqlite = (
        "(SELECT (mb.address || '@' || dom.name) FROM admin_mailbox mb "
        "INNER JOIN admin_domain dom ON mb.domain_id=dom.id "
        "WHERE mb.id IN (SELECT al_mb.mailbox_id FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "INNER JOIN admin_alias_mboxes al_mb ON al.id=al_mb.alias_id "
        "WHERE al.enabled=1 AND al.address='*' AND dom.name='%d' AND "
        "dom.enabled=1)) UNION (SELECT al.extmboxes FROM admin_alias al "
        "INNER JOIN admin_domain dom ON al.domain_id=dom.id "
        "WHERE al.enabled='1' AND al.extmboxes<>'' AND al.address='*' "
        "AND dom.name='%d' AND dom.enabled=1)"
    )


class MaintainMap(object):

    """Map files to list non available mailboxes."""

    filename = 'sql-maintain.cf'
    mysql = (
        "SELECT '450 Requested mail action not taken: mailbox unavailable' "
        "FROM admin_mailbox mb INNER JOIN admin_domain dom "
        "ON mb.domain_id=dom.id INNER JOIN admin_mailboxoperation mbop "
        "ON mbop.mailbox_id=mb.id WHERE dom.name='%d' AND mb.address='%u' "
        "LIMIT 1"
    )
    postgres = (
        "SELECT '450 Requested mail action not taken: mailbox unavailable' "
        "FROM admin_mailbox mb INNER JOIN admin_domain dom "
        "ON mb.domain_id=dom.id INNER JOIN admin_mailboxoperation mbop "
        "ON mbop.mailbox_id=mb.id WHERE dom.name='%d' AND mb.address='%u' "
        "LIMIT 1"
    )
    sqlite = (
        "SELECT '450 Requested mail action not taken: mailbox unavailable' "
        "FROM admin_mailbox mb INNER JOIN admin_domain dom "
        "ON mb.domain_id=dom.id INNER JOIN admin_mailboxoperation mbop "
        "ON mbop.mailbox_id=mb.id WHERE dom.name='%d' AND mb.address='%u' "
        "LIMIT 1"
    )


registry.add_files([
    DomainsMap, DomainsAliasesMap, AliasesMap, DomainAliasesMailboxesMap,
    MailboxesSelfAliasesMap, CatchallAliasesMap, MaintainMap
])
