# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from random import randint

from factory import (
    lazy_attribute,
    Sequence,
    SubFactory,
    fuzzy,
)
from factory.django import DjangoModelFactory as Factory
from ralph.account.models import Region

from ralph_assets import models_assets
from ralph_assets import models_support
from ralph_assets.tests.utils import assets as assets_utils


class SupportTypeFactory(Factory):
    FACTORY_FOR = models_support.SupportType

    name = Sequence(lambda n: 'Support type #{}'.format(n))


class SupportFactory(Factory):
    FACTORY_FOR = models_support.Support

    additional_notes = Sequence(lambda n: 'additional-notes-#{}'.format(n))
    contract_id = Sequence(lambda n: '{}'.format(n))
    contract_terms = Sequence(lambda n: 'contract-terms-#{}'.format(n))
    date_from = fuzzy.FuzzyDate(datetime.date(2008, 1, 1))
    date_to = fuzzy.FuzzyDate(datetime.date(2008, 1, 1))
    description = Sequence(lambda n: 'description-#{}'.format(n))
    escalation_path = Sequence(lambda n: 'escalation-path-#{}'.format(n))
    invoice_date = fuzzy.FuzzyDate(datetime.date(2008, 1, 1))
    invoice_no = Sequence(lambda n: 'invoice-no-#{}'.format(n))
    name = Sequence(lambda n: 'name-#{}'.format(n))
    period_in_months = randint(0, 150)
    price = fuzzy.FuzzyDecimal(0, 100)
    producer = Sequence(lambda n: 'producer-#{}'.format(n))
    property_of = assets_utils.SubFactory(assets_utils.AssetOwnerFactory)
    serial_no = Sequence(lambda n: 'serial-no-#{}'.format(n))
    sla_type = Sequence(lambda n: 'sla-type-#{}'.format(n))
    status = models_support.SupportStatus.new.id
    supplier = Sequence(lambda n: 'supplier-#{}'.format(n))
    support_type = SubFactory(SupportTypeFactory)

    @lazy_attribute
    def region(self):
        # lazy attr because static fails (it's not accessible during import)
        return Region.get_default_region()


class DCSupportFactory(SupportFactory):
    asset_type = models_assets.AssetType.data_center


class BOSupportFactory(SupportFactory):
    asset_type = models_assets.AssetType.back_office
