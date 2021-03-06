# Generated by Django 2.2.5 on 2019-09-28 17:37

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=32, validators=[django.core.validators.MinValueValidator(0)])),
            ],
            options={
                'db_table': 'line_items',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_verification_token', models.CharField(blank=True, max_length=100)),
                ('payment_due_date', models.DateField(blank=True, default=None, null=True)),
                ('state', django_fsm.FSMField(default='draft', max_length=50)),
                ('delivered_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('submitted_at', models.DateTimeField(default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pdf_key', models.CharField(blank=True, max_length=300, null=True)),
                ('keg_returns', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('signature_key', models.CharField(blank=True, max_length=1500, null=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='client.Client')),
            ],
            options={
                'db_table': 'orders',
                'ordering': ('-submitted_at',),
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('payment_type', models.CharField(blank=True, max_length=300, null=True)),
                ('charge_id', models.CharField(blank=True, max_length=500, null=True)),
                ('captured', models.BooleanField(default=False)),
                ('deferred', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'payments',
            },
        ),
        migrations.CreateModel(
            name='OrderActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(blank=True, default='', max_length=150)),
                ('message', models.CharField(blank=True, default='', max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_activities', to='client.Client')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='order.Order')),
            ],
            options={
                'verbose_name_plural': 'Order Activities',
                'db_table': 'order_activities',
                'ordering': ('created_at',),
            },
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order', to='order.Payment'),
        ),
    ]
