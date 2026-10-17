from django.db import migrations


LIFE_CONTENT = """
<h2>Life at TM Solutech</h2>
<p>Since 1985 we have grown by growing our people. Our team of engineers, consultants and specialists works side by side to build technology around our clients&rsquo; businesses.</p>
<h3>Our culture</h3>
<ul>
<li><strong>Learning every day</strong> &mdash; hands-on work with enterprise platforms, certifications and modern cloud technologies.</li>
<li><strong>One team</strong> &mdash; a collaborative, customer-centric workplace where everyone&rsquo;s ideas count.</li>
<li><strong>Celebrating together</strong> &mdash; team outings, festivals and milestones we mark as a family.</li>
</ul>
<h3>Want to be part of it?</h3>
<p>See our open roles on the <a href="/careers/">Careers</a> page.</p>
"""


def seed(apps, schema_editor):
    Page = apps.get_model('cms', 'Page')
    Page.objects.get_or_create(
        slug='life-at-tm-solutech',
        defaults={
            'title': 'Life at TM Solutech',
            'content': LIFE_CONTENT.strip(),
            'meta_description': 'Discover the culture, people and everyday life at TM Solutech.',
            'is_published': True,
        },
    )


def unseed(apps, schema_editor):
    # No-op: the page may have been edited in the dashboard since this ran.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0002_seed_careers_page'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
