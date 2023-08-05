import boto
import functools
import json
import logging
import random
import urllib
from urlparse import urlparse

from radosgw_agent import request as aws_request
from boto.exception import BotoServerError
from boto.s3.connection import S3Connection

log = logging.getLogger(__name__)

class Endpoint(object):
    def __init__(self, host, port, secure,
                 access_key=None, secret_key=None, region=None, zone=None):
        self.host = host
        default_port = 443 if secure else 80
        self.port = port or default_port
        self.secure = secure
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.zone = zone

    def __eq__(self, other):
        if self.host != other.host:
            return False
        if self.port == other.port:
            return True
        # if self and other are mixed http/https with default ports,
        # i.e. http://example.com and https://example.com, consider
        # them the same
        def diff_only_default_ports(a, b):
            return a.secure and a.port == 443 and not b.secure and b.port == 80
        return (diff_only_default_ports(self, other) or
                diff_only_default_ports(other, self))

    def __repr__(self):
        return 'Endpoint(host={host}, port={port}, secure={secure})'.format(
            host=self.host,
            port=self.port,
            secure=self.secure)

    def __str__(self):
        scheme = 'https' if self.secure else 'http'
        return '{scheme}://{host}:{port}'.format(scheme=scheme,
                                                 host=self.host,
                                                 port=self.port)

class ClientException(Exception):
    pass
class InvalidProtocol(ClientException):
    pass
class InvalidHost(ClientException):
    pass
class InvalidZone(ClientException):
    pass
class ZoneNotFound(ClientException):
    pass
class BucketEmpty(ClientException):
    pass

def parse_endpoint(endpoint):
    url = urlparse(endpoint)
    if url.scheme not in ['http', 'https']:
        raise InvalidProtocol('invalid protocol %r' % url.scheme)
    if not url.hostname:
        raise InvalidHost('no hostname in %r' % endpoint)
    return Endpoint(url.hostname, url.port, url.scheme == 'https')

class HttpError(ClientException):
    def __init__(self, code, body):
        self.code = code
        self.str_code = str(code)
        self.body = body
        self.message = 'Http error code %s content %s' % (code, body)
    def __str__(self):
        return self.message
class NotFound(HttpError):
    pass
code_to_exc = {
    404: NotFound,
    }

def boto_call(func):
    @functools.wraps(func)
    def translate_exception(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except boto.exception.S3ResponseError as e:
            raise code_to_exc.get(e.status, HttpError)(e.status, e.body)
    return translate_exception


def check_result_status(result):
    if result.status / 100 != 2:
        raise code_to_exc.get(result.status,
                              HttpError)(result.status, result.reason)
def url_safe(component):
    if isinstance(component, basestring):
        string = component.encode('utf8')
    else:
        string = str(component)
    return urllib.quote(string)

def request(connection, type_, resource, params=None, headers=None,
            data=None, expect_json=True, special_first_param=None, _retries=3):
    if headers is None:
        headers = {}

    if type_ in ['put', 'post']:
        headers['Content-Type'] = 'application/json; charset=UTF-8'

    request_data = data if data else ''
    if params is None:
        params = {}
    safe_params = dict([(k, url_safe(v)) for k, v in params.iteritems()])
    connection.count_request()
    request = aws_request.base_http_request(connection.s3_connection,
                             type_.upper(),
                             resource=resource,
                             special_first_param=special_first_param,
                             headers=headers,
                             data=request_data,
                             params=safe_params)

    url = '{protocol}://{host}{path}'.format(protocol=request.protocol,
                                             host=request.host,
                                             path=request.path)

    request.authorize(connection=connection)

    boto.log.debug('url = %r\nparams=%r\nheaders=%r\ndata=%r',
                   url, params, request.headers, data)
    try:
        result = aws_request.make_request(
            connection.s3_connection,
            type_.upper(),
            resource=resource,
            special_first_param=special_first_param,
            headers=headers,
            data=request_data,
            params=safe_params,
            _retries=_retries)
    except BotoServerError as error:
        check_result_status(error)

    check_result_status(result)

    if data or not expect_json:
        return result

    return json.loads(result.read())


def get_metadata(connection, section, name):
    return request(connection, 'get', 'admin/metadata/' + section,
                   params=dict(key=name))


def update_metadata(connection, section, name, metadata):
    if not isinstance(metadata, basestring):
        metadata = json.dumps(metadata)
    return request(connection, 'put', 'admin/metadata/' + section,
                   params=dict(key=name), data=metadata)


def delete_metadata(connection, section, name):
    return request(connection, 'delete', 'admin/metadata/' + section,
                   params=dict(key=name), expect_json=False)


def get_metadata_sections(connection):
    return request(connection, 'get', 'admin/metadata')


def list_metadata_keys(connection, section):
    return request(connection, 'get', 'admin/metadata/' + section)


def get_op_state(connection, client_id, op_id, bucket, obj):
    return request(connection, 'get', 'admin/opstate',
                   params={
                       'op-id': op_id,
                       'object': u'{0}/{1}'.format(bucket, obj),
                       'client-id': client_id,
                      }
                   )


def remove_op_state(connection, client_id, op_id, bucket, obj):
    return request(connection, 'delete', 'admin/opstate',
                   params={
                       'op-id': op_id,
                       'object': u'{0}/{1}'.format(bucket, obj),
                       'client-id': client_id,
                      },
                   expect_json=False,
                   )

def get_bucket_list(connection):
    return list_metadata_keys(connection, 'bucket')


@boto_call
def list_objects_in_bucket(connection, bucket_name):
    # use the boto library to do this
    bucket = connection.get_bucket(bucket_name)
    try:
        for key in bucket.list():
            yield key.name
    except boto.exception.S3ResponseError as e:
        # since this is a generator, the exception will be raised when
        # it's read, rather than when this call returns, so raise a
        # unique exception to distinguish this from client errors from
        # other calls
        if e.status == 404:
            raise BucketEmpty()
        else:
            raise


@boto_call
def delete_object(connection, bucket_name, object_name):
    bucket = connection.get_bucket(bucket_name)
    bucket.delete_key(object_name)


def sync_object_intra_region(connection, bucket_name, object_name, src_zone,
                             client_id, op_id):
    path = u'{bucket}/{object}'.format(
        bucket=bucket_name,
        object=object_name,
        )
    return request(connection, 'put', path,
                   params={
                       'rgwx-source-zone': src_zone,
                       'rgwx-client-id': client_id,
                       'rgwx-op-id': op_id,
                       },
                   headers={
                       'x-amz-copy-source': url_safe('%s/%s' % (bucket_name, object_name)),
                       },
                   expect_json=False)


def lock_shard(connection, lock_type, shard_num, zone_id, timeout, locker_id):
    return request(connection, 'post', 'admin/log',
                   params={
                       'type': lock_type,
                       'id': shard_num,
                       'length': timeout,
                       'zone-id': zone_id,
                       'locker-id': locker_id,
                       },
                   special_first_param='lock',
                   expect_json=False)


def unlock_shard(connection, lock_type, shard_num, zone_id, locker_id):
    return request(connection, 'post', 'admin/log',
                   params={
                       'type': lock_type,
                       'id': shard_num,
                       'locker-id': locker_id,
                       'zone-id': zone_id,
                       },
                   special_first_param='unlock',
                   expect_json=False)


def _id_name(type_):
    return 'bucket-instance' if type_ == 'bucket-index' else 'id'


def get_log(connection, log_type, marker, max_entries, id_):
    key = _id_name(log_type)
    return request(connection, 'get', 'admin/log',
                   params={
                       'type': log_type,
                       key: id_,
                       'marker': marker,
                       'max-entries': max_entries,
                       },
                   )


def get_log_info(connection, log_type, id_):
    key = _id_name(log_type)
    return request(
        connection, 'get', 'admin/log',
        params={
            'type': log_type,
            key: id_,
            },
        special_first_param='info',
        )


def num_log_shards(connection, shard_type):
    out = request(connection, 'get', 'admin/log', dict(type=shard_type))
    return out['num_objects']


def set_worker_bound(connection, type_, marker, timestamp,
                     daemon_id, id_, data=None):
    if data is None:
        data = []
    key = _id_name(type_)
    boto.log.debug('set_worker_bound: data = %r', data)
    return request(
        connection, 'post', 'admin/replica_log',
        params={
            'type': type_,
            key: id_,
            'marker': marker,
            'time': timestamp,
            'daemon_id': daemon_id,
            },
        data=json.dumps(data),
        special_first_param='work_bound',
        )


def del_worker_bound(connection, type_, daemon_id, id_):
    key = _id_name(type_)
    return request(
        connection, 'delete', 'admin/replica_log',
        params={
            'type': type_,
            key: id_,
            'daemon_id': daemon_id,
            },
        special_first_param='work_bound',
        expect_json=False,
        )


def get_worker_bound(connection, type_, id_):
    key = _id_name(type_)
    out = request(
        connection, 'get', 'admin/replica_log',
        params={
            'type': type_,
            key: id_,
            },
        special_first_param='bounds',
        )
    boto.log.debug('get_worker_bound returned: %r', out)
    retries = set()
    for item in out['markers']:
        names = [retry['name'] for retry in item['items_in_progress']]
        retries = retries.union(names)
    return out['marker'], out['oldest_time'], retries


class Zone(object):
    def __init__(self, zone_info):
        self.name = zone_info['name']
        self.is_master = False
        self.endpoints = [parse_endpoint(e) for e in zone_info['endpoints']]
        self.log_meta = zone_info['log_meta'] == 'true'
        self.log_data = zone_info['log_data'] == 'true'

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name


class Region(object):
    def __init__(self, region_info):
        self.name = region_info['key']
        self.is_master = region_info['val']['is_master'] == 'true'
        self.zones = {}
        for zone_info in region_info['val']['zones']:
            zone = Zone(zone_info)
            self.zones[zone.name] = zone
            if zone.name == region_info['val']['master_zone']:
                zone.is_master = True
                self.master_zone = zone
        assert hasattr(self, 'master_zone'), \
               'No master zone found for region ' + self.name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.zones.keys())


class RegionMap(object):
    def __init__(self, region_map):
        self.regions = {}
        for region_info in region_map['regions']:
            region = Region(region_info)
            self.regions[region.name] = region
            if region.is_master:
                self.master_region = region
        assert hasattr(self, 'master_region'), \
               'No master region found in region map'

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.regions)

    def find_endpoint(self, endpoint):
        for region in self.regions.itervalues():
            for zone in region.zones.itervalues():
                if endpoint in zone.endpoints or endpoint.zone == zone.name:
                    return region, zone
        raise ZoneNotFound('%s not found in region map' % endpoint)


def get_region_map(connection):
    region_map = request(connection, 'get', 'admin/config')
    return RegionMap(region_map)


def _validate_sync_dest(dest_region, dest_zone):
    if dest_region.is_master and dest_zone.is_master:
        raise InvalidZone('destination cannot be master zone of master region')


def _validate_sync_source(src_region, src_zone, dest_region, dest_zone,
                          meta_only):
    if not src_zone.is_master:
        raise InvalidZone('source zone %s must be a master zone' % src_zone.name)
    if (src_region.name == dest_region.name and
        src_zone.name == dest_zone.name):
        raise InvalidZone('source and destination must be different zones')
    if not src_zone.log_meta:
        raise InvalidZone('source zone %s must have metadata logging enabled' % src_zone.name)
    if not meta_only and not src_zone.log_data:
        raise InvalidZone('source zone %s must have data logging enabled' % src_zone.name)
    if not meta_only and src_region.name != dest_region.name:
        raise InvalidZone('data sync can only occur between zones in the same region')
    if not src_zone.endpoints:
        raise InvalidZone('region map contains no endpoints for default source zone %s' % src_zone.name)

def configure_endpoints(region_map, dest_endpoint, src_endpoint, meta_only):
    print('region map is: %r' % region_map)

    dest_region, dest_zone = region_map.find_endpoint(dest_endpoint)
    _validate_sync_dest(dest_region, dest_zone)

    # source may be specified by http endpoint or zone name
    if src_endpoint.host or src_endpoint.zone:
        src_region, src_zone = region_map.find_endpoint(src_endpoint)
    else:
        # try the master zone in the same region, then the master zone
        # in the master region
        try:
            _validate_sync_source(dest_region, dest_region.master_zone,
                                  dest_region, dest_zone, meta_only)
            src_region, src_zone = dest_region, dest_region.master_zone
        except InvalidZone as e:
            log.debug('source region %s zone %s unaccetpable: %s',
                      dest_region.name, dest_region.master_zone.name, e)
            master_region = region_map.master_region
            src_region, src_zone = master_region, master_region.master_zone

    _validate_sync_source(src_region, src_zone, dest_region, dest_zone,
                          meta_only)

    # choose a random source endpoint if one wasn't specified
    if not src_endpoint.host:
        endpoint = random.choice(src_zone.endpoints)
        src_endpoint.host = endpoint.host
        src_endpoint.port = endpoint.port
        src_endpoint.secure = endpoint.secure

    # fill in region and zone names
    dest_endpoint.region = dest_region
    dest_endpoint.zone = dest_zone
    src_endpoint.region = src_region
    src_endpoint.zone = src_zone

class S3ConnectionWrapper(object):
    def __init__(self, endpoint, debug):
        self.endpoint = endpoint
        self.debug = debug
        self.s3_connection = None
        self.reqs_before_reset = 512
        self._recreate_s3_connection()

    def count_request(self):
        self.num_requests += 1
        if self.num_requests > self.reqs_before_reset:
            self._recreate_s3_connection()

    def _recreate_s3_connection(self):
        self.num_requests = 0
        self.s3_connection = S3Connection(
            aws_access_key_id=self.endpoint.access_key,
            aws_secret_access_key=self.endpoint.secret_key,
            is_secure=self.endpoint.secure,
            host=self.endpoint.host,
            port=self.endpoint.port,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
            debug=self.debug,
        )

    def __getattr__(self, attrib):
        return getattr(self.s3_connection, attrib)

def connection(endpoint, debug=None):
    return S3ConnectionWrapper(endpoint, debug)
