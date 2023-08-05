"""
Tests for `clustercron` module.
"""

import pytest
from clustercron import clustercron


def test_parse_clustercron_args_no_args():
    '''
    Test the long command-line arguments to clustercron.
    '''
    with pytest.raises(SystemExit):
        args = clustercron.parse_clustercron_args([])
        assert vars(args) == {'verbose': False}


#def test_parse_clustercron_args_deprovision():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['deprovision'])
#
#    with pytest.raises(SystemExit):
#        args = clustercron.parse_clustercron_args(['deprovision'])
#
#    args = clustercron.parse_clustercron_args(['deprovision', 'run'])
#    assert vars(args) == {
#        'scope': 'deprovision',
#        'subcommand': 'run',
#        'verbose': False,
#        'quiet': False,
#        'delete': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#    args = clustercron.parse_clustercron_args(['deprovision', 'check'])
#    assert vars(args) == {
#        'scope': 'deprovision',
#        'subcommand': 'check',
#        'verbose': False,
#        'quiet': False,
#        'delete': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_user():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['user'])
#
#
#def test_parse_clustercron_args_user_info():
#    with pytest.raises(SystemExit):
#        args = clustercron.parse_clustercron_args(['user', 'info'])
#
#    args = clustercron.parse_clustercron_args(['user', 'info', '00200'])
#    assert vars(args) == {
#        'scope': 'user',
#        'subcommand': 'info',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_user_enable():
#    with pytest.raises(SystemExit):
#        args = clustercron.parse_clustercron_args(['user', 'enable'])
#
#    args = clustercron.parse_clustercron_args(['user', 'enable', '00200'])
#    assert vars(args) == {
#        'scope': 'user',
#        'subcommand': 'enable',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_user_disable():
#    with pytest.raises(SystemExit):
#        args = clustercron.parse_clustercron_args(['user', 'disable'])
#
#    args = clustercron.parse_clustercron_args(['user', 'disable', '00200'])
#    assert vars(args) == {
#        'scope': 'user',
#        'subcommand': 'disable',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_user_delete():
#    with pytest.raises(SystemExit):
#        args = clustercron.parse_clustercron_args(['user', 'delete'])
#
#    args = clustercron.parse_clustercron_args(['user', 'delete', '00200'])
#    assert vars(args) == {
#        'scope': 'user',
#        'subcommand': 'delete',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'force': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_user_write_address_field():
#    with pytest.raises(SystemExit):
#        args = clustercron.parse_clustercron_args(['user', 'write_address_field'])
#
#    args = clustercron.parse_clustercron_args(['user', 'write_address_field', '00200'])
#    assert vars(args) == {
#        'scope': 'user',
#        'subcommand': 'write_address_field',
#        'login': '00200',
#        'verbose': False,
#        'old_last_in_ad_date': False,
#        'quiet': False,
#        'today': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_user_clear_address_field():
#    with pytest.raises(SystemExit):
#        args = clustercron.parse_clustercron_args(['user', 'clear_address_field'])
#
#    args = clustercron.parse_clustercron_args(['user', 'clear_address_field', '00200'])
#    assert vars(args) == {
#        'scope': 'user',
#        'subcommand': 'clear_address_field',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_customer():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['customer'])
#
#
#def test_parse_clustercron_args_customerinfo():
#    with pytest.raises(SystemExit):
#        args = clustercron.parse_clustercron_args(['customer', 'info'])
#
#    args = clustercron.parse_clustercron_args(['customer', 'info', '00200'])
#    assert vars(args) == {
#        'scope': 'customer',
#        'subcommand': 'info',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_customer_list():
#    args = clustercron.parse_clustercron_args(['customer', 'list'])
#    assert vars(args) == {
#        'scope': 'customer',
#        'subcommand': 'list',
#        'login': None,
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#    args = clustercron.parse_clustercron_args(['customer', 'list', '--login=00200'])
#    assert vars(args) == {
#        'scope': 'customer',
#        'subcommand': 'list',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_customer_create():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['customer', 'create'])
#
#    args = clustercron.parse_clustercron_args(['customer', 'create', '00200'])
#    assert vars(args) == {
#        'scope': 'customer',
#        'subcommand': 'create',
#        'login': '00200',
#        'password': None,
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#        'with_subscription': False,
#    }
#
#    args = clustercron.parse_clustercron_args(
#        ['customer', 'create', '00200', '--with-subscription',
#         '--password=test']
#    )
#    assert vars(args) == {
#        'scope': 'customer',
#        'subcommand': 'create',
#        'login': '00200',
#        'with_subscription': True,
#        'password': 'test',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_customer_disable():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['customer', 'disable'])
#
#    args = clustercron.parse_clustercron_args(
#        ['customer', 'disable', '00200']
#    )
#    assert vars(args) == {
#        'scope': 'customer',
#        'subcommand': 'disable',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_customer_enable():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['customer', 'enable'])
#
#    args = clustercron.parse_clustercron_args(
#        ['customer', 'enable', '00200']
#    )
#    assert vars(args) == {
#        'scope': 'customer',
#        'subcommand': 'enable',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_customer_chpasswd():
#    with pytest.raises(SystemExit):
#        args = clustercron.parse_clustercron_args(['customer', 'chpasswd'])
#        assert vars(args) == {}
#
#    with pytest.raises(SystemExit):
#        args = clustercron.parse_clustercron_args(['customer', 'chpasswd', '00200'])
#        assert vars(args) == {}
#
#    args = clustercron.parse_clustercron_args(
#        ['customer', 'chpasswd', '00200', 'new_password']
#    )
#    assert vars(args) == {
#        'scope': 'customer',
#        'subcommand': 'chpasswd',
#        'login': '00200',
#        'password': 'new_password',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_site():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['site'])
#
#
#def test_parse_clustercron_args_siteinfo():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['site', 'info'])
#
#    args = clustercron.parse_clustercron_args(['site', 'info', '00200.ma-cloud.com'])
#    assert vars(args) == {
#        'scope': 'site',
#        'subcommand': 'info',
#        'config': '/etc/clustercron/clustercron.yml',
#        'name': '00200.ma-cloud.com',
#        'verbose': False,
#        'quiet': False,
#    }
#
#
#def test_parse_clustercron_args_site_enable():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['site', 'enable'])
#
#    args = clustercron.parse_clustercron_args(
#        ['site', 'enable', '00200.hosts.ma-cloud.nl']
#    )
#    assert vars(args) == {
#        'scope': 'site',
#        'subcommand': 'enable',
#        'name': '00200.hosts.ma-cloud.nl',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_site_disable():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['site', 'disable'])
#
#    args = clustercron.parse_clustercron_args(
#        ['site', 'disable', '00200.hosts.ma-cloud.nl']
#    )
#    assert vars(args) == {
#        'scope': 'site',
#        'subcommand': 'disable',
#        'name': '00200.hosts.ma-cloud.nl',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_subscription():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['subscription'])
#
#
#def test_parse_clustercron_args_subscriptioninfo():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['subscription', 'info'])
#
#    args = clustercron.parse_clustercron_args(['subscription', 'info', '00200'])
#    assert vars(args) == {
#        'subcommand': 'info',
#        'config': '/etc/clustercron/clustercron.yml',
#        'scope': 'subscription',
#        'verbose': False,
#        'quiet': False,
#        'login': '00200',
#    }
#
#
#def test_parse_clustercron_args_subscription_enable():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['subscription', 'enable'])
#
#    args = clustercron.parse_clustercron_args(
#        ['subscription', 'enable', '00200']
#    )
#    assert vars(args) == {
#        'scope': 'subscription',
#        'subcommand': 'enable',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_parse_clustercron_args_subscription_disable():
#    with pytest.raises(SystemExit):
#        clustercron.parse_clustercron_args(['subscription', 'disable'])
#
#    args = clustercron.parse_clustercron_args(
#        ['subscription', 'disable', '00200']
#    )
#    assert vars(args) == {
#        'scope': 'subscription',
#        'subcommand': 'disable',
#        'login': '00200',
#        'verbose': False,
#        'quiet': False,
#        'config': '/etc/clustercron/clustercron.yml',
#    }
#
#
#def test_Attrs():
#    attrs = clustercron.Attrs()
#    attrs.key = 'value'
#    assert str(attrs) == \
#        'Attrs Attributes:\n  key: value\n'
#
#
#def test_UserLDAPAttrs():
#    user_ldap_attr = clustercron.UserLDAPAttr()
#    assert user_ldap_attr.__dict__ == {
#        'accountExpires': None,
#        'cn': None,
#        'description': None,
#        'displayName': None,
#        'employeeID': None,
#        'employeeType': None,
#        'extensionAttribute1': None,
#        'mail': None,
#        'sn': None,
#    }
#
#
#def test_PleskCustomer():
#    plesk_customer = clustercron.PleskCustomer()
#    assert plesk_customer.__dict__ == {
#        'address': None,
#        'login': None,
#        'created': None,
#        'status': None,
#    }
#
#
#def test_PleskSubscription():
#    plesk_subscription = clustercron.PleskSubscription()
#    assert plesk_subscription.__dict__ == {
#        'name':  None,
#        'created': None,
#        'status': None,
#    }
#
#
#def test_PleskSite():
#    plesk_site = clustercron.PleskSite()
#    assert plesk_site.__dict__ == {
#        'name':  None,
#        'created': None,
#        'status': None,
#    }
#
#
#class Test_AddressField():
#    def test_init(self):
#        address_field = clustercron.AddressField()
#        assert address_field.__dict__ == {
#            'expiration_date': None,
#            'last_in_ad_date': None,
#            'validated_and_set': False,
#            'json_str': None,
#            'signed_json_str': None,
#            'is_valid': None,
#        }
#
#    def test_set_signer(self):
#        secret_key = 'geheim03'
#        text = 'text'
#        signer = itsdangerous.Signer(secret_key)
#        signed_text = signer.sign(text)
#        address_field = clustercron.AddressField()
#        clustercron.AddressField.set_signer(secret_key)
#        assert address_field.signer.sign(text) == signed_text
#
#    def test_data_handler(self):
#        address_field = clustercron.AddressField()
#        date_obj = datetime.datetime(2014, 7, 1, 9, 33, 54, 540076)
#        date_iso_str = '2014-07-01T09:33:54'
#        a_string = 'text'
#        assert address_field.date_handler(date_obj) == date_iso_str
#        assert address_field.date_handler(a_string) == a_string
#
#    def test_set_json_str_from_attrs(self):
#        address_field = clustercron.AddressField()
#        address_field.expiration_date = datetime.datetime(
#            2014, 7, 1, 9, 39, 1, 902187)
#        address_field.last_in_ad_date = datetime.datetime(
#            2014, 6, 2, 14, 15, 1, 815328)
#        address_field.set_json_str_from_attrs()
#        assert address_field.json_str == \
#            '{"expiration_date": "2014-07-01T09:39:01", ' \
#            '"last_in_ad_date": "2014-06-02T14:15:01"}'
#
#    def test_set_attrs_from_json_str(self):
#        address_field = clustercron.AddressField()
#        address_field.json_str = \
#            '{"last_in_ad_date": "2014-06-02T14:15:01", ' \
#            '"expiration_date": "2014-07-01T09:39:01"}'
#        address_field.set_attrs_from_json_str()
#        assert address_field.expiration_date == datetime.datetime(
#            2014, 7, 1, 9, 39, 1)
#        assert address_field.last_in_ad_date == datetime.datetime(
#            2014, 6, 2, 14, 15, 1)
#
#    def test_validate_true(self):
#        clustercron.AddressField.set_signer(
#            'wdDy6HWGYuMU3I0pS4j4PdlWpQqSbwX7oMWOFZfZ'
#        )
#        address_field = clustercron.AddressField()
#        address_field.signed_json_str = \
#            '{"last_in_ad_date": "2014-06-02T14:15:01", ' \
#            '"expiration_date": "2014-07-01T09:39:01"}' \
#            '.6rQNV-zCdnf8lEQGnI4M_YlxphQ'
#        address_field.validate()
#        assert address_field.is_valid is True
#
#    def test_validate_false(self):
#        clustercron.AddressField.set_signer(
#            'wdDy6HWGYuMU3I0pS4j4PdlWpQqSbwX7oMWOFZfZ'
#        )
#        address_field = clustercron.AddressField()
#        address_field.signed_json_str = \
#            '{"last_in_ad_date": "2014-06-02T14:15:01", ' \
#            '"expiration_date": "2014-07-01T09:39:02"}' \
#            '.6rQNV-zCdnf8lEQGnI4M_YlxphQ'
#        address_field.validate()
#        assert address_field.is_valid is False
#
#    def test_get_none(self):
#        address_field = clustercron.AddressField()
#        address_field.get(None)
#        assert address_field.expiration_date is None
#        assert address_field.last_in_ad_date is None
#        assert address_field.validated_and_set is False
#        assert address_field.json_str is None
#        assert address_field.signed_json_str is None
#        assert address_field.is_valid is None
#
#    def test_get(self):
#        clustercron.AddressField.set_signer(
#            'wdDy6HWGYuMU3I0pS4j4PdlWpQqSbwX7oMWOFZfZ'
#        )
#        address_field = clustercron.AddressField()
#        signed_json_str = \
#            '{"last_in_ad_date": "2014-06-02T14:15:01", ' \
#            '"expiration_date": "2014-07-01T09:39:01"}' \
#            '.6rQNV-zCdnf8lEQGnI4M_YlxphQ'
#        address_field.get(signed_json_str)
#        assert address_field.expiration_date == datetime.datetime(
#            2014, 7, 1, 9, 39, 1)
#        assert address_field.last_in_ad_date == datetime.datetime(
#            2014, 6, 2, 14, 15, 1)
#        assert address_field.validated_and_set is True
#        assert address_field.json_str == \
#            '{"last_in_ad_date": "2014-06-02T14:15:01", ' \
#            '"expiration_date": "2014-07-01T09:39:01"}'
#        assert address_field.signed_json_str == signed_json_str
#        assert address_field.is_valid is True
#
#    def test_set_dates_and_sign(self):
#        clustercron.AddressField.set_signer(
#            'wdDy6HWGYuMU3I0pS4j4PdlWpQqSbwX7oMWOFZfZ'
#        )
#        expiration_date = datetime.datetime(2014, 7, 1, 9, 39, 1)
#        last_in_ad_date = datetime.datetime(2014, 6, 2, 14, 15, 1)
#        address_field = clustercron.AddressField()
#        address_field.set_dates_and_sign(expiration_date, last_in_ad_date)
#        assert address_field.expiration_date == expiration_date
#        assert address_field.last_in_ad_date == last_in_ad_date
#
#
#@pytest.fixture
#def set_api_options(scope='class'):
#    clustercron.PleskRequestBase.set_api_options(
#        api_host='plesk.example.com',
#        api_port=8443,
#        api_path='/enterprise/control/agent.php',
#        api_reseller_username='reseller',
#        api_reseller_password='password',
#        api_admin_username='admin',
#        api_admin_password='password',
#        api_http_timeout='30',
#    )
#    return None
#
#
#class Test_User():
#    def test_init_student(self):
#        user = clustercron.User(
#            clustercron.PleskCustomer(None, '00200', '2014-07-12', '0')
#        )
#        assert user.login == '00200'
#        assert user.slogin == 's00200'
#
#    def test_init_non_student(self):
#        user = clustercron.User(
#            clustercron.PleskCustomer(None, 'docent01', '2014-07-12', '0')
#        )
#        assert user.login == 'docent01'
#        assert user.slogin is None
#
#    def test_set_subscription_options(self):
#        user = clustercron.User(
#            clustercron.PleskCustomer(None, '00200', '2014-07-12', '0')
#        )
#        clustercron.User.set_subscription_options(
#            '127.0.0.1',
#            'example.com',
#            'Acme Plan Name',
#        )
#        assert user.subscription_ip_address == '127.0.0.1'
#        assert user.subscription_domain == 'example.com'
#        assert user.subscription_plan_name == 'Acme Plan Name'
#
#    def test_str(self):
#        user = clustercron.User(
#            clustercron.PleskCustomer(None, 'docent01', '2014-07-12', '0')
#        )
#        assert str(user) == \
#            'Login: docent01\nPleskCustomer Attributes:\n  status: 0\n  ' \
#            'login: docent01\n  created: 2014-07-12\n  address: ' \
#            'None\nPleskSubscription Attributes:\n  status: None\n  name: ' \
#            'None\n  created: None\nPleskSite Attributes:\n  status: ' \
#            'None\n  name: None\n  created: None\nAddressField ' \
#            'Attributes:\n  ' \
#            'expiration_date: None\n  json_str: None\n  last_in_ad_date: ' \
#            'None\n  is_valid: None\n  validated_and_set: False\n  ' \
#            'signed_json_str: None\nHas ' \
#            'AD entry:None\nUserLDAPAttr Attributes:\n  employeeType: ' \
#            'None\n  employeeID: None\n  extensionAttribute1: None\n  sn: ' \
#            'None\n  accountExpires: None\n  mail: None\n  displayName: ' \
#            'None\n  cn: None\n  description: None\nExpiration date: None\n'
#
#    def test_update_plesk_customer(self, monkeypatch, set_api_options):
#        def post_mocked(self):
#            self.response_data = \
#                testdata.plesk_response_data.customer_get_info_status_updated
#        monkeypatch.setattr(clustercron.PleskRequestBase, 'post', post_mocked)
#        user = clustercron.User(
#            clustercron.PleskCustomer(None, '00200', '2014-07-12', '0')
#        )
#        user.update_plesk_customer()
#        assert user.plesk_customer.address == \
#            '{"last_in_ad_date": "2014-06-02T14:15:01", ' \
#            '"expiration_date": "2014-07-01T09:39:01"}' \
#            '.6rQNV-zCdnf8lEQGnI4M_YlxphQ'
#        assert user.plesk_customer.created == '2014-08-12'
#        assert user.plesk_customer.status == '16'
#
#    def test_set_plesk_subscription(self, monkeypatch, set_api_options):
#        def post_mocked(self):
#            self.response_data = \
#                testdata.plesk_response_data.\
#                subscription_get_info_status_active
#        monkeypatch.setattr(clustercron.PleskRequestBase, 'post', post_mocked)
#        user = clustercron.User(
#            clustercron.PleskCustomer(None, '00200', '2014-07-12', '0')
#        )
#        user.set_plesk_subscription()
#        assert user.plesk_subscription.name == '00200.hosts.ma-cloud.nl'
#        assert user.plesk_subscription.created == '2014-07-12'
#        assert user.plesk_subscription.status == '0'
#
#    def test_set_plesk_site(self, monkeypatch, set_api_options):
#        def post_mocked(self):
#            self.response_data = \
#                testdata.plesk_response_data.site_get_info_status_active
#        monkeypatch.setattr(clustercron.PleskRequestBase, 'post', post_mocked)
#        user = clustercron.User(
#            clustercron.PleskCustomer(None, '00200', '2014-07-12', '0')
#        )
#        user.set_plesk_site()
#        assert user.plesk_site.name == '00200.hosts.ma-cloud.nl'
#        assert user.plesk_site.created == '2014-07-12'
#        assert user.plesk_site.status == '0'
#
#
#class Test_ResponseAttr():
#    def test_init(self):
#        response_attr = clustercron.ResponseAttr(
#            'gen_info_login',
#            'data/gen_info/login',
#            None,
#        )
#        assert response_attr.__dict__ == {
#            'name': 'gen_info_login',
#            'xml_path': 'data/gen_info/login',
#            'default': None,
#        }
