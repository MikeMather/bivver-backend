from rest_framework import serializers
from .models import *
from utils.utils import process_image


class ItemSerializer(serializers.ModelSerializer):
    base64_image = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Item
        fields = '__all__'
    
    def create(self, validated_data):
        supplier = None
        item = Item()
        if 'request' in self.context:
            # Only suppliers can make items
            user = self.context['request'].user
            supplier = user.supplier

        item.supplier = supplier
        item.measure = 'millilitre'
        item.order_by = validated_data['order_by']
        item.quantity_per_order = validated_data.get('quantity_per_order', 1)
        item.amount_per_unit = validated_data['amount_per_unit']

        if validated_data['order_by'] == 'Keg':
            item.amount_per_unit = validated_data['amount_per_unit'] * 1000 # Convert from litres to mL
        
        item.name = validated_data['name']
        item.description = validated_data.get('description', '')
        item.stock_quantity = 0
        item.price = validated_data['price']
        item.sku = validated_data['sku']
        item.style = validated_data.get('style', '')
        item.tasting_notes = validated_data.get('tasting_notes', '')
        item.alcohol_percentage = validated_data['alcohol_percentage']

        base64_image_string = validated_data.get('base64_image', None)
        if base64_image_string:
            item.image = process_image(base64_image_string, 'items')
        
        item.save()
        return item

    def update(self, item, validated_data):

        item.order_by = validated_data['order_by']
        item.quantity_per_order = validated_data.get('quantity_per_order', 1)
        item.amount_per_unit = validated_data['amount_per_unit']
        item.name = validated_data['name']
        item.description = validated_data.get('description', '')
        item.price = validated_data['price']
        item.sku = validated_data['sku']
        item.style = validated_data.get('style', '')
        item.tasting_notes = validated_data.get('tasting_notes', '')
        item.alcohol_percentage = validated_data['alcohol_percentage']
        item.stock_quantity = validated_data['stock_quantity']
        item.disabled = validated_data['disabled']

        base64_image_string = validated_data.get('base64_image', None)
        if base64_image_string:
            item.image = process_image(base64_image_string, 'items', delete_key=item.image)
        
        item.save()
        return item