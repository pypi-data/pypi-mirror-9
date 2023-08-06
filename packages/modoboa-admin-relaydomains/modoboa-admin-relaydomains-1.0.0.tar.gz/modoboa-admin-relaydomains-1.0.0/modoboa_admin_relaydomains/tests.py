"""modoboa-admin-relaydomains unit tests."""

from django.core.urlresolvers import reverse
from django.test import TestCase

from modoboa.core.factories import UserFactory
from modoboa.lib import parameters
from modoboa.lib.tests import ModoTestCase
from modoboa.lib.test_utils import MapFilesTestCaseMixin

from modoboa_admin import factories

from .factories import RelayDomainFactory, RelayDomainAliasFactory
from .models import RelayDomain, RelayDomainAlias, Service


class Operations(object):

    def _create_relay_domain(self, name, status=200):
        srv, created = Service.objects.get_or_create(name='dummy')
        values = {
            'name': name, 'target_host': 'external.host.tld',
            'service': srv.id, 'enabled': True
        }
        return self.ajax_post(
            reverse("modoboa_admin_relaydomains:relaydomain_add"),
            values, status
        )

    def _relay_domain_alias_operation(self, optype, rdomain, name, status=200):
        rdom = RelayDomain.objects.get(name=rdomain)
        values = {
            'name': rdom.name, 'target_host': rdom.target_host,
            'service': rdom.service.id
        }
        aliases = [alias.name for alias in rdom.relaydomainalias_set.all()]
        if optype == 'add':
            aliases.append(name)
        else:
            aliases.remove(name)
        for cpt, alias in enumerate(aliases):
            fname = 'aliases' if not cpt else 'aliases_%d' % cpt
            values[fname] = alias
        return self.ajax_post(
            reverse("modoboa_admin_relaydomains:relaydomain_change",
                    args=[rdom.id]),
            values, status
        )

    def _check_limit(self, name, curvalue, maxvalue):
        l = self.user.limitspool.get_limit('%s_limit' % name)
        self.assertEqual(l.curvalue, curvalue)
        self.assertEqual(l.maxvalue, maxvalue)


class RelayDomainsTestCase(ModoTestCase, Operations):

    def setUp(self):
        super(RelayDomainsTestCase, self).setUp()
        factories.populate_database()
        self.rdom = RelayDomainFactory(name='relaydomain.tld')
        RelayDomainAliasFactory(name='relaydomainalias.tld', target=self.rdom)

    def test_create_relaydomain(self):
        """Test the creation of a relay domain.

        We also check that unique constraints are respected: domain,
        relay domain alias.

        FIXME: add a check for domain alias.
        """
        self._create_relay_domain('relaydomain1.tld')
        rdom = RelayDomain.objects.get(name='relaydomain1.tld')
        self.assertEqual(rdom.target_host, 'external.host.tld')
        self.assertEqual(rdom.service.name, 'dummy')
        self.assertEqual(rdom.enabled, True)
        self.assertEqual(rdom.verify_recipients, False)

        resp = self._create_relay_domain('test.com', 400)
        self.assertEqual(resp['form_errors']['name'][0],
                         'A domain with this name already exists')
        resp = self._create_relay_domain('relaydomainalias.tld', 400)
        self.assertEqual(
            resp['form_errors']['name'][0],
            'A relay domain alias with this name already exists'
        )

    def test_create_relaydomainalias(self):
        """Test the creation of a relay domain alias.

        We also check that unique constraints are respected: domain,
        relay domain.

        FIXME: add a check for domain alias.
        """
        self._relay_domain_alias_operation(
            'add', self.rdom.name, 'relaydomainalias1.tld'
        )
        resp = self._relay_domain_alias_operation(
            'add', self.rdom.name, 'test.com', 400
        )
        self.assertEqual(
            resp['form_errors']['aliases_2'][0],
            'A domain with this name already exists'
        )
        resp = self._relay_domain_alias_operation(
            'add', self.rdom.name, self.rdom.name, 400
        )
        self.assertEqual(
            resp['form_errors']['aliases_2'][0],
            'A relay domain with this name already exists'
        )

    def test_edit_relaydomain(self):
        """Test the modification of a relay domain.

        Rename 'relaydomain.tld' domain to 'relaydomain.org'
        """
        values = {
            'name': 'relaydomain.org', 'target_host': self.rdom.target_host,
            'service': self.rdom.service.id
        }
        self.ajax_post(
            reverse('modoboa_admin_relaydomains:relaydomain_change',
                    args=[self.rdom.id]),
            values
        )
        RelayDomain.objects.get(name='relaydomain.org')

    def test_edit_relaydomainalias(self):
        """Test the modification of a relay domain alias.

        Rename 'relaydomainalias.tld' domain to 'relaydomainalias.net'
        """
        values = {
            'name': 'relaydomain.org', 'target_host': self.rdom.target_host,
            'service': self.rdom.service.id, 'aliases': 'relaydomainalias.net'
        }
        self.ajax_post(
            reverse('modoboa_admin_relaydomains:relaydomain_change',
                    args=[self.rdom.id]),
            values
        )
        RelayDomainAlias.objects.get(name='relaydomainalias.net')
        with self.assertRaises(RelayDomainAlias.DoesNotExist):
            RelayDomainAlias.objects.get(name='relaydomainalias.tld')

    def test_delete_relaydomain(self):
        """Test the removal of a relay domain
        """
        self.ajax_post(
            reverse("modoboa_admin_relaydomains:relaydomain_delete",
                    args=[self.rdom.id]),
            {}
        )
        with self.assertRaises(RelayDomain.DoesNotExist):
            RelayDomain.objects.get(name='relaydomain.tld')

    def test_delete_relaydomainalias(self):
        """Test the remove of a relay domain alias
        """
        self._relay_domain_alias_operation(
            'del', self.rdom.name, 'relaydomainalias.tld'
        )
        with self.assertRaises(RelayDomain.DoesNotExist):
            RelayDomain.objects.get(name='relaydomainalias.tld')


class LimitsTestCase(ModoTestCase, Operations):

    def setUp(self):
        super(LimitsTestCase, self).setUp()
        from modoboa_admin_limits.models import LimitTemplates

        for tpl in LimitTemplates().templates:
            parameters.save_admin(
                "DEFLT_{0}".format(tpl[0].upper()), 2,
                app="modoboa_admin_limits"
            )
        self.user = UserFactory.create(
            username='reseller', groups=('Resellers',)
        )
        self.clt.logout()
        self.clt.login(username='reseller', password='toto')

    def test_relay_domains_limit(self):
        self._create_relay_domain('relaydomain1.tld')
        self._check_limit('relay_domains', 1, 2)
        self._create_relay_domain('relaydomain2.tld')
        self._check_limit('relay_domains', 2, 2)
        resp = self._create_relay_domain('relaydomain3.tld', 403)
        self._check_limit('relay_domains', 2, 2)
        self.ajax_post(
            reverse('modoboa_admin_relaydomains:relaydomain_delete',
                    args=[RelayDomain.objects.get(name='relaydomain2.tld').id]),
            {}
        )
        self._check_limit('relay_domains', 1, 2)

    def test_relay_domain_aliases_limit(self):
        self._create_relay_domain('relaydomain1.tld')
        self._relay_domain_alias_operation(
            'add', 'relaydomain1.tld', 'relay-domain-alias1.tld'
        )
        self._check_limit('relay_domain_aliases', 1, 2)
        self._relay_domain_alias_operation(
            'add', 'relaydomain1.tld', 'relay-domain-alias2.tld'
        )
        self._check_limit('relay_domain_aliases', 2, 2)
        self._relay_domain_alias_operation(
            'add', 'relaydomain1.tld', 'relay-domain-alias3.tld', 403
        )
        self._check_limit('relay_domain_aliases', 2, 2)
        self._relay_domain_alias_operation(
            'delete', 'relaydomain1.tld', 'relay-domain-alias2.tld'
        )
        self._check_limit('relay_domain_aliases', 1, 2)


class MapFilesTestCase(MapFilesTestCaseMixin, TestCase):

    """Test case for modoboa-admin-relaydomains."""

    extension = "modoboa_admin_relaydomains"

    MAP_FILES = [
        "sql-relaydomains.cf",
        "sql-relaydomains-transport.cf",
        "sql-relaydomain-aliases-transport.cf",
        "sql-relay-recipient-verification.cf"
    ]
