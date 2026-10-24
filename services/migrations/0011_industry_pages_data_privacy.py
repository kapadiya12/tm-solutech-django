"""
- Full content for the industry pages (they only had a one-line summary).
- "Data Privacy & Compliance Services" under Network & Security (listed on the previous site).
Only empty fields are filled; the service is only created when missing.
"""
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations

INDUSTRIES = {
    'industrial': (
        '<p>Large manufacturers run on IT that cannot stop: ERP and SAP, plant networks, design workstations and the data that ties them together. '
        'TM Solutech plans, sizes and implements that infrastructure, and can take over day-to-day IT operations so your teams can focus on manufacturing.</p>'
        '<ul><li>SAP and ERP sizing, servers and storage</li><li>Plant and office networks, Wi-Fi and secure remote access</li>'
        '<li>Data centre build-outs, backup and disaster recovery</li><li>End-user computing, licensing and on-site support</li></ul>',
        '<ul><li><strong>Higher uptime</strong> for production systems through proactive monitoring.</li>'
        '<li><strong>One partner</strong> for hardware, licences, networks and support.</li>'
        '<li><strong>Predictable costs</strong> with AMC and managed services.</li></ul>'),
    'education': (
        '<p>Schools, colleges and universities need campus-wide connectivity, secure labs and simple IT that staff and students can rely on. '
        'TM Solutech has delivered campus networks, mail servers, firewalls and management solutions for leading institutions such as CEPT University.</p>'
        '<ul><li>Campus networks and high-density Wi-Fi</li><li>Computer labs, devices and software licensing</li>'
        '<li>Firewalls, content filtering and secure email</li><li>Microsoft 365 and collaboration tools for teaching</li></ul>',
        '<ul><li><strong>Reliable campus connectivity</strong> for classrooms, hostels and offices.</li>'
        '<li><strong>Safer networks</strong> for students and staff.</li>'
        '<li><strong>Education licensing</strong> guidance that keeps costs down.</li></ul>'),
    'sme': (
        '<p>Growing businesses need enterprise-grade IT without an enterprise-sized team. Share your ideas and we help turn them into reality: '
        'modern infrastructure, managed security and support that scales as you grow.</p>'
        '<ul><li>Office networks, firewalls and secure Wi-Fi</li><li>Microsoft 365, email and cloud migration</li>'
        '<li>Hardware procurement, licensing and AMC</li><li>Remote monitoring and helpdesk support</li></ul>',
        '<ul><li><strong>Enterprise-grade security</strong> at SMB budgets.</li>'
        '<li><strong>A single IT partner</strong> instead of many vendors.</li>'
        '<li><strong>Room to grow</strong> with cloud and managed services.</li></ul>'),
    'banking': (
        '<p>Banks, NBFCs, brokers and insurers face strict regulation and constant cyber threats. TM Solutech has served 150+ banks across Gujarat, '
        'Madhya Pradesh and Rajasthan, and created Autobank, banking software built exclusively for co-operative banks. We help counter cyber fraud, '
        'meet SEBI CSCRF and RBI expectations, and integrate banking applications across platforms.</p>'
        '<ul><li>Core banking infrastructure and Autobank for co-operative banks</li><li>Managed SOC, VAPT and incident response</li>'
        '<li>SEBI CSCRF gap assessments and compliance support</li><li>Secure branch networks, data localisation and backups</li></ul>',
        '<ul><li><strong>Audit-ready security</strong> with evidence for regulators.</li>'
        '<li><strong>24/7 monitoring</strong> of critical banking systems.</li>'
        '<li><strong>Decades of banking experience</strong>, including clients like Adarsh Co-op. Bank and The Gujarat State Co-op. Bank.</li></ul>'),
    'hi-tech': (
        '<p>Software and technology companies move fast and need infrastructure that keeps up. We help move data to the cloud, build mobile and '
        'data-processing capabilities, and run secure, DevOps-ready environments that measurably boost productivity.</p>'
        '<ul><li>Cloud architecture, migration and cost optimisation</li><li>Development and test environments</li>'
        '<li>Secure networks, VPN and endpoint protection</li><li>Licensing for development and productivity tools</li></ul>',
        '<ul><li><strong>Faster delivery</strong> with on-demand environments.</li>'
        '<li><strong>Lower cloud bills</strong> through right-sizing.</li>'
        '<li><strong>Security built in</strong> from code to cloud.</li></ul>'),
    'medical': (
        '<p>Pharmaceutical and medical companies need compliant, always-available IT. We provide on-site engineering support for pharmaceutical '
        'manufacturing and pharmacovigilance teams, deploying servers, storage, client computing and security devices, plus private GenAI tools such as '
        'our Custom Copilot for medical representatives.</p>'
        '<ul><li>Servers, storage and on-site engineering</li><li>Validated, secure networks and backups</li>'
        '<li>Private AI copilots that keep research IP in-house</li><li>Endpoint security and compliance support</li></ul>',
        '<ul><li><strong>Protected research IP</strong> with on-premises AI.</li>'
        '<li><strong>Reliable systems</strong> for regulated operations.</li>'
        '<li><strong>Responsive on-site support</strong> when it matters.</li></ul>'),
}

DATA_PRIVACY = dict(
    title='Data Privacy & Compliance Services',
    slug='data-privacy-compliance',
    icon='fas fa-user-shield',
    short_description='Practical data protection for India\'s DPDP Act, ISO 27001 and sector rules: data discovery, access controls, encryption, policies and audit-ready evidence.',
    description=(
        '<p>Data privacy is now a legal duty, not just good practice. Our Data Privacy &amp; Compliance Services help you understand what personal and '
        'sensitive data you hold, where it lives and who can access it, then put the right technical and policy controls in place.</p>'
        '<p>We align your network and systems with the Digital Personal Data Protection (DPDP) Act, ISO 27001 and sector requirements such as SEBI and '
        'RBI guidelines, and give you the documentation auditors expect.</p>'),
    feature_items=[
        {'icon': 'fas fa-magnifying-glass', 'title': 'Data discovery & mapping', 'text': 'Find where personal and sensitive data is stored and how it flows across your network.'},
        {'icon': 'fas fa-key', 'title': 'Access control & encryption', 'text': 'Least-privilege access, MFA and encryption in transit and at rest.'},
        {'icon': 'fas fa-file-shield', 'title': 'Policies & consent', 'text': 'Privacy policies, retention rules and consent processes aligned with the DPDP Act.'},
        {'icon': 'fas fa-clipboard-check', 'title': 'Audit readiness', 'text': 'Gap assessments, evidence collection and support during audits.'},
    ],
    benefit_items=[
        {'title': 'Lower regulatory risk', 'text': 'Meet DPDP, ISO 27001 and sector obligations with confidence.'},
        {'title': 'Customer trust', 'text': 'Show clients and partners their data is handled responsibly.'},
        {'title': 'Fewer breaches', 'text': 'Reduce exposure by knowing and protecting your sensitive data.'},
    ],
    process_items=[
        {'title': 'Assess', 'text': 'Review data, systems and current controls against the applicable rules.'},
        {'title': 'Plan', 'text': 'Prioritise gaps into a practical remediation roadmap.'},
        {'title': 'Implement', 'text': 'Deploy controls, policies and network safeguards.'},
        {'title': 'Sustain', 'text': 'Monitor, review and keep evidence ready for audits.'},
    ],
    faq_items=[
        {'question': 'Does the DPDP Act apply to my business?', 'answer': 'It applies to most organisations that process digital personal data of people in India. We assess your situation and explain what it means for you.'},
        {'question': 'Can you help us prepare for an ISO 27001 audit?', 'answer': 'Yes. We run a gap assessment, help implement the missing controls and prepare the evidence auditors ask for.'},
    ],
)


def apply(apps, schema_editor):
    Industry = apps.get_model('services', 'Industry')
    Service = apps.get_model('services', 'Service')
    ServiceCategory = apps.get_model('services', 'ServiceCategory')
    for slug, (desc, benefits) in INDUSTRIES.items():
        ind = Industry.objects.filter(slug=slug).first()
        if not ind:
            continue
        fields = []
        if not (ind.description or '').strip():
            ind.description = desc; fields.append('description')
        if not (ind.benefits or '').strip():
            ind.benefits = benefits; fields.append('benefits')
        if fields:
            ind.save(update_fields=fields)

    cat = ServiceCategory.objects.filter(slug='network-security').first()
    if cat and not Service.objects.filter(slug=DATA_PRIVACY['slug']).exists():
        last = Service.objects.filter(category=cat).order_by('-display_order').values_list('display_order', flat=True).first() or 0
        svc = Service(category=cat, display_order=last + 1, is_active=True, show_in_nav=True, **DATA_PRIVACY)
        src = os.path.join(settings.BASE_DIR, 'static', 'images', 'services', 'security-policy-compliance-support.jpg')
        if os.path.exists(src):
            with open(src, 'rb') as f:
                svc.image.save('data-privacy-compliance.jpg', ContentFile(f.read()), save=False)
        svc.save()


class Migration(migrations.Migration):
    dependencies = [('services', '0010_show_medical_industry')]
    operations = [migrations.RunPython(apply, migrations.RunPython.noop)]
