from django.db import migrations


CAREERS_CONTENT = """
<h2>Build Your Career at TM Solutech</h2>
<p>For over three decades we have grown by growing our people. Join a team of engineers, consultants and specialists who build technology around our clients&rsquo; businesses across cloud, security, networking and infrastructure.</p>
<h3>Why work with us</h3>
<ul>
<li><strong>Meaningful work</strong> &mdash; deliver projects for organizations that depend on reliable, secure IT.</li>
<li><strong>Continuous learning</strong> &mdash; hands-on exposure to enterprise platforms and modern cloud technologies.</li>
<li><strong>Collaborative culture</strong> &mdash; a customer-centric team where quality comes without compromise.</li>
</ul>
<h3>How to apply</h3>
<p>We are always keen to hear from talented people. Share your CV and the role you are interested in through our <a href="/contact/">contact page</a>.</p>
"""


def seed(apps, schema_editor):
    Page = apps.get_model('cms', 'Page')
    Page.objects.get_or_create(
        slug='careers',
        defaults={
            'title': 'Careers',
            'content': CAREERS_CONTENT.strip(),
            'meta_description': 'Build your career with TM Solutech.',
            'is_published': True,
        },
    )


def unseed(apps, schema_editor):
    # No-op: the page may have been edited in the dashboard since this ran.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
