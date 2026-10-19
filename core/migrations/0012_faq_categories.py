import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0011_official_social_links'),
    ]

    operations = [
        migrations.RenameField('faq', 'category', 'legacy_category'),
        migrations.CreateModel(
            name='FAQCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('slug', models.SlugField(max_length=90, unique=True)),
                ('icon', models.CharField(default='fas fa-circle-question', max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['display_order', 'name'], 'verbose_name': 'FAQ category', 'verbose_name_plural': 'FAQ categories'},
        ),
        migrations.AddField('faq', 'category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='faqs', to='core.faqcategory')),
        migrations.AddField('faq', 'is_popular', models.BooleanField(default=False)),
        migrations.AddField('faq', 'helpful_yes', models.PositiveIntegerField(default=0, editable=False)),
        migrations.AddField('faq', 'helpful_no', models.PositiveIntegerField(default=0, editable=False)),
        migrations.AddField('faq', 'updated_at', models.DateTimeField(auto_now=True, default=django.utils.timezone.now), preserve_default=False),
        migrations.AlterModelOptions('faq', options={'ordering': ['display_order', 'pk'], 'verbose_name': 'FAQ', 'verbose_name_plural': 'FAQs'}),
    ]
