#!/usr/bin/python
# -*- coding: utf-8 -*-
import warnings
from django.conf import settings
from django.views.generic.base import TemplateView
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

import urllib2
from urlparse import urlparse
import datetime
from decimal import Decimal
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from oscar.apps.catalogue.models import (Product, Category, ProductAttribute,
                                         ProductClass, ProductCategory, ProductImage,
                                         ProductAttributeValue)

from django.http import HttpResponseRedirect

import urllib
import json


class ImportView(TemplateView):

    def dispatch(self, *args, **kwargs):
        partner = Partner.objects.filter(name='opt.my')
        if partner.exists():
            partner = partner[0]
        else:
            partner = Partner()
            partner.name = 'opt.my'
            partner.save()

        url = "http://path/?format=json"
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        # set category
        for item in data:
            if item['parent'] != "null":
                category = Category(
                    id=item['id'], path=str(item['id']), name=item['name'], depth=1)
                category.save()

        url = "http://path/?format=json"
        response = urllib.urlopen(url)
        data = json.loads(response.read())

        # set class
        class_attr = ProductClass(id=1, name="product", slug="product")
        class_attr.save()

        # set products
        for item in data:
            product_category = ProductCategory(product_id=item['id'],
                                               category_id=item['category_id'])
            product_category.save()

            product = Product(id=item['id'],
                              upc=item['id'],
                              title=item['name'],
                              slug=str(item['id']),
                              product_class_id=1,
                              date_created=datetime.datetime.today(),
                              description=item['description'])
            product.save()

            # set attribute
            attribute_weight = ProductAttribute.objects.filter(name='height')
            if attribute_weight.exists():
                attribute_weight = attribute_weight[0]
            else:
                attribute_weight = ProductAttribute()
                attribute_weight.name = 'height'
                attribute_weight.save()

            weight_attr = ProductAttributeValue()
            weight_attr.product = product
            weight_attr.attribute = attribute_weight
            weight_attr.value_text = str(item['height'])
            weight_attr.save()

            attribute_depth = ProductAttribute.objects.filter(name='depth')
            if attribute_depth.exists():
                attribute_depth = attribute_depth[0]
            else:
                attribute_depth = ProductAttribute()
                attribute_depth.name = 'depth'
                attribute_depth.save()

            depth_attr = ProductAttributeValue()
            depth_attr.product = product
            depth_attr.attribute = attribute_depth
            depth_attr.value_text = str(item['depth'])
            depth_attr.save()

            attribute_length = ProductAttribute.objects.filter(name='length')
            if attribute_length.exists():
                attribute_length = attribute_length[0]
            else:
                attribute_length = ProductAttribute()
                attribute_length.name = 'length'
                attribute_length.save()

            length_attr = ProductAttributeValue()
            length_attr.product = product
            length_attr.attribute = attribute_length
            length_attr.value_text = str(item['length'])
            length_attr.save()

            # set image
            try:
                img_url = 'http://path/media/{0}'.format(
                    item['main_picture'])
                name = urlparse(img_url).path.split('/')[-1]
                image = ProductImage()
                image.product = product
                image.original = ''
                image.save()

                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(urllib2.urlopen(img_url).read())
                img_temp.flush()

                image.original.save(name, File(img_temp))
            except Exception, e:
                pass

            # set the price
            rec = StockRecord.objects.filter(product=product)
            if rec.exists():
                rec = rec[0]
            else:
                rec = StockRecord()
                rec.product = product
                rec.partner = partner
                rec.num_in_stock = 10
                rec.partner_sku = product.upc

            rec.product = product
            rec.partner = partner
            rec.num_in_stock = 10
            rec.partner_sku = product.upc
            rec.price_excl_tax = Decimal(str(item['dollar']))
            rec.save()

        return HttpResponseRedirect(reverse("dashboard:index"))
