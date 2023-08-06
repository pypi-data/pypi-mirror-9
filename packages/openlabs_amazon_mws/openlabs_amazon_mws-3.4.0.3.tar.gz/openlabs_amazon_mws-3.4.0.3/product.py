# -*- coding: UTF-8 -*-
'''
    product

    :copyright: (c) 2013-2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
'''
from decimal import Decimal
from lxml import etree
from lxml.builder import E

from trytond.model import ModelView, fields
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pool import PoolMeta, Pool


__all__ = [
    'Product', 'ExportCatalogStart', 'ExportCatalog',
    'ExportCatalogDone', 'ExportCatalogPricingStart', 'ExportCatalogPricing',
    'ExportCatalogPricingDone', 'ExportCatalogInventoryStart',
    'ExportCatalogInventory', 'ExportCatalogInventoryDone', 'ProductCode',
    'Template',
]
__metaclass__ = PoolMeta


class Template:
    "Product Template"
    __name__ = 'product.template'

    export_to_amazon = fields.Boolean('Amazon Exportable')


class Product:
    "Product"
    __name__ = "product.product"

    asin = fields.Function(fields.Many2One(
        'product.product.code', 'ASIN'
    ), 'get_codes')
    ean = fields.Function(fields.Many2One(
        'product.product.code', 'EAN'
    ), 'get_codes')
    upc = fields.Function(fields.Many2One(
        'product.product.code', 'UPC'
    ), 'get_codes')
    isbn = fields.Function(fields.Many2One(
        'product.product.code', 'ISBN'
    ), 'get_codes')
    gtin = fields.Function(fields.Many2One(
        'product.product.code', 'GTIN'
    ), 'get_codes')

    @classmethod
    def __setup__(cls):
        """
        Setup the class before adding to pool
        """
        super(Product, cls).__setup__()
        cls._error_messages.update({
            "missing_product_codes": (
                'Product "%(product)s" misses Amazon Product Identifiers'
            ),
            "missing_product_code": (
                'Product "%(product)s" misses Product Code'
            )
        })

    @classmethod
    def get_codes(cls, products, names):
        ProductCode = Pool().get('product.product.code')

        res = {}
        for name in names:
            res[name] = {}
            for product in products:
                code = ProductCode.search([
                    ('product', '=', product.id),
                    ('code_type', '=', name)
                ])
                res[name][product.id] = code and code[0].id or None

        return res

    @classmethod
    def find_or_create_using_amazon_sku(cls, sku):
        """
        Find or create a product using Amazon Seller SKU. This method looks
        for an existing product using the SKU provided. If found, it
        returns the product found, else creates a new one and returns that

        :param sku: Product Seller SKU from Amazon
        :returns: Active record of Product Created
        """
        SaleChannel = Pool().get('sale.channel')

        products = cls.search([('code', '=', sku)])

        if products:
            return products[0]

        # if product is not found get the info from amazon and
        # delegate to create_using_amazon_data
        amazon_channel = SaleChannel(
            Transaction().context['amazon_channel']
        )
        api = amazon_channel.get_amazon_product_api()

        product_data = api.get_matching_product_for_id(
            amazon_channel.marketplace_id, 'SellerSKU', [sku]
        ).parsed

        return cls.create_using_amazon_data(product_data)

    @classmethod
    def extract_product_values_from_amazon_data(cls, product_attributes):
        """
        Extract product values from the amazon data, used for
        creation of product. This method can be overwritten by
        custom modules to store extra info to a product

        :param product_data: Product data from amazon
        :returns: Dictionary of values
        """
        SaleChannel = Pool().get('sale.channel')

        amazon_channel = SaleChannel(
            Transaction().context['amazon_channel']
        )

        return {
            'name': product_attributes['Title']['value'],
            'list_price': Decimal('0.01'),
            'cost_price': Decimal('0.01'),
            'default_uom': amazon_channel.default_uom.id,
            'salable': True,
            'sale_uom': amazon_channel.default_uom.id,
            'account_expense': amazon_channel.default_account_expense.id,
            'account_revenue': amazon_channel.default_account_revenue.id,
        }

    @classmethod
    def create_using_amazon_data(cls, product_data):
        """
        Create a new product with the `product_data` from amazon.

        :param product_data: Product Data from Amazon
        :returns: Active record of product created
        """
        Template = Pool().get('product.template')

        # TODO: Handle attribute sets in multiple languages
        product_attribute_set = product_data['Products']['Product'][
            'AttributeSets'
        ]
        if isinstance(product_attribute_set, dict):
            product_attributes = product_attribute_set['ItemAttributes']
        else:
            product_attributes = product_attribute_set[0]['ItemAttributes']

        product_values = cls.extract_product_values_from_amazon_data(
            product_attributes
        )

        product_values.update({
            'products': [('create', [{
                'code': product_data['Id']['value'],
                'description': product_attributes['Title']['value'],
                'channel_listings': [('create', [{
                    'channel': Transaction().context['amazon_channel']
                }])]
            }])],
        })

        product_template, = Template.create([product_values])

        return product_template.products[0]

    @classmethod
    def export_to_amazon(cls, products):
        """Export the products to the Amazon account in context

        :param products: List of active records of products
        """
        SaleChannel = Pool().get('sale.channel')

        amazon_channel = SaleChannel(
            Transaction().context['amazon_channel']
        )

        NS = "http://www.w3.org/2001/XMLSchema-instance"
        location_attribute = '{%s}noNamespaceSchemaLocation' % NS

        products_xml = []
        for product in products:
            if not product.code:
                cls.raise_user_error(
                    'missing_product_code', {
                        'product': product.template.name
                    }
                )
            if not product.codes:
                cls.raise_user_error(
                    'missing_product_codes', {
                        'product': product.template.name
                    }
                )
            # Get the product's code to be set as standard ID to amazon
            product_standard_id = (
                product.asin or product.ean or product.upc or product.isbn
                or product.gtin
            )
            products_xml.append(E.Message(
                E.MessageID(str(product.id)),
                E.OperationType('Update'),
                E.Product(
                    E.SKU(product.code),
                    E.StandardProductID(
                        E.Type(product_standard_id.code_type.upper()),
                        E.Value(product_standard_id.code),
                    ),
                    E.DescriptionData(
                        E.Title(product.template.name),
                        E.Description(product.description),
                    ),
                    # Amazon needs this information so as to place the product
                    # under a category.
                    # FIXME: Either we need to create all that inside our
                    # system or figure out a way to get all that via API
                    E.ProductData(
                        E.Miscellaneous(
                            E.ProductType('Misc_Other'),
                        ),
                    ),
                )
            ))

        envelope_xml = E.AmazonEnvelope(
            E.Header(
                E.DocumentVersion('1.01'),
                E.MerchantIdentifier(amazon_channel.merchant_id)
            ),
            E.MessageType('Product'),
            E.PurgeAndReplace('false'),
            *(product_xml for product_xml in products_xml)
        )

        envelope_xml.set(location_attribute, 'amznenvelope.xsd')

        feeds_api = amazon_channel.get_amazon_feed_api()

        response = feeds_api.submit_feed(
            etree.tostring(envelope_xml),
            feed_type='_POST_PRODUCT_DATA_',
            marketplaceids=[amazon_channel.marketplace_id]
        )

        cls.write(products, {
            'channel_listings': [('create', [{
                'product': product.id,
                'channel': amazon_channel.id,
            } for product in products])]
        })

        return response.parsed

    @classmethod
    def export_pricing_to_amazon(cls, products):
        """Export prices of the products to the Amazon account in context

        :param products: List of active records of products
        """
        SaleChannel = Pool().get('sale.channel')

        amazon_channel = SaleChannel(
            Transaction().context['amazon_channel']
        )

        NS = "http://www.w3.org/2001/XMLSchema-instance"
        location_attribute = '{%s}noNamespaceSchemaLocation' % NS

        pricing_xml = []
        for product in products:

            if amazon_channel in [
                ch.channel for ch in product.channel_listings
            ]:
                pricing_xml.append(E.Message(
                    E.MessageID(str(product.id)),
                    E.OperationType('Update'),
                    E.Price(
                        E.SKU(product.code),
                        E.StandardPrice(
                            # TODO: Use a pricelist
                            str(product.template.list_price),
                            currency=amazon_channel.company.currency.code
                        ),
                    )
                ))

        envelope_xml = E.AmazonEnvelope(
            E.Header(
                E.DocumentVersion('1.01'),
                E.MerchantIdentifier(amazon_channel.merchant_id)
            ),
            E.MessageType('Price'),
            E.PurgeAndReplace('false'),
            *(price_xml for price_xml in pricing_xml)
        )

        envelope_xml.set(location_attribute, 'amznenvelope.xsd')

        feeds_api = amazon_channel.get_amazon_feed_api()

        response = feeds_api.submit_feed(
            etree.tostring(envelope_xml),
            feed_type='_POST_PRODUCT_PRICING_DATA_',
            marketplaceids=[amazon_channel.marketplace_id]
        )

        return response.parsed

    @classmethod
    def export_inventory_to_amazon(cls, products):
        """Export inventory of the products to the Amazon account in context

        :param products: List of active records of products
        """
        SaleChannel = Pool().get('sale.channel')

        amazon_channel = SaleChannel(
            Transaction().context['amazon_channel']
        )

        NS = "http://www.w3.org/2001/XMLSchema-instance"
        location_attribute = '{%s}noNamespaceSchemaLocation' % NS

        inventory_xml = []
        for product in products:

            with Transaction().set_context({
                'locations': [amazon_channel.warehouse.id]
            }):
                quantity = product.quantity

            if not quantity:
                continue

            if amazon_channel in [
                ch.channel for ch in product.channel_listings
            ]:
                inventory_xml.append(E.Message(
                    E.MessageID(str(product.id)),
                    E.OperationType('Update'),
                    E.Inventory(
                        E.SKU(product.code),
                        E.Quantity(str(round(quantity))),
                        E.FulfillmentLatency(
                            str(product.template.delivery_time)
                        ),
                    )
                ))

        envelope_xml = E.AmazonEnvelope(
            E.Header(
                E.DocumentVersion('1.01'),
                E.MerchantIdentifier(amazon_channel.merchant_id)
            ),
            E.MessageType('Inventory'),
            E.PurgeAndReplace('false'),
            *(inv_xml for inv_xml in inventory_xml)
        )

        envelope_xml.set(location_attribute, 'amznenvelope.xsd')

        feeds_api = amazon_channel.get_amazon_feed_api()

        response = feeds_api.submit_feed(
            etree.tostring(envelope_xml),
            feed_type='_POST_INVENTORY_AVAILABILITY_DATA_',
            marketplaceids=[amazon_channel.marketplace_id]
        )

        return response.parsed


class ProductCode:
    "Amazon Product Identifier"
    __name__ = 'product.product.code'

    @classmethod
    def __setup__(cls):
        """
        Setup the class before adding to pool
        """
        super(ProductCode, cls).__setup__()
        cls.code_type.selection.extend([
            ('upc', 'UPC'),
            ('isbn', 'ISBN'),
            ('asin', 'ASIN'),
            ('gtin', 'GTIN')
        ])


class ExportCatalogStart(ModelView):
    'Export Catalog to Amazon View'
    __name__ = 'amazon.export_catalog.start'

    products = fields.Many2Many(
        'product.product', None, None, 'Products', required=True,
        domain=[
            ('codes', 'not in', []),
            ('code', '!=', None),
        ],
    )


class ExportCatalogDone(ModelView):
    'Export Catalog to Amazon Done View'
    __name__ = 'amazon.export_catalog.done'

    status = fields.Char('Status', readonly=True)
    submission_id = fields.Char('Submission ID', readonly=True)


class ExportCatalog(Wizard):
    '''Export catalog to Amazon

    Export the products selected to this amazon account
    '''
    __name__ = 'amazon.export_catalog'

    start = StateView(
        'amazon.export_catalog.start',
        'amazon_mws.export_catalog_start', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Continue', 'export_', 'tryton-ok', default=True),
        ]
    )
    export_ = StateTransition()
    done = StateView(
        'amazon.export_catalog.done',
        'amazon_mws.export_catalog_done', [
            Button('OK', 'end', 'tryton-cancel'),
        ]
    )

    def transition_export_(self):
        """
        Export the products selected to this amazon account
        """
        Product = Pool().get('product.product')
        SaleChannel = Pool().get('sale.channel')

        amazon_channel = SaleChannel(Transaction().context.get('active_id'))

        if not self.start.products:
            return 'end'

        with Transaction().set_context(amazon_channel=amazon_channel.id):
            response = Product.export_to_amazon(self.start.products)

        Transaction().set_context({'response': response})

        return 'done'

    def default_done(self, fields):
        "Display response"
        response = Transaction().context['response']
        return {
            'status': response['FeedSubmissionInfo'][
                'FeedProcessingStatus'
            ]['value'],
            'submission_id': response['FeedSubmissionInfo'][
                'FeedSubmissionId'
            ]['value']
        }


class ExportCatalogPricingStart(ModelView):
    'Export Catalog Pricing to Amazon View'
    __name__ = 'amazon.export_catalog_pricing.start'

    products = fields.Many2Many(
        'product.product', None, None, 'Products', required=True,
        domain=[
            ('codes', 'not in', []),
            ('code', '!=', None),
            ('channel_listings', 'not in', []),
        ],
    )


class ExportCatalogPricingDone(ModelView):
    'Export Catalog Pricing to Amazon Done View'
    __name__ = 'amazon.export_catalog_pricing.done'

    status = fields.Char('Status', readonly=True)
    submission_id = fields.Char('Submission ID', readonly=True)


class ExportCatalogPricing(Wizard):
    '''Export catalog pricing to Amazon

    Export the prices products selected to this amazon account
    '''
    __name__ = 'amazon.export_catalog_pricing'

    start = StateView(
        'amazon.export_catalog_pricing.start',
        'amazon_mws.export_catalog_pricing_start', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Continue', 'export_', 'tryton-ok', default=True),
        ]
    )
    export_ = StateTransition()
    done = StateView(
        'amazon.export_catalog_pricing.done',
        'amazon_mws.export_catalog_pricing_done', [
            Button('OK', 'end', 'tryton-cancel'),
        ]
    )

    def transition_export_(self):
        """
        Export the prices for products selected to this amazon account
        """
        Product = Pool().get('product.product')
        SaleChannel = Pool().get('sale.channel')

        amazon_channel = SaleChannel(Transaction().context.get('active_id'))

        if not self.start.products:
            return 'end'

        with Transaction().set_context(amazon_channel=amazon_channel.id):

            response = Product.export_pricing_to_amazon(self.start.products)

        Transaction().set_context({'response': response})

        return 'done'

    def default_done(self, fields):
        "Display response"
        response = Transaction().context['response']
        return {
            'status': response['FeedSubmissionInfo'][
                'FeedProcessingStatus'
            ]['value'],
            'submission_id': response['FeedSubmissionInfo'][
                'FeedSubmissionId'
            ]['value']
        }


class ExportCatalogInventoryStart(ModelView):
    'Export Catalog Inventory to Amazon View'
    __name__ = 'amazon.export_catalog_inventory.start'

    products = fields.Many2Many(
        'product.product', None, None, 'Products', required=True,
        domain=[
            ('codes', 'not in', []),
            ('code', '!=', None),
            ('channel_listings', 'not in', []),
        ],
    )


class ExportCatalogInventoryDone(ModelView):
    'Export Catalog Inventory to Amazon Done View'
    __name__ = 'amazon.export_catalog_inventory.done'

    status = fields.Char('Status', readonly=True)
    submission_id = fields.Char('Submission ID', readonly=True)


class ExportCatalogInventory(Wizard):
    '''Export catalog inventory to Amazon

    Export the prices products selected to this amazon account
    '''
    __name__ = 'amazon.export_catalog_inventory'

    start = StateView(
        'amazon.export_catalog_inventory.start',
        'amazon_mws.export_catalog_inventory_start', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Continue', 'export_', 'tryton-ok', default=True),
        ]
    )
    export_ = StateTransition()
    done = StateView(
        'amazon.export_catalog_inventory.done',
        'amazon_mws.export_catalog_inventory_done', [
            Button('OK', 'end', 'tryton-cancel'),
        ]
    )

    def transition_export_(self):
        """
        Export the prices for products selected to this amazon account
        """
        Product = Pool().get('product.product')
        SaleChannel = Pool().get('sale.channel')

        amazon_channel = SaleChannel(Transaction().context.get('active_id'))

        if not self.start.products:
            return 'end'

        with Transaction().set_context(amazon_channel=amazon_channel.id):
            response = Product.export_inventory_to_amazon(self.start.products)

        Transaction().set_context({'response': response})

        return 'done'

    def default_done(self, fields):
        "Display response"
        response = Transaction().context['response']
        return {
            'status': response['FeedSubmissionInfo'][
                'FeedProcessingStatus'
            ]['value'],
            'submission_id': response['FeedSubmissionInfo'][
                'FeedSubmissionId'
            ]['value']
        }
