from bingads.bulk.entities import *
from bingads.bulk.entities.ad_extensions.bulk_site_links_ad_extensions import _SiteLinkAdExtensionIdentifier
from bingads.bulk.entities.ad_extensions.bulk_product_ad_extensions import _BulkProductAdExtensionIdentifier
from bingads.bulk.entities.targets.bulk_targets import _BulkCampaignTargetIdentifier, \
    _BulkAdGroupTargetIdentifier, _BulkTargetIdentifier

from bingads.internal.bulk.string_table import _StringTable
from bingads.internal.bulk.entity_info import _EntityInfo
from bingads.bulk.entities.bulk_negative_sites import _BulkAdGroupNegativeSitesIdentifier, \
    _BulkCampaignNegativeSitesIdentifier
from bingads.internal.bulk.format_version import _FormatVersion


class _BulkObjectFactory():
    INDIVIDUAL_ENTITY_MAP = {
        _StringTable.Account: _EntityInfo(lambda: BulkAccount()),
        _StringTable.Campaign: _EntityInfo(lambda: BulkCampaign()),
        _StringTable.AdGroup: _EntityInfo(lambda: BulkAdGroup()),
        _StringTable.Keyword: _EntityInfo(lambda: BulkKeyword()),
        _StringTable.SiteLinksAdExtension: _EntityInfo(
            lambda: BulkSiteLink(),
            _StringTable.SiteLinkExtensionOrder,
            lambda: _SiteLinkAdExtensionIdentifier()
        ),
        _StringTable.CampaignSiteLinksAdExtension: _EntityInfo(
            lambda: BulkCampaignSiteLinkAdExtension()
        ),
        _StringTable.AdGroupSiteLinksAdExtension: _EntityInfo(
            lambda: BulkAdGroupSiteLinkAdExtension()
        ),
        _StringTable.ProductAdExtension: _EntityInfo(
            lambda: BulkProductConditionCollection(),
            _StringTable.BingMerchantCenterId,
            lambda: _BulkProductAdExtensionIdentifier(),
        ),
        _StringTable.CampaignProductAdExtension: _EntityInfo(
            lambda: BulkCampaignProductAdExtension()
        ),
        _StringTable.CallAdExtension: _EntityInfo(lambda: BulkCallAdExtension()),
        _StringTable.CampaignCallAdExtension: _EntityInfo(lambda: BulkCampaignCallAdExtension()),
        _StringTable.ImageAdExtension: _EntityInfo(lambda: BulkImageAdExtension()),
        _StringTable.CampaignImageAdExtension: _EntityInfo(lambda: BulkCampaignImageAdExtension()),
        _StringTable.AdGroupImageAdExtension: _EntityInfo(lambda: BulkAdGroupImageAdExtension()),
        _StringTable.LocationAdExtension: _EntityInfo(lambda: BulkLocationAdExtension()),
        _StringTable.CampaignLocationAdExtension: _EntityInfo(lambda: BulkCampaignLocationAdExtension()),
        _StringTable.MobileAd: _EntityInfo(lambda: BulkMobileAd()),
        _StringTable.ProductAd: _EntityInfo(lambda: BulkProductAd()),
        _StringTable.TextAd: _EntityInfo(lambda: BulkTextAd()),
        "Campaign Negative Site": _EntityInfo(
            lambda: BulkCampaignNegativeSite(),
            _StringTable.Website,
            lambda: _BulkCampaignNegativeSitesIdentifier()
        ),
        "Ad Group Negative Site": _EntityInfo(
            lambda: BulkAdGroupNegativeSite(),
            _StringTable.Website,
            lambda: _BulkAdGroupNegativeSitesIdentifier()
        ),
        "Ad Group Product Target": _EntityInfo(lambda: BulkAdGroupProductTarget()),

        _StringTable.NegativeKeywordList: _EntityInfo(lambda: BulkNegativeKeywordList()),
        _StringTable.ListNegativeKeyword: _EntityInfo(lambda: BulkSharedNegativeKeyword()),
        _StringTable.CampaignNegativeKeywordList: _EntityInfo(lambda: BulkCampaignNegativeKeywordList()),
        _StringTable.CampaignNegativeKeyword: _EntityInfo(lambda: BulkCampaignNegativeKeyword()),
        _StringTable.AdGroupNegativeKeyword: _EntityInfo(lambda: BulkAdGroupNegativeKeyword()),
        'Ad Group Age Target': _EntityInfo(
            lambda: BulkAdGroupAgeTargetBid(),
            _StringTable.Target,
            lambda: _BulkAdGroupTargetIdentifier(target_bid_type=BulkAdGroupAgeTargetBid)
        ),
        'Campaign Age Target': _EntityInfo(
            lambda: BulkCampaignAgeTargetBid(),
            _StringTable.Target,
            lambda: _BulkCampaignTargetIdentifier(target_bid_type=BulkCampaignAgeTargetBid)
        ),
        'Ad Group DayTime Target': _EntityInfo(
            lambda: BulkAdGroupDayTimeTargetBid(),
            _StringTable.Target,
            lambda: _BulkAdGroupTargetIdentifier(target_bid_type=BulkAdGroupDayTimeTargetBid)
        ),
        'Campaign DayTime Target': _EntityInfo(
            lambda: BulkCampaignDayTimeTargetBid(),
            _StringTable.Target,
            lambda: _BulkCampaignTargetIdentifier(target_bid_type=BulkCampaignDayTimeTargetBid)
        ),
        'Ad Group DeviceOS Target': _EntityInfo(
            lambda: BulkAdGroupDeviceOsTargetBid(),
            _StringTable.Target,
            lambda: _BulkAdGroupTargetIdentifier(target_bid_type=BulkAdGroupDeviceOsTargetBid)
        ),
        'Campaign DeviceOS Target': _EntityInfo(
            lambda: BulkCampaignDeviceOsTargetBid(),
            _StringTable.Target,
            lambda: _BulkCampaignTargetIdentifier(target_bid_type=BulkCampaignDeviceOsTargetBid)
        ),
        'Ad Group Gender Target': _EntityInfo(
            lambda: BulkAdGroupGenderTargetBid(),
            _StringTable.Target,
            lambda: _BulkAdGroupTargetIdentifier(target_bid_type=BulkAdGroupGenderTargetBid)
        ),
        'Campaign Gender Target': _EntityInfo(
            lambda: BulkCampaignGenderTargetBid(),
            _StringTable.Target,
            lambda: _BulkCampaignTargetIdentifier(target_bid_type=BulkCampaignGenderTargetBid)
        ),
        'Ad Group Location Target': _EntityInfo(
            lambda: BulkAdGroupLocationTargetBid(),
            _StringTable.Target,
            lambda: _BulkAdGroupTargetIdentifier(target_bid_type=BulkAdGroupLocationTargetBid)
        ),
        'Campaign Location Target': _EntityInfo(
            lambda: BulkCampaignLocationTargetBid(),
            _StringTable.Target,
            lambda: _BulkCampaignTargetIdentifier(target_bid_type=BulkCampaignLocationTargetBid)
        ),
        'Ad Group Negative Location Target': _EntityInfo(
            lambda: BulkAdGroupNegativeLocationTargetBid(),
            _StringTable.Target,
            lambda: _BulkAdGroupTargetIdentifier(target_bid_type=BulkAdGroupNegativeLocationTargetBid)
        ),
        'Campaign Negative Location Target': _EntityInfo(
            lambda: BulkCampaignNegativeLocationTargetBid(),
            _StringTable.Target,
            lambda: _BulkCampaignTargetIdentifier(target_bid_type=BulkCampaignNegativeLocationTargetBid)
        ),
        'Ad Group Radius Target': _EntityInfo(
            lambda: BulkAdGroupRadiusTargetBid(),
            _StringTable.Target,
            lambda: _BulkAdGroupTargetIdentifier(target_bid_type=BulkAdGroupRadiusTargetBid)
        ),
        'Campaign Radius Target': _EntityInfo(
            lambda: BulkCampaignRadiusTargetBid(),
            _StringTable.Target,
            lambda: _BulkCampaignTargetIdentifier(target_bid_type=BulkCampaignRadiusTargetBid)
        ),
    }

    ADDITIONAL_OBJECT_MAP = {
        'Format Version': lambda: _FormatVersion(),
        'Keyword Best Position Bid': lambda: BulkKeywordBestPositionBid(),
        'Keyword Main Line Bid': lambda: BulkKeywordMainLineBid(),
        'Keyword First Page Bid': lambda: BulkKeywordFirstPageBid(),
    }

    TYPE_REVERSE_MAP = {}
    TARGET_IDENTIFIER_TYPE_REVERSE_MAP = {}

    @staticmethod
    def create_bulk_object(row_values):
        type_column = row_values[_StringTable.Type]

        if type_column.endswith('Error'):
            return BulkError()
        elif type_column in _BulkObjectFactory.ADDITIONAL_OBJECT_MAP:
            return _BulkObjectFactory.ADDITIONAL_OBJECT_MAP[type_column]()
        elif type_column in _BulkObjectFactory.INDIVIDUAL_ENTITY_MAP:
            info = _BulkObjectFactory.INDIVIDUAL_ENTITY_MAP[type_column]
            if row_values[_StringTable.Status] == 'Deleted' \
                    and info.delete_all_column_name \
                    and not row_values[info.delete_all_column_name]:
                return info.create_identifier_func()
            return info.create_func()
        else:
            return UnknownBulkEntity()

    @staticmethod
    def get_bulk_row_type(bulk_object):
        if isinstance(bulk_object, BulkError):
            return '{0} Error'.format(_BulkObjectFactory.get_bulk_row_type(bulk_object.entity))
        if isinstance(bulk_object, _BulkTargetIdentifier):
            return _BulkObjectFactory.TARGET_IDENTIFIER_TYPE_REVERSE_MAP[type(bulk_object)][bulk_object.target_bid_type]
        return _BulkObjectFactory.TYPE_REVERSE_MAP[type(bulk_object)]


for (k, v) in _BulkObjectFactory.INDIVIDUAL_ENTITY_MAP.items():
    _BulkObjectFactory.TYPE_REVERSE_MAP[type(v.create_func())] = k

    if v.create_identifier_func is not None:
        identifier = v.create_identifier_func()
        if isinstance(identifier, _BulkTargetIdentifier):
            if not type(identifier) in _BulkObjectFactory.TARGET_IDENTIFIER_TYPE_REVERSE_MAP:
                _BulkObjectFactory.TARGET_IDENTIFIER_TYPE_REVERSE_MAP[type(identifier)] = {}
            _BulkObjectFactory.TARGET_IDENTIFIER_TYPE_REVERSE_MAP[type(identifier)][identifier.target_bid_type] = k
        else:
            _BulkObjectFactory.TYPE_REVERSE_MAP[type(identifier)] = k
