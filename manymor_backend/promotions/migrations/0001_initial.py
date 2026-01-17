# Generated migration file for promotions app
# Run: python manage.py makemigrations promotions
# Then: python manage.py migrate

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarouselPromotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(upload_to='promotions/carousel/')),
                ('link_url', models.URLField(blank=True, help_text='Optional link when banner is clicked', null=True)),
                ('button_text', models.CharField(blank=True, help_text='Text for CTA button', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Lower numbers appear first in carousel')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Carousel Promotion',
                'verbose_name_plural': 'Carousel Promotions',
                'ordering': ['display_order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductPromotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], default='percentage', max_length=20)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('badge_text', models.CharField(blank=True, help_text="Text to display on product badge (e.g., 'SALE', '20% OFF')", max_length=50)),
                ('badge_color', models.CharField(default='#FF0000', help_text='Hex color code for badge background', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('products', models.ManyToManyField(blank=True, related_name='promotions', to='products.product')),
            ],
            options={
                'verbose_name': 'Product Promotion',
                'verbose_name_plural': 'Product Promotions',
                'ordering': ['-created_at'],
            },
        ),
    ]
