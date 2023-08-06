import logging

import ldap3
from ldap3.core.exceptions import LDAPExceptionError, LDAPCommunicationError

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, DataError
from ldap3_sync.models import LDAPUser, LDAPGroup


logger = logging.getLogger(__name__)

NOTHING = 'NOTHING'
SUSPEND = 'SUSPEND'
DELETE = 'DELETE'

USER_REMOVAL_OPTIONS = (NOTHING, SUSPEND, DELETE)
GROUP_REMOVAL_OPTIONS = (NOTHING, DELETE)


class Command(NoArgsCommand):
    help = "Synchronize users, groups and group membership from an LDAP server"

    def handle_noargs(self, **options):
        self.load_settings()
        self.sync_ldap_users()
        self.sync_ldap_groups()

    def get_ldap_users(self):
        """
        Retrieve user data from target LDAP server.
        """
        logging.debug('Retrieving Users from LDAP')
        users = self.smart_ldap_searcher.search(self.user_base, self.user_filter, ldap3.SEARCH_SCOPE_WHOLE_SUBTREE, self.user_ldap_attribute_names)
        logger.info("Retrieved {} LDAP users".format(len(users)))
        return users

    def sync_ldap_users(self):
        """
        Synchronize users with local user database.
        """
        ldap_users = self.get_ldap_users()
        django_users = self.get_django_users()

        self.sync_generic(ldap_objects=ldap_users,
                          django_objects=django_users,
                          attribute_map=self.user_attribute_map,
                          django_object_model=self.user_model,
                          unique_name_field='username',
                          ldap_sync_model=LDAPUser,
                          ldap_sync_related_name='ldap_sync_user',
                          exempt_unique_names=self.exempt_usernames,
                          removal_action=self.user_removal_action)

    def get_ldap_groups(self):
        """
        Retrieve groups from target LDAP server.
        """
        logger.debug('Retrieving Groups from LDAP')
        groups = self.smart_ldap_searcher.search(self.group_base, self.group_filter, ldap3.SEARCH_SCOPE_WHOLE_SUBTREE, self.group_ldap_attribute_names)
        logger.info('Rerieved {} LDAP Groups'.format(len(groups)))
        return groups

    def sync_ldap_groups(self):
        """
        Synchronize LDAP groups with local group database.
        """
        ldap_groups = self.get_ldap_groups()
        django_groups = self.get_django_groups()

        self.sync_generic(ldap_objects=ldap_groups,
                          django_objects=django_groups,
                          attribute_map=self.group_attribute_map,
                          django_object_model=Group,
                          unique_name_field='name',
                          ldap_sync_model=LDAPGroup,
                          ldap_sync_related_name='ldap_sync_group',
                          exempt_unique_names=self.exempt_groupnames,
                          removal_action=self.group_removal_action)

    def get_ldap_group_membership(self, user_dn):
        '''
        Retrieve a list of django groups that this user DN is a member of.
        '''
        if not hasattr(self, '_group_cache'):
            self._group_cache = {}
        logger.debug('Retrieving groups that {} is a member of'.format(user_dn))
        ldap_groups = self.smart_ldap_searcher.search(self.group_base, self.group_membership_filter.format(user_dn=user_dn), ldap3.SEARCH_SCOPE_SINGLE_LEVEL, None)
        django_groups = []
        for ldap_group in ldap_groups:
            group_dn = ldap_group['dn']
            if group_dn in self._group_cache:
                django_groups.append(self._group_cache[group_dn])
            else:
                try:
                    ldap_sync_group = LDAPGroup.objects.get(dn=group_dn)
                    django_groups.append(ldap_sync_group.obj)
                    self._group_cache[group_dn] = ldap_sync_group.obj
                except LDAPGroup.DoesNotExist:
                    logger.warning('Cannot find Django Group associated with DN {}'.format(ldap_group['dn']))
                    continue
        return django_groups

    def sync_group_membership(self):
        '''
        Synchornize group membership with the directory. Only synchronize groups that have a related LDAPGroup object.
        '''
        django_users = self.get_django_users()
        for django_user in django_users:
            try:
                user_dn = django_user.ldap_sync_user.dn
            except LDAPUser.DoesNotExist:
                logger.warning('Django user with {} = {} does not have a distinguishedName associated'.format(self.username_field, getattr(django_user, self.username_field)))
                continue
            django_groups = self.get_ldap_group_membership(user_dn)
            django_user.groups = django_groups
            django_user.save()

    def sync_generic(self,
                     ldap_objects,
                     django_objects,
                     attribute_map,
                     django_object_model,
                     unique_name_field,
                     ldap_sync_model,
                     ldap_sync_related_name,
                     exempt_unique_names=[],
                     removal_action=NOTHING):
        """
        A generic synchronization method.
        """
        model_name = django_object_model.__name__

        unsaved_models = []
        model_dn_map = {}

        updated_model_count = 0

        for ldap_object in ldap_objects:
            try:
                value_map = self.generate_value_map(attribute_map, ldap_object['attributes'])
            except MissingLdapField as e:
                logger.error('LDAP Object {} is missing a field: {}'.format(ldap_object['dn'], e))
                continue
            unique_name = value_map[unique_name_field]
            distinguished_name = ldap_object['dn']

            model_dn_map[unique_name] = distinguished_name

            try:
                django_object = django_objects[unique_name]
                if self.will_model_change(value_map, django_object):
                    self.apply_value_map(value_map, django_object)
                    django_object.save()
                    updated_model_count += 1
                try:
                    if getattr(django_object, ldap_sync_related_name).distinguished_name != distinguished_name:
                        getattr(django_object, ldap_sync_related_name).distinguished_name = distinguished_name
                        getattr(django_object, ldap_sync_related_name).save()
                except ldap_sync_model.DoesNotExist:
                    ldap_sync_model(obj=django_object, distinguished_name=distinguished_name).save()
                del(django_objects[unique_name])
            except KeyError:
                django_object = django_object_model(**value_map)
                if hasattr(django_object, 'set_unusable_password') and self.set_unusable_password:
                    # only do this when its a user (or has this method) and the config says to do it
                    django_object.set_unusable_password()
                unsaved_models.append(django_object)
        logger.debug('Bulk creating unsaved {}'.format(model_name))
        django_object_model.objects.bulk_create(unsaved_models)
        logger.debug('Retrieving ID\'s for the objects that were just created')

        filter_key = '{}__in'.format(unique_name_field)
        filter_value = [getattr(u, unique_name_field) for u in unsaved_models]
        just_saved_models = django_object_model.objects.filter(**{filter_key: filter_value}).all()
        logger.debug('Bulk creating ldap_sync models')
        ldap_sync_model.objects.bulk_create([ldap_sync_model(obj=u, distinguished_name=model_dn_map[getattr(u, unique_name_field)]) for u in just_saved_models])

        msg = 'Updated {} existing {}'.format(updated_model_count, model_name)
        self.stdout.write(msg)
        logger.info(msg)

        msg = 'Created {} new {}'.format(len(unsaved_models), model_name)
        self.stdout.write(msg)
        logger.info(msg)

        # Anything left in the existing_users dict is no longer in the ldap directory
        # These should be disabled.
        existing_unique_names = set(_unique_name for _unique_name in django_objects.keys())
        # existing_unique_names.difference_update(exempt_unique_names)
        existing_model_ids = [djo.id for djo in django_objects.values() if getattr(djo, unique_name_field) in existing_unique_names]

        if removal_action == NOTHING:
            logger.info('Removal action is set to NOTHING so the {} objects that would have been removed are being ignored.'.format(len(existing_unique_names)))
        elif removal_action == SUSPEND:
            if hasattr(django_object_model, 'is_active'):
                django_object_model.objects.in_bulk(existing_model_ids).update(is_active=False)
                logger.info('Suspended {} {}.'.format(len(existing_model_ids), model_name))
            else:
                logger.info('REMOVAL_ACTION is set to SUSPEND however {} do not have an is_active attribute. Effective action will be NOTHING for {}.'.format(model_name, len(existing_model_ids)))
        elif removal_action == DELETE:
            django_object_model.objects.in_bulk(existing_model_ids).all().delete()
            logger.info('Deleted {} users.'.format(len(existing_unique_names)))

        logger.info("{} are synchronized".format(model_name))
        self.stdout.write('{} are synchronized'.format(model_name))

    def will_model_change(self, value_map, user_model):
        # I think all the attrs are utf-8 strings, possibly need to coerce
        # local user values to strings?
        for model_attr, value in value_map.items():
            if not getattr(user_model, model_attr) == value:
                return True
        return False

    def apply_value_map(self, value_map, user_model):
        for k, v in value_map.items():
            try:
                setattr(user_model, k, v)
            except AttributeError:
                raise UnableToApplyValueMapError('User model {} does not have attribute {}'.format(user_model.__class__.__name__, k))
        return user_model

    def generate_value_map(self, attribute_map, ldap_attribute_values):
        '''Given an attribute map (dict with keys as ldap attrs and values as model attrs) generate a dictionary
           which maps model attribute keys to ldap values'''
        value_map = {}
        for ldap_attr, model_attr in attribute_map.items():
            try:
                value_map[model_attr] = ldap_attribute_values[ldap_attr]
            except KeyError:
                raise MissingLdapField(ldap_attr)
        return value_map

    def get_django_objects(self, model):
        '''
        Given a Django model class get all of the current records that match.
        This is better than django's bulk methods and has no upper limit.
        '''
        model_name = model.__class__.__name__
        model_objects = [i for i in model.objects.all()]
        logger.debug('Found {} {} objects in DB'.format(len(model_objects), model_name))
        return model_objects

    def get_django_users(self):
        '''
        Return a dictionary of all existing users where the key is the username and the value is the user object.
        '''
        return dict([(getattr(u, self.username_field), u) for u in self.get_django_objects(self.user_model) if getattr(u, self.username_field) not in self.exempt_usernames])

    def get_django_groups(self):
        '''
        Return a dictionary of all existing groups where the key is the group name and the value is the group object.
        DO NOT return any groups whose name in in the LDAP_SYNC_GROUP_EXEMPT_FROM_SYNC collection.
        '''
        return dict([(g.name, g) for g in self.get_django_objects(Group) if g.name not in self.exempt_groupnames])

    def load_settings(self):
        '''
        Get all of the required settings to perform a sync and check them for sanity.
        '''
        # User sync settings
        self.user_filter = getattr(settings, 'LDAP_SYNC_USER_FILTER', '(objectClass=user)')

        try:
            self.user_base = getattr(settings, 'LDAP_SYNC_USER_BASE')
        except AttributeError:
            try:
                self.user_base = getattr(settings, 'LDAP_SYNC_BASE')
            except AttributeError:
                raise ImproperlyConfigured('Either LDAP_SYNC_USER_BASE or LDAP_SYNC_BASE are required. Neither were found.')

        try:
            self.user_attribute_map = getattr(settings, 'LDAP_SYNC_USER_ATTRIBUTES')
        except AttributeError:
            raise ImproperlyConfigured('LDAP_SYNC_USER_ATTRIBUTES is a required setting')
        self.user_ldap_attribute_names = self.user_attribute_map.keys()
        self.user_model_attribute_names = self.user_attribute_map.values()

        self.exempt_usernames = getattr(settings, 'LDAP_SYNC_USER_EXEMPT_FROM_SYNC', [])
        self.user_removal_action = getattr(settings, 'LDAP_SYNC_USER_REMOVAL_ACTION', NOTHING)
        if self.user_removal_action not in USER_REMOVAL_OPTIONS:
            raise ImproperlyConfigured('LDAP_SYNC_USER_REMOVAL_ACTION must be one of {}'.format(USER_REMOVAL_OPTIONS))

        self.user_model = get_user_model()
        self.username_field = getattr(self.user_model, 'USERNAME_FIELD', 'username')

        self.set_unusable_password = getattr(settings, 'LDAP_SYNC_USER_SET_UNUSABLE_PASSWORD', True)

        self.sync_users = getattr(settings, 'LDAP_SYNC_USERS', True)

        # Check to make sure we have assigned a value to the username field
        if self.username_field not in self.user_model_attribute_names:
            raise ImproperlyConfigured("LDAP_SYNC_USER_ATTRIBUTES must contain the username field '%s'" % self.username_field)

        # Group sync settings
        self.group_filter = getattr(settings, 'LDAP_SYNC_GROUP_FILTER', '(objectClass=group)')

        try:
            self.group_base = getattr(settings, 'LDAP_SYNC_GROUP_BASE')
        except AttributeError:
            try:
                self.group_base = getattr(settings, 'LDAP_SYNC_BASE')
            except AttributeError:
                    raise ImproperlyConfigured('Either LDAP_SYNC_GROUP_BASE or LDAP_SYNC_BASE are required. Neither were found.')

        try:
            self.group_attribute_map = getattr(settings, 'LDAP_SYNC_GROUP_ATTRIBUTES')
        except AttributeError:
            raise ImproperlyConfigured('LDAP_SYNC_GROUP_ATTRIBUTES is a required setting')
        self.group_ldap_attribute_names = self.group_attribute_map.keys()
        self.group_model_attribute_names = self.group_attribute_map.values()

        self.group_removal_action = getattr(settings, 'LDAP_SYNC_GROUP_REMOVAL_ACTION', NOTHING)
        if self.group_removal_action not in GROUP_REMOVAL_OPTIONS:
            raise ImproperlyConfigured('LDAP_SYNC_GROUP_REMOVAL_ACTION must be one of {}'.format(GROUP_REMOVAL_OPTIONS))

        self.exempt_groupnames = getattr(settings, 'LDAP_SYNC_GROUP_EXEMPT_FROM_SYNC', [])

        self.sync_groups = getattr(settings, 'LDAP_SYNC_GROUPS', True)

        self.sync_group_membership = getattr(settings, 'LDAP_SYNC_GROUP_MEMBERSHIP', True)

        self.group_membership_filter = getattr(settings, 'LDAP_SYNC_GROUP_MEMBERSHIP_FILTER', '(&(objectClass=group)(member={user_dn}))')


        # LDAP Servers
        try:
            self.ldap_config = getattr(settings, 'LDAP_CONFIG')
        except AttributeError:
            raise ImproperlyConfigured('LDAP_CONFIG is a required configuration item')
        self.smart_ldap_searcher = SmartLDAPSearcher(self.ldap_config)


class SmartLDAPSearcher:
    def __init__(self, ldap_config):
        self.ldap_config = ldap_config
        # Setup a few other config items
        self.page_size = self.ldap_config.get('page_size', 500)
        self.bind_user = self.ldap_config.get('bind_user', None)
        self.bind_password = self.ldap_config.get('bind_password', None)
        pooling_strategy = self.ldap_config.get('pooling_strategy', 'ROUND_ROBIN')
        if pooling_strategy not in ldap3.POOLING_STRATEGIES:
            raise ImproperlyConfigured('LDAP_CONFIG.pooling_strategy must be one of {}'.format(ldap3.POOLING_STRATEGIES))
        self.server_pool = ldap3.ServerPool(None, pooling_strategy)
        try:
            server_defns = self.ldap_config.get('servers')
        except AttributeError:
            raise ImproperlyConfigured('ldap_config.servers must be defined and must contain at least one server')
        for server_defn in server_defns:
            self.server_pool.add(self._defn_to_server(server_defn))

    def _defn_to_server(self, defn):
        '''Turn a settings file server definition into a ldap3 server object'''
        try:
            address = defn.get('address')
        except AttributeError:
            raise ImproperlyConfigured('Server definition must contain an address')
        port = defn.get('port', 389)
        use_ssl = defn.get('use_ssl', False)
        timeout = defn.get('timeout', 30)
        get_info = defn.get('get_schema', ldap3.SCHEMA)
        return ldap3.Server(address, port=port, use_ssl=use_ssl, connect_timeout=timeout, get_info=get_info)

    def get_connection(self):
        c = ldap3.Connection(self.server_pool, user=self.bind_user, password=self.bind_password)
        c.bind()
        return c

    def search(self, base, filter, scope, attributes):
        '''Perform a paged search but return all of the results in one hit'''
        connection = self.get_connection()
        connection.search(search_base=base, search_filter=filter, search_scope=ldap3.SEARCH_SCOPE_WHOLE_SUBTREE, attributes=attributes, paged_size=self.page_size, paged_cookie=None)
        if len(connection.response) < self.page_size:
            results = connection.response
        else:
            results = connection.response
            cookie = connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
            while cookie:
                connection.search(search_base=base, search_filter=filter, search_scope=ldap3.SEARCH_SCOPE_WHOLE_SUBTREE, attributes=attributes, paged_size=self.page_size, paged_cookie=cookie)
                results += connection.response
                cookie = connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        connection.unbind()
        return results

    def get(self, dn, attributes=[]):
        '''Return the object referenced by the given dn or return None'''
        # break the dn down and get a base from it
        search_base = ','.join(dn.split(',')[1:])
        connection = self.get_connection()
        connection.search(search_base=base, search_filter='(distinguishedName={})'.format(dn), search_scope=ldap3.SEARCH_SCOPE_SINGLE_LEVEL, attributes=attributes)
        results = connection.response
        if len(results) > 1:
            raise MultipleLDAPResultsReturnedMultipleLDAPResultsReturned()
        elif len(results) == 0:
            return None
        else:
            return results[0]


class UnableToApplyValueMapError(Exception):
    pass


class MissingLdapField(Exception):
    pass


class SyncError(Exception):
    pass


class MultipleLDAPResultsReturned(Exception):
    pass

# class PagedResultsSearchObject:
#     """
#     Taken from the python-ldap paged_search_ext_s.py demo, showing how to use
#     the paged results control: https://bitbucket.org/jaraco/python-ldap/
#     """
#     page_size = getattr(settings, 'LDAP_SYNC_PAGE_SIZE', 100)

#     def paged_search_ext_s(self, base, scope, filterstr='(objectClass=*)',
#                            attrlist=None, attrsonly=0, serverctrls=None,
#                            clientctrls=None, timeout=-1, sizelimit=0):
#         """
#         Behaves exactly like LDAPObject.search_ext_s() but internally uses the
#         simple paged results control to retrieve search results in chunks.
#         """
#         req_ctrl = SimplePagedResultsControl(True, size=self.page_size,
#                                              cookie='')

#         # Send first search request
#         msgid = self.search_ext(base, ldap.SCOPE_SUBTREE, filterstr,
#                                 attrlist=attrlist,
#                                 serverctrls=(serverctrls or []) + [req_ctrl])
#         results = []

#         while True:
#             rtype, rdata, rmsgid, rctrls = self.result3(msgid)
#             results.extend(rdata)
#             # Extract the simple paged results response control
#             pctrls = [c for c in rctrls if c.controlType ==
#                       SimplePagedResultsControl.controlType]

#             if pctrls:
#                 if pctrls[0].cookie:
#                     # Copy cookie from response control to request control
#                     req_ctrl.cookie = pctrls[0].cookie
#                     msgid = self.search_ext(base, ldap.SCOPE_SUBTREE,
#                                             filterstr, attrlist=attrlist,
#                                             serverctrls=(serverctrls or []) +
#                                             [req_ctrl])
#                 else:
#                     break

#         return results


# class PagedLDAPObject(LDAPObject, PagedResultsSearchObject):
#     pass
