# -*- coding: utf-8 -*-
# Copyright (C) 2010 Samalyse SARL
# Copyright (C) 2010-2014 Parisson SARL

# This software is a computer program whose purpose is to backup, analyse,
# transcode and stream any audio content with its metadata over a web frontend.

# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
#
# Authors: Olivier Guilyardi <olivier@samalyse.com>
#          David LIPSZYC <davidlipszyc@gmail.com>
#          Guillaume Pellerin <yomguy@parisson.com>


from __future__ import division
from django.utils.translation import ugettext_lazy as _
from telemeta.models.core import *
from telemeta.models.query import *
from telemeta.models.identifier import *
from telemeta.models.resource import *

# Special code regex of collections for the branch
collection_published_code_regex = getattr(settings, 'COLLECTION_PUBLISHED_CODE_REGEX', '[A-Za-z0-9._-]*')
collection_unpublished_code_regex = getattr(settings, 'COLLECTION_UNPUBLISHED_CODE_REGEX', '[A-Za-z0-9._-]*')

# CREM
#collection_published_code_regex   = 'CNRSMH_E_[0-9]{4}(?:_[0-9]{3}){2}'
#collection_unpublished_code_regex = 'CNRSMH_I_[0-9]{4}_[0-9]{3}'

collection_code_regex = '(?:%s|%s)' % (collection_published_code_regex,
                                       collection_unpublished_code_regex)


class MediaCollection(MediaResource):
    "Describe a collection of items"

    element_type = 'collection'

    def is_valid_collection_code(value):
        "Check if the collection code is well formed"
        regex = '^' + collection_code_regex + '$'
        if not re.match(regex, value):
            raise ValidationError(u'%s is not a valid collection code' % value)

    # General informations
    title                 = CharField(_('title'), required=True)
    alt_title             = CharField(_('original title / translation'))
    creator               = CharField(_('depositor / contributor'), help_text=_('First name, Last name ; First name, Last name'))
    description           = TextField(_('description'))
    recording_context     = WeakForeignKey('RecordingContext', related_name="collections", verbose_name=_('recording context'))
    recorded_from_year    = IntegerField(_('recording year (from)'), help_text=_('YYYY'))
    recorded_to_year      = IntegerField(_('recording year (until)'), help_text=_('YYYY'))
    year_published        = IntegerField(_('year published'), help_text=_('YYYY'))
    public_access         = CharField(_('access type'), choices=PUBLIC_ACCESS_CHOICES, max_length=16, default="metadata")

    # Geographic and cultural informations
    # See "countries" and "ethnic_groups" methods below

    # Legal notices
    collector             = CharField(_('recordist'), help_text=_('First name, Last name ; First name, Last name'))
    publisher             = WeakForeignKey('Publisher', related_name="collections", verbose_name=_('publisher'))
    publisher_collection  = WeakForeignKey('PublisherCollection', related_name="collections", verbose_name=_('publisher collection'))
    publisher_serial      = CharField(_('publisher serial number'))
    booklet_author        = CharField(_('booklet author'), blank=True)
    reference             = CharField(_('publisher reference'))
    external_references   = TextField(_('bibliographic references'))

    auto_period_access    = BooleanField(_('automatic access after a rolling period'), default=True)
    legal_rights          = WeakForeignKey('LegalRight', related_name="collections", verbose_name=_('legal rights'))

    # Archiving data
    code                  = CharField(_('code'), unique=True, required=True, validators=[is_valid_collection_code])
    old_code              = CharField(_('old code'), unique=False, null=True, blank=True)
    acquisition_mode      = WeakForeignKey('AcquisitionMode', related_name="collections", verbose_name=_('mode of acquisition'))
    cnrs_contributor      = CharField(_('CNRS depositor'))
    copy_type             = WeakForeignKey('CopyType', related_name="collections", verbose_name=_('copy type'))
    metadata_author       = WeakForeignKey('MetadataAuthor', related_name="collections", verbose_name=_('record author'))
    booklet_description   = TextField(_('related documentation'))
    publishing_status     = WeakForeignKey('PublishingStatus', related_name="collections", verbose_name=_('secondary edition'))
    status                = WeakForeignKey('Status', related_name="collections", verbose_name=_('collection status'))
    alt_copies            = TextField(_('copies'))
    comment               = TextField(_('comment'))
    metadata_writer       = WeakForeignKey('MetadataWriter', related_name="collections", verbose_name=_('record writer'))
    archiver_notes        = TextField(_('archiver notes'))
    items_done            = CharField(_('items finished'))
    collector_is_creator  = BooleanField(_('recordist identical to depositor'))
    is_published          = BooleanField(_('published'))
    conservation_site     = CharField(_('conservation site'))

    # Technical data
    media_type            = WeakForeignKey('MediaType', related_name="collections", verbose_name=_('media type'))
    approx_duration       = DurationField(_('estimated duration'), help_text='hh:mm:ss')
    physical_items_num    = IntegerField(_('number of components (medium / piece)'))
    original_format       = WeakForeignKey('OriginalFormat', related_name="collections", verbose_name=_('original format'))
    physical_format       = WeakForeignKey('PhysicalFormat', related_name="collections", verbose_name=_('archive format'))
    ad_conversion         = WeakForeignKey('AdConversion', related_name='collections', verbose_name=_('digitization'))

    # No more used old fields
    alt_ids               = CharField(_('copies (obsolete field)'))
    travail               = CharField(_('archiver notes (obsolete field)'))

    # All
    objects               = MediaCollectionManager()

    exclude = ['alt_ids', 'travail']

    class Meta(MetaCore):
        db_table = 'media_collections'
        ordering = ['code']
        verbose_name = _('collection')

    def __unicode__(self):
        return self.code

    def save(self, force_insert=False, force_update=False, user=None, code=None):
        super(MediaCollection, self).save(force_insert, force_update)

    @property
    def public_id(self):
        return self.code

    @property
    def has_mediafile(self):
        "Tell wether this collection has any media files attached to its items"
        items = self.items.all()
        for item in items:
            if item.file:
                return True
        return False

    def __name_cmp(self, obj1, obj2):
        return unaccent_icmp(obj1.name, obj2.name)

    def countries(self):
        "Return the countries of the items"
        countries = []
        for item in self.items.filter(location__isnull=False):
            for country in item.location.countries():
                if not country in countries:
                    countries.append(country)
        countries.sort(self.__name_cmp)
        return countries
    countries.verbose_name = _("states / nations")

    def main_countries(self):
        "Return the main countries of the items (no aliases or ancestors)"
        countries = []
        for item in self.items.filter(location__isnull=False):
            if not item.location in countries:
                countries.append(item.location)
        countries.sort(self.__name_cmp)
        return countries
    main_countries.verbose_name = _("states / nations")

    def ethnic_groups(self):
        "Return the ethnic groups of the items"
        groups = []
        items = self.items.all()
        for item in items:
            if item.ethnic_group and not item.ethnic_group in groups:
                groups.append(item.ethnic_group)

        cmp = lambda a, b: unaccent_icmp(a.value, b.value)
        groups.sort(cmp)

        return groups
    ethnic_groups.verbose_name = _('populations / social groups')

    def computed_duration(self):
        duration = Duration()
        for item in self.items.all():
            duration += item.computed_duration()
        return duration
    computed_duration.verbose_name = _('computed duration')

    def computed_size(self):
        "Return the total size of a collection"
        size = 0
        for item in self.items.all():
            size += item.size()
        return size
    computed_size.verbose_name = _('collection size')

    def document_status(self):
        if '_I_' in self.public_id:
            return ugettext('Unpublished')
        elif '_E_' in self.public_id:
            return ugettext('Published')
        else:
            return ''

    def get_url(self):
        return get_full_url(reverse('telemeta-collection-detail', kwargs={'public_id':self.pk}))

    def to_dict_with_more(self):
        # metadata = model_to_dict(self, fields=[], exclude=self.exclude)
        metadata = self.to_dict()
        for key in self.exclude:
            if key in metadata.keys():
                del metadata[key]

        metadata['url'] = get_full_url(reverse('telemeta-collection-detail', kwargs={'public_id':self.pk}))
        metadata['doc_status'] = self.document_status()
        metadata['countries'] = ';'.join([location.name for location in self.main_countries()])
        metadata['ethnic_groups'] = ';'.join([group.value for group in self.ethnic_groups()])
        metadata['last_modification_date'] = unicode(self.get_revision().time)
        metadata['computed_duration'] = unicode(self.computed_duration())
        metadata['computed_size'] = unicode(self.computed_size())
        metadata['number_of_items'] = unicode(self.items.all().count())

        i = 0
        for media in self.related.all():
            metadata['related_media_title' + '_' + str(i)] = media.title
            if media.url:
                tag = 'related_media_url' + '_' + str(i)
                metadata[tag] = media.url
            elif media.url:
                metadata[tag] = get_full_url(reverse('telemeta-collection-related',
                                            kwargs={'public_id': self.public_id, 'media_id': media.id}))
            i += 1

        # One ID only
        identifiers = self.identifiers.all()
        if identifiers:
            identifier = identifiers[0]
            metadata['identifier_id'] = identifier.identifier
            metadata['identifier_type'] = identifier.type
            metadata['identifier_date'] = unicode(identifier.date_last)
            metadata['identifier_note'] = identifier.notes

        # All IDs
        # i = 0
        # for indentifier in self.identifiers.all():
        #     metadata['identifier' + '_' + str(i)] = identifier.identifier
        #     metadata['identifier_type' + '_' + str(i)] = identifier.type
        #     metadata['identifier_date_last' + '_' + str(i)] = unicode(identifier.date_last)
        #     metadata['identifier_notes' + '_' + str(i)] = identifier.notes
        #     i += 1

        return metadata


    def epub(self, filename):
        from epub.models import EPub
        e = EPub()
        e.metadata.title = self.title
        # e.metadata.add_creator(self.metadata_author)
        e.metadata.description = self.description
        e.metadata.publisher = self.publisher
        e.metadata.language = 'fr-FR'
        for item in self.items.all():
            e.add_article(item.title, item.comment)
        e.generate_epub(filename)



class MediaCollectionRelated(MediaRelated):
    "Collection related media"

    collection      = ForeignKey('MediaCollection', related_name="related", verbose_name=_('collection'))

    class Meta(MetaCore):
        db_table = 'media_collection_related'
        verbose_name = _('collection related media')
        verbose_name_plural = _('collection related media')


class MediaCollectionIdentifier(Identifier):
    """Collection identifier"""

    collection = ForeignKey(MediaCollection, related_name="identifiers", verbose_name=_('collection'))

    class Meta(MetaCore):
        db_table = 'media_collection_identifier'
        verbose_name = _('collection identifier')
        verbose_name_plural = _('collection identifiers')
        unique_together = ('identifier', 'collection')

