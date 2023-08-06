"""Registries storing information about the agent's state and configuration.

"""
from collections import namedtuple
import logging

from appdynamics.lib import u2b, keys, values

from appdynamics.agent import pb
from appdynamics.agent.core import conditions
from appdynamics.agent.models import errors, exitcalls, transactions


class TransactionRegistry(object):
    """Track transactions that have been discovered, configured, and excluded.

    """
    __slots__ = ('registered_bts', 'excluded_bts')

    def __init__(self):
        super(TransactionRegistry, self).__init__()
        self.registered_bts = {}
        self.excluded_bts = set()

    def get_registered_id(self, entry_type, name):
        """Return the id for the named BT if it has been registered.

        Parameters
        ----------
        entry_type : int
            The entry point type for the BT, one of the ENTRY_xxx constants
            defined in :py:mod:`appdynamics.agent.models.transactions`.
        name : str
            The name of the BT.

        Returns
        -------
        id : long or None
            The id registered with the named BT, if any. If the BT has not been
            registered, then `None`.

        """
        return self.registered_bts.get((entry_type, name))

    def is_excluded(self, entry_type, name):
        """Return true if the named BT is excluded in the latest configuration.

        Parameters
        ----------
        entry_type : int
            The entry point type for the BT, one of the ENTRY_xxx constants
            defined in :py:mod:`appdynamics.agent.models.transactions`.
        name : str
            The name of the BT.
        """
        return (entry_type, name) in self.excluded_bts

    def update_config(self, tx_info):
        """Update the registry from configuration.

        Parameters
        ----------
        tx_info : appdynamics.agent.pb.TransactionInfo
            The transaction info from a `ConfigResponse`.

        """
        self.registered_bts = {}
        self.excluded_bts = set()

        for registered_bt in tx_info.registeredBTs:
            if registered_bt.btInfo.internalName and registered_bt.id:
                bt_info = registered_bt.btInfo
                key = (bt_info.entryPointType, bt_info.internalName)
                self.registered_bts[key] = registered_bt.id

        for excluded_bt in tx_info.blackListedAndExcludedBTs:
            if excluded_bt.internalName:
                key = (excluded_bt.entryPointType, excluded_bt.internalName)
                self.excluded_bts.add(key)


class BackendRegistry(object):
    """Track backends that have been registered.

    """
    __slots__ = ('backends', 'backend_to_component')

    URL_PROPERTY_MAX_LEN = 100
    HOST_PROPERTY_MAX_LEN = 50
    DB_NAME_PROPERTY_MAX_LEN = 50
    VENDOR_PROPERTY_MAX_LEN = 50

    def __init__(self):
        super(BackendRegistry, self).__init__()
        self.backends = {}
        self.backend_to_component = {}

    def get_backend(self, exit_call_type, identifying_properties, name):
        """Get a backend from its type and identifying properties.

        It will generally be more convenient to use the `get_http_backend`,
        `get_http_backend_from_url`, and `get_db_backend` methods to invoke
        this method instead of directly calling it.

        Parameters
        ----------
        exit_call_type : {exitcalls.EXIT_DB, exitcalls.EXIT_HTTP, exitcalls.EXIT_CACHE, exitcalls.EXIT_QUEUE}
            The type of the exit call being made.
        identifying_properties : dict
            A dict representing the appropriate identifying properties for a
            backend for the given exit call type.
        name : str
            A display name to give the backend.

        Returns
        -------
        backend : exitcalls.Backend
            The backend. If no backend has been added to the registry of the
            specified type with the given identifying properties, a new
            backend is created and added to the registry.

        See Also
        --------
        get_http_backend, get_http_backend_from_url, get_db_backend

        """
        k = keys(identifying_properties)
        v = map(str, values(identifying_properties))
        identifying_properties = zip(k, v)

        backend_key = (exit_call_type, tuple(sorted(identifying_properties)))

        try:
            backend = self.backends[backend_key]
        except KeyError:
            backend = exitcalls.Backend(exit_call_type, dict(identifying_properties), name)
            self.backends[backend_key] = backend

        return backend

    def get_db_backend(self, vendor, host, port, dbname):
        """Get a (SQL) database backend.

        This method is a wrapper that just invokes `get_backend` with the
        correct type, identifying properties, and name.

        Parameters
        ----------
        vendor : str
            The name of the DB server vendor, such as 'MySQL'.
        host : str
            The host the outgoing connection is being made to.
        port : int
            The port the outgoing connection is being made to.
        dbname : str
            The name of the database we are connecting to. Do not confuse this
            with the `vendor` parameter. If you are using MySQL and connecting
            to the 'ecommerce' database, the `vendor` would be 'MySQL' and
            the `dbname` would be 'ecommerce'.

        Returns
        -------
        backend : exitcalls.Backend
            The HTTP backend for the given host, port, and URL.

        """

        vendor = vendor[:self.VENDOR_PROPERTY_MAX_LEN]
        host = host[:self.HOST_PROPERTY_MAX_LEN]
        dbname = dbname[:self.DB_NAME_PROPERTY_MAX_LEN]

        identifying_properties = {
            'Vendor': vendor,
            'Host': host,
            'Port': port,
            'Database': dbname,
        }

        display_name = '{host}:{port} - {dbname} - {vendor}'.format(vendor=vendor, host=host, port=port, dbname=dbname)
        return self.get_backend(exitcalls.EXIT_DB, identifying_properties, display_name)

    def get_component_for_registered_backend(self, backend_id):
        return self.backend_to_component.get(backend_id)

    def update_config(self, backend_info):
        """Update the registry with information from configuration.

        Parameters
        ----------
        backend_info : appdynamics.agent.pb.BackendInfo
            The backend configuration from a :py:class:`appdynamics.agent.pb.ConfigResponse`.

        """
        self.backends = {}

        for rb in backend_info.registeredBackends:
            backend_config = rb.registeredBackend
            exit_point_type = backend_config.exitPointType

            exit_call_info = rb.exitCallInfo
            identifying_properties = tuple((p.name, p.value) for p in exit_call_info.identifyingProperties)

            backend = exitcalls.Backend(exit_point_type, dict(identifying_properties), exit_call_info.displayName)
            backend.registered_id = backend_config.backendID
            backend.component_id = backend_config.componentID
            backend.is_foreign_app = backend_config.componentIsForeignAppID

            backend_key = (exit_point_type, tuple(sorted(identifying_properties)))
            self.backends[backend_key] = backend

            if backend.component_id and not backend.is_foreign_app:
                self.backend_to_component[backend.registered_id] = backend.component_id


class TransactionNamingMatch(object):
    """A match found by the :py:class:`NamingSchemeRegistry`.

    Instances of this object will have a `name` field set to a non-empty
    string, and then either one of its `custom_match_id` or `naming_scheme`
    attributes (but never both) set.

    Parameters
    ----------
    name : str
        The generated name of the BT.
    custom_match_id : int or None
        If the naming match occurred against a custom match rule, then the id
        of that rule is set on the match. If no custom match rule was matched,
        then `None` is set for this attribute.
    naming_scheme : str or None
        If the naming match occurred through discovery (instead of a custom
        match rule), then the naming scheme used for generating the BT's name
        is set on the match. If the BT matched a custom match rule, then
        `None` is set for this attribute.

    """
    __slots__ = ('name', 'custom_match_id', 'naming_scheme')

    def __init__(self, name, custom_match_id=None, naming_scheme=None):
        super(TransactionNamingMatch, self).__init__()

        if custom_match_id is naming_scheme or (custom_match_id is not None and naming_scheme):
            raise ValueError('a naming match must have either a custom_match_id or a naming_scheme (but not both)')

        self.name = name
        self.custom_match_id = custom_match_id
        self.naming_scheme = naming_scheme


EntryPointConfig = namedtuple('EntryPointConfig', ('naming_scheme', 'exclude_rules', 'custom_match_rules'))


class NamingSchemeRegistry(object):
    """Registry of configured naming schemes.

    """
    __slots__ = ('entry_point_configs', 'logger')

    ENTRY_TYPES = {
        'pythonWeb': 'http',
    }

    def __init__(self):
        super(NamingSchemeRegistry, self).__init__()
        self.entry_point_configs = {}
        self.logger = logging.getLogger('appdynamics.agent')

    def match(self, entry_type, request, base_name=None):
        """Match a BT to its naming configuration and generate its name.

        This may return `None` if any of the following hold for the given
        entry type:

        1. There is no configuration, or
        2. BT reporting is disabled, or
        3. The BT does not match any custom match rules and either (a) BT
           discovery is disabled or (b) the BT matches an exclusion rule.

        Parameters
        ----------
        entry_type : int
            One of the ENTRY_xxx constants defined in
            :py:mod:`appdynamics.agent.models.transactions`.
        request : request object
            A request object that has the attributes `method`, `path`,
            `headers`, `args` (the query parameters), and `cookies`.

        Other Parameters
        ----------------
        base_name : str, optional
            If set to a non-empty string, this will be used for a discovered
            name's prefix instead of the prefix specified by the naming
            scheme.

        Returns
        -------
        match : (name, custom_match_id, naming_scheme) or None
            If the BT matches the discovery or custom match rule config of
            this registry, a `TransactionNamingMatch` named tuple is returned.
            If the BT is excluded (either explicitly or because discovery is
            disabled and no custom rule matches), or if there is no naming
            configuration for the given entry point, then `None` is returned,
            and no BT will be reported.

        """
        entry_type_name = pb.EntryPointType.Name(entry_type)
        entry_point_config = self.entry_point_configs.get(entry_type)

        if not entry_point_config:
            self.logger.debug('Skipping BT: entry point %s is disabled/unconfigured.', entry_type_name)
            return None

        for rule in entry_point_config['custom_definitions']:
            if conditions.match_http(request, rule['condition']):
                match = TransactionNamingMatch(name=rule['name'], custom_match_id=rule['id'])
                return match

        if not entry_point_config['discovery_enabled']:
            self.logger.debug('Skipping BT: entry point %s, no custom match and discovery is disabled')
            return None  # Discovery disabled and no custom match rules matched.

        for rule in entry_point_config['exclude_rules']:
            if conditions.match_http(request, rule):
                self.logger.debug('Skipping BT: bt matched an exclude rule')
                return None  # Matched an exclusion rule

        # At this point, we need to generate a discovered name according to
        # the naming scheme for this type of BT.
        naming_scheme = entry_point_config['naming_scheme']
        name = transactions.get_http_bt_name(naming_scheme['properties'], request, base_name)
        return TransactionNamingMatch(name=name, naming_scheme=naming_scheme['type'])

    def update_config(self, tx_config):
        """Update the naming configuration for transactions and backends.

        Parameters
        ----------
        tx_config : appdynamics.agent.pb.TransactionConfig
            The transaction naming configuration from a
            :py:class:`appdynamics.agent.pb.ConfigResponse`.

        """
        self.entry_point_configs = {}

        for field_name, entry_point_match_name in self.ENTRY_TYPES.items():
            pt_config = getattr(tx_config, field_name)

            if not pt_config.IsInitialized() or not pt_config.enabled:
                continue  # No config, or entry point is disabled

            entry_type = pt_config.entryPointType

            # Extract custom match rules.
            custom_definitions = []

            for rule in pt_config.customDefinitions:
                custom_definitions.append({
                    'id': rule.id,
                    'name': u2b(rule.btName),
                    'priority': rule.priority,
                    'condition': getattr(rule.condition, entry_point_match_name),
                })

            custom_definitions.sort(key=lambda r: r['priority'])

            discovery_config = pt_config.discoveryConfig
            exclude_rules = []
            naming_scheme = None

            if discovery_config.enabled:
                properties = dict((p.name, p.value) for p in discovery_config.namingScheme.properties)

                # Headers are case insensitive, so lowercase them so that we have consistent casing.
                if properties.get('uri-suffix-scheme') == 'header-value':
                    properties['suffix-key'] = properties.get('suffix-key', '').lower()

                naming_scheme = {
                    'type': discovery_config.namingScheme.type,
                    'properties': properties,
                }

                for rule in discovery_config.excludes:
                    exclude_rules.append(getattr(rule, entry_point_match_name))

            self.entry_point_configs[entry_type] = {
                'custom_definitions': custom_definitions,
                'discovery_enabled': discovery_config.enabled,
                'naming_scheme': naming_scheme,
                'exclude_rules': exclude_rules,
            }


class ErrorConfigRegistry(object):
    """Contains configuration of ignored errors/exceptions.

    """
    WILDCARD_PATTERN = '*'

    def __init__(self):
        super(ErrorConfigRegistry, self).__init__()
        self.error_threshold = errors.PY_ERROR
        self.should_detect_errors = True
        self.mark_transaction_as_error = True
        self.ignored_exceptions = []
        self.ignored_errors = []
        self.http_status_codes = []

    def should_record_error(self, level, message):
        """Returns true if the error log should be recorded.

        This does NOT check whether the error is ignored.

        Parameters
        ----------
        level : int
            One of the logging levels from :py:mod:`logging`.
        message : str
            The log message.

        """
        if self.should_detect_errors and level >= self.error_threshold:
            return True

        return False

    def is_exception_ignored(self, exc):
        """Returns true if this exception is ignored for error reporting.

        IMPORTANT NOTE: Ignored exceptions are still reported as part of the
        BT and backend. Ignoring an exception controls whether the exception
        flags the BT as having an error. This is confusing, but that's the
        terminology already used everywhere else.

        Parameters
        ----------
        exc : errors.ExceptionInfo

        Returns
        -------
        ignored : bool
            True if the ignored exception configuration in this registry
            specifies that the exception should be ignored.

        """
        return any(_match_exception(exc, rule) for rule in self.ignored_exceptions)

    def is_error_ignored(self, error):
        """Returns true if this error log is ignored for error reporting.

        IMPORTANT NOTE: Unlike exceptions, ignored errors are not added to the BT.

        Parameters
        ----------
        error : errors.ErrorInfo

        Returns
        -------
        ignored : bool
            True if the error log is ignored according to the configuration
            stored in this registry.

        """
        if error.level < self.error_threshold:
            return True
        return any(conditions.match(error.message, match_cond) for match_cond in self.ignored_errors)

    def get_http_error(self, status_code, msg):
        """Return an ErrorInfo object if the status code should trigger an error.

        If the status code is in the error config and enabled, or the status code is >= 400,
        create and return an ErrorInfo object.  Otherwise, return False.

        """
        for error_code in self.http_status_codes:
            if status_code >= error_code.lowerBound and status_code <= error_code.upperBound:
                if error_code.enabled:
                    message = error_code.description
                    break
                else:
                    return False
        else:
            if status_code >= 400:
                    message = msg
            else:
                return False

        return errors.ErrorInfo(message, 'HTTP %d' % status_code, pb.PY_HTTP_ERROR)

    def update_config(self, error_config):
        if error_config.HasField('errorDetection'):
            detection = error_config.errorDetection
            self.should_detect_errors = bool(detection.detectErrors)
            self.mark_transaction_as_error = bool(self.should_detect_errors and detection.markTransactionAsError)

            if detection.HasField('pythonErrorThreshold'):
                self.error_threshold = detection.pythonErrorThreshold

        self.ignored_exceptions = []
        for exc in error_config.ignoredExceptions:
            class_name = exc.classNames[0] if exc.classNames else self.WILDCARD_PATTERN
            class_name = class_name or self.WILDCARD_PATTERN
            match_condition = exc.matchCondition if exc.HasField('matchCondition') else None

            if class_name or match_condition:
                self.ignored_exceptions.append((class_name, match_condition))

        self.ignored_errors = []
        for err in error_config.ignoredMessages:
            if err.HasField('matchCondition'):
                self.ignored_errors.append(err.matchCondition)

        self.http_status_codes = error_config.httpStatusCodes


def _match_exception(exc, rule):
    ignored_name, match_condition = rule
    name_matches = False

    if ignored_name == ErrorConfigRegistry.WILDCARD_PATTERN:
        name_matches = True
    else:
        if ignored_name.startswith('exceptions.') and '.' not in exc.klass:
            # The builtin exceptions can be matched qualified or unqualified.
            # That is, "ValueError" matches "exceptions.ValueError" as well as
            # "ValueError". (This is because the builtins are defined in the
            # exceptions module, so either way someone attempts to match them
            # should work.)
            options = (ignored_name, ignored_name[11:])
        else:
            options = (ignored_name,)

        for check in options:
            if exc.klass == check:
                name_matches = True
                break

    return name_matches and (match_condition is None or conditions.match(exc.message, match_condition))
