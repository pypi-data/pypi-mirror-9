"""Map file definitions for postfix."""

from modoboa.core.commands.postfix_maps import registry


class RelayDomainsMap(object):

    """Map file to list all relay domains."""

    filename = "sql-relaydomains.cf"
    mysql = (
        "SELECT name FROM postfix_relay_domains_relaydomain "
        "WHERE name='%s' AND enabled=1"
    )
    postgres = (
        "SELECT name FROM postfix_relay_domains_relaydomain "
        "WHERE name='%s' AND enabled"
    )
    sqlite = (
        "SELECT name FROM postfix_relay_domains_relaydomain "
        "WHERE name='%s' AND enabled=1"
    )


class RelayDomainsTransportMap(object):

    """A transport map for relay domains."""

    filename = "sql-relaydomains-transport.cf"
    mysql = (
        "SELECT CONCAT(srv.name, ':[', rdom.target_host, ']') "
        "FROM postfix_relay_domains_service AS srv "
        "INNER JOIN postfix_relay_domains_relaydomain AS rdom "
        "ON rdom.service_id=srv.id WHERE rdom.enabled=1 AND rdom.name='%s'"
    )
    postgres = (
        "SELECT srv.name || ':[' || rdom.target_host || ']' "
        "FROM postfix_relay_domains_service AS srv "
        "INNER JOIN postfix_relay_domains_relaydomain AS rdom "
        "ON rdom.service_id=srv.id WHERE rdom.enabled AND rdom.name='%s'"
    )
    sqlite = (
        "SELECT srv.name || ':[' || rdom.target_host || ']' "
        "FROM postfix_relay_domains_service AS srv "
        "INNER JOIN postfix_relay_domains_relaydomain AS rdom "
        "ON rdom.service_id=srv.id WHERE rdom.enabled=1 AND rdom.name='%s'"
    )


class RelayDomainAliasesTransportMap(object):

    """A transport map for relay domain aliases."""

    filename = "sql-relaydomain-aliases-transport.cf"
    mysql = (
        "SELECT CONCAT(srv.name, ':[', rdom.target_host, ']') "
        "FROM postfix_relay_domains_service AS srv "
        "INNER JOIN postfix_relay_domains_relaydomain AS rdom "
        "ON rdom.service_id=srv.id "
        "INNER JOIN postfix_relay_domains_relaydomainalias AS rdomalias "
        "ON rdom.id=rdomalias.target_id WHERE rdom.enabled=1 "
        "AND rdomalias.enabled=1 AND rdomalias.name='%s'"
    )
    postgres = (
        "SELECT srv.name || ':[' || rdom.target_host || ']' "
        "FROM postfix_relay_domains_service AS srv "
        "INNER JOIN postfix_relay_domains_relaydomain AS rdom "
        "ON rdom.service_id=srv.id "
        "INNER JOIN postfix_relay_domains_relaydomainalias AS rdomalias "
        "ON rdom.id=rdomalias.target_id WHERE rdom.enabled "
        "AND rdomalias.enabled AND rdomalias.name='%s'"
    )
    sqlite = (
        "SELECT srv.name || ':[' || rdom.target_host || ']' "
        "FROM postfix_relay_domains_service AS srv "
        "INNER JOIN postfix_relay_domains_relaydomain AS rdom "
        "ON rdom.service_id=srv.id "
        "INNER JOIN postfix_relay_domains_relaydomainalias AS rdomalias "
        "ON rdom.id=rdomalias.target_id WHERE rdom.enabled=1 "
        "AND rdomalias.enabled=1 AND rdomalias.name='%s'"
    )


class RelayRecipientVerification(object):

    """A map file to enable recipient verification."""

    filename = "sql-relay-recipient-verification.cf"
    mysql = (
        "SELECT 'reject_unverified_recipient' "
        "FROM postfix_relay_domains_relaydomain "
        "WHERE verify_recipients=1 AND name='%d'"
    )
    postgres = (
        "SELECT 'reject_unverified_recipient' "
        "FROM postfix_relay_domains_relaydomain "
        "WHERE verify_recipients AND name='%d'"
    )
    sqlite = (
        "SELECT 'reject_unverified_recipient' "
        "FROM postfix_relay_domains_relaydomain "
        "WHERE verify_recipients=1 AND name='%d'"
    )


registry.add_files([
    RelayDomainsMap, RelayDomainsTransportMap, RelayDomainAliasesTransportMap,
    RelayRecipientVerification
])
