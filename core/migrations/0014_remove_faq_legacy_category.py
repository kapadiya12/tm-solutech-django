from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0013_seed_faq_categories_and_questions'),
    ]

    operations = [
        migrations.RemoveField('faq', 'legacy_category'),
    ]
