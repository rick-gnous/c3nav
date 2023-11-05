from collections import UserDict
from functools import cached_property
from operator import attrgetter
from typing import Any, Mapping, Self

from django.contrib.auth import get_user_model
from django.db import NotSupportedError, models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from c3nav.mesh.dataformats import BoardType
from c3nav.mesh.messages import ChipType
from c3nav.mesh.messages import MeshMessage as MeshMessage
from c3nav.mesh.messages import MeshMessageType


class MeshNodeQuerySet(models.QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._prefetch_last_messages = set()
        self._prefetch_last_messages_done = False

    def _clone(self):
        clone = super()._clone()
        clone._prefetch_last_messages = self._prefetch_last_messages
        return clone

    def prefetch_last_messages(self, *types: MeshMessageType):
        clone = self._chain()
        clone._prefetch_last_messages |= (
            set(types) if types else set(msgtype for msgtype in MeshMessageType)
        )
        return clone

    def _fetch_all(self):
        super()._fetch_all()
        if self._prefetch_last_messages and not self._prefetch_last_messages_done:
            nodes = {node.pk: node for node in self._result_cache}
            try:
                for message in NodeMessage.objects.order_by('message_type', 'src_node', '-datetime', '-pk').filter(
                        message_type__in=(t.name for t in self._prefetch_last_messages),
                        src_node__in=nodes.keys(),
                ).prefetch_related("uplink_node").distinct('message_type', 'src_node'):
                    nodes[message.src_node_id].last_messages[message.message_type] = message
                for node in nodes.values():
                    node.last_messages["any"] = max(node.last_messages.values(), key=attrgetter("datetime"))
            except NotSupportedError:
                pass


class LastMessagesByTypeLookup(UserDict):
    def __init__(self, node):
        super().__init__()
        self.node = node

    def _get_key(self, item):
        if isinstance(item, MeshMessageType):
            return item
        if isinstance(item, str):
            try:
                return getattr(MeshMessageType, item)
            except AttributeError:
                pass
        return MeshMessageType(item)

    def __getitem__(self, key):
        if key == "any":
            msg = self.node.received_messages.order_by('-datetime', '-pk').first()
            self.data["any"] = msg
            return msg
        key = self._get_key(key)
        try:
            return self.data[key]
        except KeyError:
            pass
        msg = self.node.received_messages.filter(message_type=key.name).order_by('-datetime', '-pk').first()
        self.data[key] = msg
        return msg

    def __setitem__(self, key, item):
        if key == "any":
            self.data["any"] = item
            return
        self.data[self._get_key(key)] = item


class MeshNode(models.Model):
    address = models.CharField(_('mac address'), max_length=17, primary_key=True)
    name = models.CharField(_('name'), max_length=32, null=True, blank=True)
    first_seen = models.DateTimeField(_('first seen'), auto_now_add=True)
    uplink = models.ForeignKey('MeshNode', models.PROTECT, null=True,
                               related_name='routed_nodes', verbose_name=_('uplink'))
    last_signin = models.DateTimeField(_('last signin'), null=True)
    objects = models.Manager.from_queryset(MeshNodeQuerySet)()

    def __str__(self):
        if self.name:
            return '%s (%s)' % (self.address, self.name)
        return self.address

    @cached_property
    def last_messages(self) -> Mapping[Any, Self]:
        return LastMessagesByTypeLookup(self)


class NodeMessage(models.Model):
    MESSAGE_TYPES = [(msgtype.name, msgtype.pretty_name) for msgtype in MeshMessageType]
    src_node = models.ForeignKey('MeshNode', models.PROTECT,
                                 related_name='received_messages', verbose_name=_('node'))
    uplink_node = models.ForeignKey('MeshNode', models.PROTECT,
                                    related_name='relayed_messages', verbose_name=_('uplink node'))
    datetime = models.DateTimeField(_('datetime'), db_index=True, auto_now_add=True)
    message_type = models.CharField(_('message type'), max_length=24, db_index=True, choices=MESSAGE_TYPES)
    data = models.JSONField(_('message data'))

    def __str__(self):
        return '(#%d) %s at %s' % (self.pk, self.get_message_type_display(), self.datetime)

    @cached_property
    def parsed(self) -> dict:
        return MeshMessage.fromjson(self.data)


class FirmwareVersion(models.Model):
    project_name = models.CharField(_('project name'), max_length=32)
    version = models.CharField(_('firmware version'), max_length=32, unique=True)
    idf_version = models.CharField(_('IDF version'), max_length=32)
    uploader = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(_('creation/upload date'), auto_now_add=True)

    def serialize(self):
        return {
            'project_name': self.project_name,
            'version': self.version,
            'idf_version': self.idf_version,
            'created': self.created.isoformat(),
            'builds': {
                build.variant: build.serialize()
                for build in self.builds.all().prefetch_related("firmwarebuildboard_set")
            }
        }


def firmware_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    version = slugify(instance.version.version)
    variant = slugify(instance.variant)
    return f"firmware/{version}/{variant}/{filename}"


class FirmwareBuild(models.Model):
    CHIPS = [(chiptype.value, chiptype.pretty_name) for chiptype in ChipType]

    version = models.ForeignKey(FirmwareVersion, related_name='builds', on_delete=models.CASCADE)
    variant = models.CharField(_('variant name'), max_length=64)
    chip = models.SmallIntegerField(_('chip'), db_index=True, choices=CHIPS)
    sha256_hash = models.CharField(_('SHA256 hash'), unique=True, max_length=64)
    project_description = models.JSONField(verbose_name=_('project_description.json'))
    binary = models.FileField(_('firmware file'), null=True, upload_to=firmware_upload_path)

    class Meta:
        unique_together = [
            ('version', 'variant'),
        ]

    @property
    def boards(self):
        return [board.board for board in self.firmwarebuildboard_set.all()]

    def serialize(self):
        return {
            'chip': ChipType(self.chip).name,
            'sha256_hash': self.sha256_hash,
            'url': self.binary.url,
            'boards': self.boards,
        }


class FirmwareBuildBoard(models.Model):
    BOARDS = [(boardtype.name, boardtype.pretty_name) for boardtype in BoardType]
    build = models.ForeignKey(FirmwareBuild, on_delete=models.CASCADE)
    board = models.CharField(_('board'), max_length=32, db_index=True, choices=BOARDS)

    class Meta:
        unique_together = [
            ('build', 'board'),
        ]
