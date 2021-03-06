from __future__ import absolute_import
from __future__ import unicode_literals

from contextlib import closing

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import connections, models, transaction
from django.db.models import Q

from casexml.apps.phone.models import SyncLog
from corehq.apps.app_manager.models import Application
from corehq.apps.domain.models import Domain
from corehq.apps.groups.models import Group
from corehq.apps.locations.models import LocationType, SQLLocation
from corehq.apps.users.models import CouchUser
from corehq.form_processor.models import XFormInstanceSQL
from corehq.sql_db.routers import db_for_read_write
from corehq.warehouse.const import (APPLICATION_STAGING_SLUG,
    APP_STATUS_FACT_SLUG, APP_STATUS_FORM_STAGING_SLUG,
    APP_STATUS_SYNCLOG_STAGING_SLUG, DOMAIN_STAGING_SLUG, FORM_STAGING_SLUG,
    GROUP_STAGING_SLUG, LOCATION_STAGING_SLUG, SYNCLOG_STAGING_SLUG,
    USER_STAGING_SLUG, APPLICATION_DIM_SLUG, USER_DIM_SLUG, DOMAIN_DIM_SLUG)
from corehq.warehouse.dbaccessors import (get_application_ids_by_last_modified,
    get_domain_ids_by_last_modified, get_forms_by_last_modified,
    get_group_ids_by_last_modified, get_synclogs_by_date,
    get_user_ids_by_last_modified)
from corehq.warehouse.etl import HQToWarehouseETLMixin, CustomSQLETLMixin
from corehq.warehouse.models.shared import WarehouseTable
from corehq.warehouse.models.dimensions import ApplicationDim, UserDim
from corehq.warehouse.utils import truncate_records_for_cls
from dimagi.utils.couch.database import iter_docs


class StagingTable(models.Model, WarehouseTable):
    batch = models.ForeignKey(
        'Batch',
        on_delete=models.PROTECT,
    )

    class Meta(object):
        abstract = True

    @classmethod
    def commit(cls, batch):
        cls.clear_records()
        cls.load(batch)
        return True

    @classmethod
    def clear_records(cls):
        truncate_records_for_cls(cls, cascade=False)


class LocationStagingTable(StagingTable, HQToWarehouseETLMixin):
    '''
    Represents the staging table to dump data before loading into the LocationDim

    Grain: location_id
    '''
    slug = LOCATION_STAGING_SLUG

    domain = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    site_code = models.CharField(max_length=100)
    location_id = models.CharField(max_length=255)
    location_type_id = models.IntegerField()
    external_id = models.CharField(max_length=255, null=True)
    supply_point_id = models.CharField(max_length=255, null=True)
    user_id = models.CharField(max_length=255)

    sql_location_id = models.IntegerField()
    sql_parent_location_id = models.IntegerField(null=True)

    location_last_modified = models.DateTimeField(null=True)
    location_created_on = models.DateTimeField(null=True)

    is_archived = models.NullBooleanField()

    latitude = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=10, null=True)

    location_type_name = models.CharField(max_length=255)
    location_type_code = models.SlugField(db_index=False, null=True)

    location_type_last_modified = models.DateTimeField(null=True)

    @classmethod
    def field_mapping(cls):
        return [
            ('domain', 'domain'),
            ('name', 'name'),
            ('site_code', 'site_code'),
            ('location_id', 'location_id'),
            ('location_type_id', 'location_type_id'),
            ('external_id', 'external_id'),
            ('supply_point_id', 'supply_point_id'),
            ('user_id', 'user_id'),
            ('id', 'sql_location_id'),
            ('parent_id', 'sql_parent_location_id'),
            ('last_modified', 'location_last_modified'),
            ('created_at', 'location_created_on'),
            ('is_archived', 'is_archived'),
            ('latitude', 'latitude'),
            ('longitude', 'longitude'),
            ('location_type.name', 'location_type_name'),
            ('location_type.code', 'location_type_code'),
            ('location_type.last_modified', 'location_type_last_modified'),
        ]

    @classmethod
    def dependencies(cls):
        return []

    @classmethod
    def record_iter(cls, start_datetime, end_datetime):
        return SQLLocation.objects.filter(
            Q(last_modified__gt=start_datetime, last_modified__lte=end_datetime) |
            Q(location_type__last_modified__gt=start_datetime, location_type__last_modified__lte=end_datetime)
        ).select_related('location_type').iterator()


class GroupStagingTable(StagingTable, HQToWarehouseETLMixin):
    '''
    Represents the staging table to dump data before loading into the GroupDim

    Grain: group_id
    '''
    slug = GROUP_STAGING_SLUG

    group_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    user_ids = ArrayField(models.CharField(max_length=255), null=True)
    removed_user_ids = ArrayField(models.CharField(max_length=255), null=True)

    case_sharing = models.NullBooleanField()
    reporting = models.NullBooleanField()

    group_last_modified = models.DateTimeField(null=True)

    @classmethod
    def field_mapping(cls):
        return [
            ('_id', 'group_id'),
            ('domain', 'domain'),
            ('name', 'name'),
            ('case_sharing', 'case_sharing'),
            ('reporting', 'reporting'),
            ('last_modified', 'group_last_modified'),
            ('doc_type', 'doc_type'),
            ('users', 'user_ids'),
            ('removed_users', 'removed_user_ids'),
        ]

    @classmethod
    def dependencies(cls):
        return []

    @classmethod
    def record_iter(cls, start_datetime, end_datetime):
        group_ids = get_group_ids_by_last_modified(start_datetime, end_datetime)

        return iter_docs(Group.get_db(), group_ids)


class UserStagingTable(StagingTable, HQToWarehouseETLMixin):
    '''
    Represents the staging table to dump data before loading into the UserDim

    Grain: user_id
    '''
    slug = USER_STAGING_SLUG

    user_id = models.CharField(max_length=255)
    username = models.CharField(max_length=150)
    first_name = models.TextField(null=True)
    last_name = models.TextField(null=True)
    email = models.CharField(max_length=255, null=True)
    doc_type = models.CharField(max_length=100)
    base_doc = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, null=True, blank=True)

    assigned_location_ids = ArrayField(models.CharField(max_length=255), null=True)
    domain_memberships = JSONField(null=True)
    is_active = models.BooleanField()
    is_staff = models.BooleanField()
    is_superuser = models.BooleanField()

    last_login = models.DateTimeField(null=True)
    date_joined = models.DateTimeField()

    user_last_modified = models.DateTimeField(null=True)

    @classmethod
    def dependencies(cls):
        return []

    @classmethod
    def field_mapping(cls):
        return [
            ('_id', 'user_id'),
            ('username', 'username'),
            ('first_name', 'first_name'),
            ('last_name', 'last_name'),
            ('email', 'email'),
            ('domain', 'domain'),
            ('doc_type', 'doc_type'),
            ('base_doc', 'base_doc'),
            ('is_active', 'is_active'),
            ('is_staff', 'is_staff'),
            ('is_superuser', 'is_superuser'),
            ('last_login', 'last_login'),
            ('date_joined', 'date_joined'),
            ('last_modified', 'user_last_modified'),
            ('domain_memberships', 'domain_memberships'),
            ('assigned_location_ids', 'assigned_location_ids')
        ]

    @classmethod
    def record_iter(cls, start_datetime, end_datetime):
        user_ids = get_user_ids_by_last_modified(start_datetime, end_datetime)

        return iter_docs(CouchUser.get_db(), user_ids)


class DomainStagingTable(StagingTable, HQToWarehouseETLMixin):
    '''
    Represents the staging table to dump data before loading into the DomainDim

    Grain: domain_id
    '''
    slug = DOMAIN_STAGING_SLUG

    domain_id = models.CharField(max_length=255)
    domain = models.CharField(max_length=100)
    default_timezone = models.CharField(max_length=255)
    hr_name = models.CharField(max_length=255, null=True)
    creating_user_id = models.CharField(max_length=255, null=True)
    project_type = models.CharField(max_length=255, null=True)
    doc_type = models.CharField(max_length=100)

    is_active = models.BooleanField()
    case_sharing = models.BooleanField()
    commtrack_enabled = models.BooleanField()
    is_test = models.CharField(max_length=255)
    location_restriction_for_users = models.BooleanField()
    use_sql_backend = models.NullBooleanField()
    first_domain_for_user = models.NullBooleanField()

    domain_last_modified = models.DateTimeField(null=True)
    domain_created_on = models.DateTimeField(null=True)

    @classmethod
    def dependencies(cls):
        return []

    @classmethod
    def field_mapping(cls):
        return [
            ('_id', 'domain_id'),
            ('name', 'domain'),
            ('default_timezone', 'default_timezone'),
            ('hr_name', 'hr_name'),
            ('creating_user_id', 'creating_user_id'),
            ('project_type', 'project_type'),

            ('is_active', 'is_active'),
            ('case_sharing', 'case_sharing'),
            ('commtrack_enabled', 'commtrack_enabled'),
            ('is_test', 'is_test'),
            ('location_restriction_for_users', 'location_restriction_for_users'),
            ('use_sql_backend', 'use_sql_backend'),
            ('first_domain_for_user', 'first_domain_for_user'),

            ('last_modified', 'domain_last_modified'),
            ('date_created', 'domain_created_on'),
            ('doc_type', 'doc_type'),
        ]

    @classmethod
    def record_iter(cls, start_datetime, end_datetime):
        domain_ids = get_domain_ids_by_last_modified(start_datetime, end_datetime)

        return iter_docs(Domain.get_db(), domain_ids)


class FormStagingTable(StagingTable, HQToWarehouseETLMixin):
    '''
    Represents the staging table to dump data before loading into the FormFact

    Grain: form_id
    '''
    slug = FORM_STAGING_SLUG

    form_id = models.CharField(max_length=255, unique=True)

    domain = models.CharField(max_length=255, default=None)
    app_id = models.CharField(max_length=255, null=True)
    xmlns = models.CharField(max_length=255, default=None)
    user_id = models.CharField(max_length=255, null=True)

    # The time at which the server has received the form
    received_on = models.DateTimeField(db_index=True)
    deleted_on = models.DateTimeField(null=True)
    edited_on = models.DateTimeField(null=True)

    time_end = models.DateTimeField(null=True, blank=True)
    time_start = models.DateTimeField(null=True, blank=True)
    commcare_version = models.CharField(max_length=8, blank=True, null=True)
    app_version = models.PositiveIntegerField(null=True, blank=True)

    build_id = models.CharField(max_length=255, null=True)

    state = models.PositiveSmallIntegerField(
        choices=XFormInstanceSQL.STATES,
        default=XFormInstanceSQL.NORMAL
    )

    @classmethod
    def dependencies(cls):
        return []

    @classmethod
    def field_mapping(cls):
        return [
            ('form_id', 'form_id'),
            ('domain', 'domain'),
            ('app_id', 'app_id'),
            ('xmlns', 'xmlns'),
            ('user_id', 'user_id'),

            ('received_on', 'received_on'),
            ('deleted_on', 'deleted_on'),
            ('edited_on', 'edited_on'),
            ('build_id', 'build_id'),

            ('time_end', 'time_end'),
            ('time_start', 'time_start'),
            ('commcare_version', 'commcare_version'),
            ('app_version', 'app_version'),
        ]

    @classmethod
    def record_iter(cls, start_datetime, end_datetime):
        return get_forms_by_last_modified(start_datetime, end_datetime)


class SyncLogStagingTable(StagingTable, HQToWarehouseETLMixin):
    '''
    Represents the staging table to dump data before loading into the SyncLogFact

    Grain: sync_log_id
    '''
    slug = SYNCLOG_STAGING_SLUG

    sync_log_id = models.CharField(max_length=255)
    sync_date = models.DateTimeField(null=True)

    # this is only added as of 11/2016 - not guaranteed to be set
    domain = models.CharField(max_length=255, null=True)
    user_id = models.CharField(max_length=255, null=True)

    # this is only added as of 11/2016 and only works with app-aware sync
    build_id = models.CharField(max_length=255, null=True)

    duration = models.IntegerField(null=True)  # in seconds

    @classmethod
    def dependencies(cls):
        return []

    @classmethod
    def field_mapping(cls):
        return [
            ('synclog_id', 'sync_log_id'),
            ('date', 'sync_date'),
            ('domain', 'domain'),
            ('user_id', 'user_id'),
            ('build_id', 'build_id'),
            ('duration', 'duration'),
        ]

    @classmethod
    def record_iter(cls, start_datetime, end_datetime):
        return get_synclogs_by_date(start_datetime, end_datetime)


class ApplicationStagingTable(StagingTable, HQToWarehouseETLMixin):
    '''
    Represents the staging table to dump data before loading into the ApplicationDim

    Grain: application_id
    '''
    slug = APPLICATION_STAGING_SLUG

    application_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=100)
    application_last_modified = models.DateTimeField(null=True)
    doc_type = models.CharField(max_length=100)
    version = models.IntegerField(null=True)
    copy_of = models.CharField(max_length=255, null=True, blank=True)

    @classmethod
    def field_mapping(cls):
        return [
            ('_id', 'application_id'),
            ('domain', 'domain'),
            ('name', 'name'),
            ('last_modified', 'application_last_modified'),
            ('doc_type', 'doc_type'),
            ('version', 'version'),
            ('copy_of', 'copy_of'),
        ]

    @classmethod
    def dependencies(cls):
        return []

    @classmethod
    def record_iter(cls, start_datetime, end_datetime):
        application_ids = get_application_ids_by_last_modified(start_datetime, end_datetime)

        return iter_docs(Application.get_db(), application_ids)


class AppStatusFormStaging(StagingTable, CustomSQLETLMixin):

    slug = APP_STATUS_FORM_STAGING_SLUG

    domain = models.CharField(max_length=255, default=None, db_index=True)
    app_dim = models.ForeignKey(ApplicationDim, on_delete=models.PROTECT, null=True)
    user_dim = models.ForeignKey(UserDim, on_delete=models.PROTECT)
    last_submission = models.DateTimeField(db_index=True)
    submission_build_version = models.CharField(max_length=255, null=True, db_index=True)
    commcare_version = models.CharField(max_length=255, null=True, db_index=True)

    @classmethod
    def dependencies(cls):
        return [
            FORM_STAGING_SLUG,
            APP_STATUS_FACT_SLUG,
            APPLICATION_DIM_SLUG,
            USER_DIM_SLUG,
            DOMAIN_DIM_SLUG
        ]


class AppStatusSynclogStaging(StagingTable, CustomSQLETLMixin):

    slug = APP_STATUS_SYNCLOG_STAGING_SLUG

    last_sync = models.DateTimeField(null=True, db_index=True)
    domain = models.CharField(max_length=255, null=True, db_index=True)
    user_dim = models.ForeignKey(UserDim, on_delete=models.PROTECT)

    @classmethod
    def dependencies(cls):
        return [
            SYNCLOG_STAGING_SLUG,
            APP_STATUS_FACT_SLUG,
            APPLICATION_DIM_SLUG,
            USER_DIM_SLUG,
            DOMAIN_DIM_SLUG
        ]
