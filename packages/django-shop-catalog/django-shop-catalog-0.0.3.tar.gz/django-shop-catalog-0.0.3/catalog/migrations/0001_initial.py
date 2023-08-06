# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ModifierTranslation'
        db.create_table(u'catalog_modifiers_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['catalog.Modifier'])),
        ))
        db.send_create_signal(u'catalog', ['ModifierTranslation'])

        # Adding unique constraint on 'ModifierTranslation', fields ['language_code', 'master']
        db.create_unique(u'catalog_modifiers_translation', ['language_code', 'master_id'])

        # Adding model 'Modifier'
        db.create_table(u'catalog_modifiers', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=128)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default='0.0', max_digits=30, decimal_places=2)),
            ('percent', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=2, blank=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(default=u'standard', max_length=128)),
        ))
        db.send_create_signal(u'catalog', ['Modifier'])

        # Adding model 'ModifierCondition'
        db.create_table(u'catalog_modifier_conditions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modifier', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'conditions', to=orm['catalog.Modifier'])),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('arg', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=3, blank=True)),
        ))
        db.send_create_signal(u'catalog', ['ModifierCondition'])

        # Adding model 'ModifierCode'
        db.create_table(u'catalog_modifier_codes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modifier', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'codes', to=orm['catalog.Modifier'])),
            ('code', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=30)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('valid_from', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('valid_until', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('num_uses', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('max_uses', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'catalog', ['ModifierCode'])

        # Adding model 'CartModifierCode'
        db.create_table(u'catalog_cart_modifier_codes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Cart'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('can_be_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'catalog', ['CartModifierCode'])

        # Adding model 'CategoryTranslation'
        db.create_table(u'catalog_categories_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=128)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['catalog.Category'])),
        ))
        db.send_create_signal(u'catalog', ['CategoryTranslation'])

        # Adding unique constraint on 'CategoryTranslation', fields ['slug', 'language_code']
        db.create_unique(u'catalog_categories_translation', ['slug', 'language_code'])

        # Adding unique constraint on 'CategoryTranslation', fields ['language_code', 'master']
        db.create_unique(u'catalog_categories_translation', ['language_code', 'master_id'])

        # Adding model 'Category'
        db.create_table(u'catalog_categories', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'children', null=True, to=orm['catalog.Category'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'catalog', ['Category'])

        # Adding M2M table for field modifiers on 'Category'
        m2m_table_name = db.shorten_name(u'catalog_categories_modifiers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm[u'catalog.category'], null=False)),
            ('modifier', models.ForeignKey(orm[u'catalog.modifier'], null=False))
        ))
        db.create_unique(m2m_table_name, ['category_id', 'modifier_id'])

        # Adding model 'BrandTranslation'
        db.create_table(u'catalog_brands_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=128)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['catalog.Brand'])),
        ))
        db.send_create_signal(u'catalog', ['BrandTranslation'])

        # Adding unique constraint on 'BrandTranslation', fields ['slug', 'language_code']
        db.create_unique(u'catalog_brands_translation', ['slug', 'language_code'])

        # Adding unique constraint on 'BrandTranslation', fields ['language_code', 'master']
        db.create_unique(u'catalog_brands_translation', ['language_code', 'master_id'])

        # Adding model 'Brand'
        db.create_table(u'catalog_brands', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'children', null=True, to=orm['catalog.Brand'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'catalog', ['Brand'])

        # Adding M2M table for field modifiers on 'Brand'
        m2m_table_name = db.shorten_name(u'catalog_brands_modifiers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('brand', models.ForeignKey(orm[u'catalog.brand'], null=False)),
            ('modifier', models.ForeignKey(orm[u'catalog.modifier'], null=False))
        ))
        db.create_unique(m2m_table_name, ['brand_id', 'modifier_id'])

        # Adding model 'ManufacturerTranslation'
        db.create_table(u'catalog_manufacturers_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=128)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['catalog.Manufacturer'])),
        ))
        db.send_create_signal(u'catalog', ['ManufacturerTranslation'])

        # Adding unique constraint on 'ManufacturerTranslation', fields ['slug', 'language_code']
        db.create_unique(u'catalog_manufacturers_translation', ['slug', 'language_code'])

        # Adding unique constraint on 'ManufacturerTranslation', fields ['language_code', 'master']
        db.create_unique(u'catalog_manufacturers_translation', ['language_code', 'master_id'])

        # Adding model 'Manufacturer'
        db.create_table(u'catalog_manufacturers', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'children', null=True, to=orm['catalog.Manufacturer'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'catalog', ['Manufacturer'])

        # Adding M2M table for field modifiers on 'Manufacturer'
        m2m_table_name = db.shorten_name(u'catalog_manufacturers_modifiers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('manufacturer', models.ForeignKey(orm[u'catalog.manufacturer'], null=False)),
            ('modifier', models.ForeignKey(orm[u'catalog.modifier'], null=False))
        ))
        db.create_unique(m2m_table_name, ['manufacturer_id', 'modifier_id'])

        # Adding model 'Tax'
        db.create_table(u'catalog_taxes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('percent', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
        ))
        db.send_create_signal(u'catalog', ['Tax'])

        # Adding model 'ProductTranslation'
        db.create_table(u'catalog_products_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=128)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['catalog.Product'])),
        ))
        db.send_create_signal(u'catalog', ['ProductTranslation'])

        # Adding unique constraint on 'ProductTranslation', fields ['slug', 'language_code']
        db.create_unique(u'catalog_products_translation', ['slug', 'language_code'])

        # Adding unique constraint on 'ProductTranslation', fields ['language_code', 'master']
        db.create_unique(u'catalog_products_translation', ['language_code', 'master_id'])

        # Adding model 'Product'
        db.create_table(u'catalog_products', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('upc', self.gf('catalog.fields.NullableCharField')(max_length=64, unique=True, null=True, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'variants', null=True, to=orm['catalog.Product'])),
            ('unit_price', self.gf('django.db.models.fields.DecimalField')(default='0.0', max_digits=30, decimal_places=2)),
            ('is_discountable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('discount_percent', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=2, blank=True)),
            ('tax', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'products', null=True, to=orm['catalog.Tax'])),
            ('quantity', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('featured_image', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'featured_images', null=True, to=orm['filer.Image'])),
            ('category', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'products', null=True, to=orm['catalog.Category'])),
            ('brand', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'products', null=True, to=orm['catalog.Brand'])),
            ('manufacturer', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'products', null=True, to=orm['catalog.Manufacturer'])),
            ('media', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'product_media_set', null=True, to=orm['cms.Placeholder'])),
            ('body', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'product_body_set', null=True, to=orm['cms.Placeholder'])),
        ))
        db.send_create_signal(u'catalog', ['Product'])

        # Adding M2M table for field modifiers on 'Product'
        m2m_table_name = db.shorten_name(u'catalog_products_modifiers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm[u'catalog.product'], null=False)),
            ('modifier', models.ForeignKey(orm[u'catalog.modifier'], null=False))
        ))
        db.create_unique(m2m_table_name, ['product_id', 'modifier_id'])

        # Adding model 'AttributeTranslation'
        db.create_table(u'catalog_attributes_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['catalog.Attribute'])),
        ))
        db.send_create_signal(u'catalog', ['AttributeTranslation'])

        # Adding unique constraint on 'AttributeTranslation', fields ['language_code', 'master']
        db.create_unique(u'catalog_attributes_translation', ['language_code', 'master_id'])

        # Adding model 'Attribute'
        db.create_table(u'catalog_attributes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=128)),
            ('kind', self.gf('django.db.models.fields.CharField')(default=u'integer', max_length=20)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'catalog', ['Attribute'])

        # Adding model 'ProductAttributeValue'
        db.create_table(u'catalog_product_attribute_values', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'values', to=orm['catalog.Attribute'])),
            ('value_integer', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('value_boolean', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('value_float', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('value_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('value_option', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalog.AttributeOption'], null=True, blank=True)),
            ('value_file', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'value_files', null=True, to=orm['filer.File'])),
            ('value_image', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'value_images', null=True, to=orm['filer.Image'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'attribute_values', to=orm['catalog.Product'])),
        ))
        db.send_create_signal(u'catalog', ['ProductAttributeValue'])

        # Adding unique constraint on 'ProductAttributeValue', fields ['attribute', 'product']
        db.create_unique(u'catalog_product_attribute_values', ['attribute_id', 'product_id'])

        # Adding model 'AttributeOptionTranslation'
        db.create_table(u'catalog_attribute_options_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['catalog.AttributeOption'])),
        ))
        db.send_create_signal(u'catalog', ['AttributeOptionTranslation'])

        # Adding unique constraint on 'AttributeOptionTranslation', fields ['language_code', 'master']
        db.create_unique(u'catalog_attribute_options_translation', ['language_code', 'master_id'])

        # Adding model 'AttributeOption'
        db.create_table(u'catalog_attribute_options', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'options', to=orm['catalog.Attribute'])),
        ))
        db.send_create_signal(u'catalog', ['AttributeOption'])

        # Adding model 'ProductMeasurement'
        db.create_table(u'catalog_product_measurements', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(default=u'width', max_length=20)),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=3)),
            ('unit', self.gf('django.db.models.fields.CharField')(default='m', max_length=20)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'measurements', to=orm['catalog.Product'])),
        ))
        db.send_create_signal(u'catalog', ['ProductMeasurement'])

        # Adding unique constraint on 'ProductMeasurement', fields ['product', 'kind']
        db.create_unique(u'catalog_product_measurements', ['product_id', 'kind'])


    def backwards(self, orm):
        # Removing unique constraint on 'ProductMeasurement', fields ['product', 'kind']
        db.delete_unique(u'catalog_product_measurements', ['product_id', 'kind'])

        # Removing unique constraint on 'AttributeOptionTranslation', fields ['language_code', 'master']
        db.delete_unique(u'catalog_attribute_options_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'ProductAttributeValue', fields ['attribute', 'product']
        db.delete_unique(u'catalog_product_attribute_values', ['attribute_id', 'product_id'])

        # Removing unique constraint on 'AttributeTranslation', fields ['language_code', 'master']
        db.delete_unique(u'catalog_attributes_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'ProductTranslation', fields ['language_code', 'master']
        db.delete_unique(u'catalog_products_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'ProductTranslation', fields ['slug', 'language_code']
        db.delete_unique(u'catalog_products_translation', ['slug', 'language_code'])

        # Removing unique constraint on 'ManufacturerTranslation', fields ['language_code', 'master']
        db.delete_unique(u'catalog_manufacturers_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'ManufacturerTranslation', fields ['slug', 'language_code']
        db.delete_unique(u'catalog_manufacturers_translation', ['slug', 'language_code'])

        # Removing unique constraint on 'BrandTranslation', fields ['language_code', 'master']
        db.delete_unique(u'catalog_brands_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'BrandTranslation', fields ['slug', 'language_code']
        db.delete_unique(u'catalog_brands_translation', ['slug', 'language_code'])

        # Removing unique constraint on 'CategoryTranslation', fields ['language_code', 'master']
        db.delete_unique(u'catalog_categories_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'CategoryTranslation', fields ['slug', 'language_code']
        db.delete_unique(u'catalog_categories_translation', ['slug', 'language_code'])

        # Removing unique constraint on 'ModifierTranslation', fields ['language_code', 'master']
        db.delete_unique(u'catalog_modifiers_translation', ['language_code', 'master_id'])

        # Deleting model 'ModifierTranslation'
        db.delete_table(u'catalog_modifiers_translation')

        # Deleting model 'Modifier'
        db.delete_table(u'catalog_modifiers')

        # Deleting model 'ModifierCondition'
        db.delete_table(u'catalog_modifier_conditions')

        # Deleting model 'ModifierCode'
        db.delete_table(u'catalog_modifier_codes')

        # Deleting model 'CartModifierCode'
        db.delete_table(u'catalog_cart_modifier_codes')

        # Deleting model 'CategoryTranslation'
        db.delete_table(u'catalog_categories_translation')

        # Deleting model 'Category'
        db.delete_table(u'catalog_categories')

        # Removing M2M table for field modifiers on 'Category'
        db.delete_table(db.shorten_name(u'catalog_categories_modifiers'))

        # Deleting model 'BrandTranslation'
        db.delete_table(u'catalog_brands_translation')

        # Deleting model 'Brand'
        db.delete_table(u'catalog_brands')

        # Removing M2M table for field modifiers on 'Brand'
        db.delete_table(db.shorten_name(u'catalog_brands_modifiers'))

        # Deleting model 'ManufacturerTranslation'
        db.delete_table(u'catalog_manufacturers_translation')

        # Deleting model 'Manufacturer'
        db.delete_table(u'catalog_manufacturers')

        # Removing M2M table for field modifiers on 'Manufacturer'
        db.delete_table(db.shorten_name(u'catalog_manufacturers_modifiers'))

        # Deleting model 'Tax'
        db.delete_table(u'catalog_taxes')

        # Deleting model 'ProductTranslation'
        db.delete_table(u'catalog_products_translation')

        # Deleting model 'Product'
        db.delete_table(u'catalog_products')

        # Removing M2M table for field modifiers on 'Product'
        db.delete_table(db.shorten_name(u'catalog_products_modifiers'))

        # Deleting model 'AttributeTranslation'
        db.delete_table(u'catalog_attributes_translation')

        # Deleting model 'Attribute'
        db.delete_table(u'catalog_attributes')

        # Deleting model 'ProductAttributeValue'
        db.delete_table(u'catalog_product_attribute_values')

        # Deleting model 'AttributeOptionTranslation'
        db.delete_table(u'catalog_attribute_options_translation')

        # Deleting model 'AttributeOption'
        db.delete_table(u'catalog_attribute_options')

        # Deleting model 'ProductMeasurement'
        db.delete_table(u'catalog_product_measurements')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'catalog.attribute': {
            'Meta': {'ordering': "(u'code',)", 'object_name': 'Attribute', 'db_table': "u'catalog_attributes'"},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "u'integer'", 'max_length': '20'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'catalog.attributeoption': {
            'Meta': {'object_name': 'AttributeOption', 'db_table': "u'catalog_attribute_options'"},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'options'", 'to': u"orm['catalog.Attribute']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'catalog.attributeoptiontranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'AttributeOptionTranslation', 'db_table': "u'catalog_attribute_options_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['catalog.AttributeOption']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'catalog.attributetranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'AttributeTranslation', 'db_table': "u'catalog_attributes_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['catalog.Attribute']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'catalog.brand': {
            'Meta': {'object_name': 'Brand', 'db_table': "u'catalog_brands'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modifiers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalog.Modifier']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['catalog.Brand']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalog.brandtranslation': {
            'Meta': {'unique_together': "[(u'slug', u'language_code'), ('language_code', 'master')]", 'object_name': 'BrandTranslation', 'db_table': "u'catalog_brands_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['catalog.Brand']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '128'})
        },
        u'catalog.cartmodifiercode': {
            'Meta': {'object_name': 'CartModifierCode', 'db_table': "u'catalog_cart_modifier_codes'"},
            'can_be_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Cart']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'catalog.category': {
            'Meta': {'object_name': 'Category', 'db_table': "u'catalog_categories'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modifiers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalog.Modifier']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['catalog.Category']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalog.categorytranslation': {
            'Meta': {'unique_together': "[(u'slug', u'language_code'), ('language_code', 'master')]", 'object_name': 'CategoryTranslation', 'db_table': "u'catalog_categories_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['catalog.Category']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '128'})
        },
        u'catalog.manufacturer': {
            'Meta': {'object_name': 'Manufacturer', 'db_table': "u'catalog_manufacturers'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modifiers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalog.Modifier']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['catalog.Manufacturer']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'catalog.manufacturertranslation': {
            'Meta': {'unique_together': "[(u'slug', u'language_code'), ('language_code', 'master')]", 'object_name': 'ManufacturerTranslation', 'db_table': "u'catalog_manufacturers_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['catalog.Manufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '128'})
        },
        u'catalog.modifier': {
            'Meta': {'object_name': 'Modifier', 'db_table': "u'catalog_modifiers'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '30', 'decimal_places': '2'}),
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "u'standard'", 'max_length': '128'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'})
        },
        u'catalog.modifiercode': {
            'Meta': {'object_name': 'ModifierCode', 'db_table': "u'catalog_modifier_codes'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_uses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'codes'", 'to': u"orm['catalog.Modifier']"}),
            'num_uses': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'valid_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'valid_until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'catalog.modifiercondition': {
            'Meta': {'object_name': 'ModifierCondition', 'db_table': "u'catalog_modifier_conditions'"},
            'arg': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '3', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'conditions'", 'to': u"orm['catalog.Modifier']"}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'catalog.modifiertranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'ModifierTranslation', 'db_table': "u'catalog_modifiers_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['catalog.Modifier']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'catalog.product': {
            'Meta': {'object_name': 'Product', 'db_table': "u'catalog_products'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'attributes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'attributes'", 'symmetrical': 'False', 'through': u"orm['catalog.ProductAttributeValue']", 'to': u"orm['catalog.Attribute']"}),
            'body': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'product_body_set'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'brand': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'products'", 'null': 'True', 'to': u"orm['catalog.Brand']"}),
            'category': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'products'", 'null': 'True', 'to': u"orm['catalog.Category']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'discount_percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'featured_image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'featured_images'", 'null': 'True', 'to': "orm['filer.Image']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_discountable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'manufacturer': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'products'", 'null': 'True', 'to': u"orm['catalog.Manufacturer']"}),
            'media': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'product_media_set'", 'null': 'True', 'to': "orm['cms.Placeholder']"}),
            'modifiers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['catalog.Modifier']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'variants'", 'null': 'True', 'to': u"orm['catalog.Product']"}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'products'", 'null': 'True', 'to': u"orm['catalog.Tax']"}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '30', 'decimal_places': '2'}),
            'upc': ('catalog.fields.NullableCharField', [], {'max_length': '64', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'catalog.productattributevalue': {
            'Meta': {'unique_together': "((u'attribute', u'product'),)", 'object_name': 'ProductAttributeValue', 'db_table': "u'catalog_product_attribute_values'"},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'values'", 'to': u"orm['catalog.Attribute']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'attribute_values'", 'to': u"orm['catalog.Product']"}),
            'value_boolean': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'value_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'value_file': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'value_files'", 'null': 'True', 'to': "orm['filer.File']"}),
            'value_float': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'value_image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'value_images'", 'null': 'True', 'to': "orm['filer.Image']"}),
            'value_integer': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'value_option': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catalog.AttributeOption']", 'null': 'True', 'blank': 'True'})
        },
        u'catalog.productmeasurement': {
            'Meta': {'unique_together': "((u'product', u'kind'),)", 'object_name': 'ProductMeasurement', 'db_table': "u'catalog_product_measurements'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "u'width'", 'max_length': '20'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'measurements'", 'to': u"orm['catalog.Product']"}),
            'unit': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '20'}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '3'})
        },
        u'catalog.producttranslation': {
            'Meta': {'unique_together': "[(u'slug', u'language_code'), ('language_code', 'master')]", 'object_name': 'ProductTranslation', 'db_table': "u'catalog_products_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['catalog.Product']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '128'})
        },
        u'catalog.tax': {
            'Meta': {'object_name': 'Tax', 'db_table': "u'catalog_taxes'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'filer.file': {
            'Meta': {'object_name': 'File'},
            '_file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_files'", 'null': 'True', 'to': "orm['filer.Folder']"}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_files'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_filer.file_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'sha1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.folder': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('parent', 'name'),)", 'object_name': 'Folder'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filer_owned_folders'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['filer.Folder']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.image': {
            'Meta': {'object_name': 'Image', '_ormbases': ['filer.File']},
            '_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            '_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_alt_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'default_caption': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['filer.File']", 'unique': 'True', 'primary_key': 'True'}),
            'must_always_publish_author_credit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'must_always_publish_copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_location': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'shop.cart': {
            'Meta': {'object_name': 'Cart'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['catalog']