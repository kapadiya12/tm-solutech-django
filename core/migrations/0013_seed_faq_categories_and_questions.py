"""
FAQ categories + a full launch set of questions.

- Existing questions are moved into the new categories.
- The original launch answers are only rewritten while they still hold the
  original text, so answers edited from the dashboard are kept.
- New questions are only added when the same question doesn't exist yet.
"""
from django.db import migrations
from django.utils.html import strip_tags

CATEGORIES = [
    # slug, name, icon, description
    ('general', 'About TM Solutech', 'fas fa-building', 'Who we are, where we are and who we work with.'),
    ('services', 'Services & Solutions', 'fas fa-layer-group', 'What we deliver and how to find the right fit.'),
    ('engagement', 'Working With Us', 'fas fa-handshake', 'Projects, pricing, contracts and getting started.'),
    ('cloud', 'Cloud & Infrastructure', 'fas fa-cloud', 'Cloud platforms, migration, monitoring and recovery.'),
    ('security', 'Cybersecurity & Compliance', 'fas fa-shield-halved', 'Data protection, SOC, VAPT and regulations.'),
    ('support', 'Support & AMC', 'fas fa-headset', 'Support hours, maintenance contracts and raising requests.'),
]

# old fixed choices -> new category
LEGACY = {'general': 'general', 'services': 'services', 'cloud': 'cloud', 'network': 'security',
          'infrastructure': 'cloud', 'billing': 'engagement', 'support': 'support'}

# original launch answers (plain text) keyed by question
ORIGINAL = {
    'What IT services does TM Solutech provide?': 'TM Solutech provides comprehensive IT solutions including Cloud Solutions',
    'How long has TM Solutech been in business?': 'TM Solutech Private Limited was incorporated in 2020, but carries forward a rich heritage originating in 1985 through TM Systems. Our leadership team brings over 30 years',
    'What industries does TM Solutech serve?': 'We serve diverse verticals including Hi-Tech',
    'Do you provide 24/7 support?': 'Yes, our managed services include 24/7 continuous infrastructure monitoring',
    'What cloud platforms do you support?': 'We support major cloud platforms including Microsoft Azure, AWS, and Google Cloud.',
    'How do you ensure data security?': 'We implement multi-layered security including Identity',
    'What is your approach to project delivery?': 'We follow a structured 5-step delivery framework',
    'Where is TM Solutech located?': '805/806 Aditya Building',
}

# (question, category, popular, answer html)
FAQS = [
    # ---- About
    ('What IT services does TM Solutech provide?', 'general', True,
     '<p>TM Solutech is an end-to-end IT services partner. Our six service areas are:</p>'
     '<ul><li><strong>Cloud Solutions:</strong> migration, managed cloud, Microsoft 365, backup and disaster recovery.</li>'
     '<li><strong>Cybersecurity:</strong> threat monitoring (SOC), VAPT, endpoint security, incident response and compliance support.</li>'
     '<li><strong>Network &amp; Security:</strong> firewalls, VPN, routing and switching, Wi-Fi and WAN optimisation.</li>'
     '<li><strong>Remote Infrastructure Management:</strong> proactive monitoring, system administration and IT strategy.</li>'
     '<li><strong>AI Modernization:</strong> custom AI copilots, predictive analytics and intelligent data processing.</li>'
     '<li><strong>IT Hardware &amp; VAR:</strong> procurement, licensing, installation, AMC and on-site support.</li></ul>'
     '<p>See the full list on our <a href="/services/">services page</a>.</p>'),
    ('How long has TM Solutech been in business?', 'general', False,
     '<p>TM Solutech Private Limited was incorporated in 2020 and carries forward a heritage that began in 1985 with TM Systems. '
     'That means decades of hands-on experience running IT for businesses, combined with a modern, cloud-first and security-first approach.</p>'),
    ('What industries does TM Solutech serve?', 'general', False,
     '<p>We work across Banking &amp; Financial Services (including 150+ banks), capital markets, Medical &amp; Pharmaceuticals, '
     'Industrial &amp; Manufacturing, Hi-Tech, Education and Small &amp; Medium Enterprises.</p>'
     '<p>Each industry has its own regulations and risks, and we tailor our solutions to them. Explore our <a href="/services/industries/">industries</a>.</p>'),
    ('Where is TM Solutech located?', 'general', False,
     '<p>Our office is at 805/806 Aditya Building, Near Mithakhali Six Roads, Ellisbridge, Ahmedabad, Gujarat 380006, India.</p>'
     '<p>Many services, such as monitoring, remote administration and cloud management, are delivered remotely, so location is rarely a barrier. '
     'Call <a href="tel:+917947717070">+91 79 4771 7070</a> or email <a href="mailto:info@tmsolutech.com">info@tmsolutech.com</a> to discuss on-site needs.</p>'),

    # ---- Services
    ('How do I know which service my business needs?', 'services', True,
     '<p>You don\'t need to have the answer before talking to us. In a free consultation we learn how your business runs, review your current setup and risks, '
     'and recommend what will make the biggest difference first.</p>'
     '<p>Often that starts with a short assessment of your network, cloud or security posture. <a href="/contact/">Book a consultation</a> to get started.</p>'),
    ('Can you work alongside our in-house IT team or other vendors?', 'services', False,
     '<p>Yes. Many clients use us in a co-managed model: your team keeps day-to-day ownership while we add specialist skills, 24/7 monitoring or extra capacity. '
     'We agree clear responsibilities up front so nothing falls between teams.</p>'),
    ('Do you build custom AI solutions?', 'services', False,
     '<p>Yes. Our AI Modernization team builds private AI copilots trained on your own documents, predictive analytics and intelligent document processing. '
     'Where data is sensitive, we deploy entirely within your own environment so it never leaves your control.</p>'
     '<p>Read how this works in our article on a <a href="/insights/custom-copilot-transforming-medical-rep-conversations/">custom copilot for medical reps</a>, '
     'or see our <a href="/services/ai-modernization/">AI services</a>.</p>'),
    ('Do you supply hardware and software licences?', 'services', False,
     '<p>Yes. As a value-added reseller we source servers, laptops, networking and security equipment and software licences, then install, configure and support them. '
     'We also track warranties and renewals so nothing expires unnoticed. See <a href="/services/it-hardware-var/">IT Hardware &amp; VAR</a>.</p>'),

    # ---- Working with us
    ('What is your approach to project delivery?', 'engagement', False,
     '<p>Every project follows a five-step framework:</p>'
     '<ol><li><strong>Define scope:</strong> agree goals, requirements and success measures.</li>'
     '<li><strong>Plan:</strong> design the solution, timeline and risk controls.</li>'
     '<li><strong>Build:</strong> implement and test in stages.</li>'
     '<li><strong>Stabilise:</strong> go live carefully, with support on hand.</li>'
     '<li><strong>Execute:</strong> hand over, document and keep improving.</li></ol>'
     '<p>You get a single point of contact and regular progress updates throughout.</p>'),
    ('How is pricing structured?', 'engagement', True,
     '<p>It depends on the type of work:</p>'
     '<ul><li><strong>Projects</strong> such as a migration or firewall rollout are usually quoted at a fixed price after scoping.</li>'
     '<li><strong>Managed services</strong> such as monitoring or SOC are a predictable monthly fee, based on the number of users, devices or systems covered.</li>'
     '<li><strong>Hardware, licences and AMC</strong> are quoted per item or per contract term.</li></ul>'
     '<p>We share a clear, itemised quote before any work starts. <a href="/contact/">Request a quote</a>.</p>'),
    ('Do you sign NDAs and SLAs?', 'engagement', False,
     '<p>Yes. We\'re happy to sign a non-disclosure agreement before you share sensitive information. '
     'Managed services and support contracts come with a service level agreement that defines response and resolution times by priority, so expectations are clear on both sides.</p>'),
    ('How quickly can you get started?', 'engagement', False,
     '<p>For most engagements we can start within days of agreeing the scope. Assessments and consultations can usually be scheduled within the week. '
     'If you are dealing with an active security incident or outage, call us directly and we\'ll prioritise it.</p>'),

    # ---- Cloud & infrastructure
    ('What cloud platforms do you support?', 'cloud', False,
     '<p>We work with Microsoft Azure, Amazon Web Services (AWS) and Google Cloud, as well as Microsoft 365 for email and collaboration. '
     'Our services cover strategy, migration, architecture, security, cost optimisation and ongoing managed support. '
     'We\'ll recommend the platform that fits your applications and budget rather than pushing a single vendor.</p>'),
    ('Can you migrate us to the cloud without disrupting the business?', 'cloud', True,
     '<p>Yes. We migrate in planned waves, test each application before cut-over, schedule changes outside business hours and always keep a rollback plan. '
     'Most users notice little more than a short, pre-announced maintenance window.</p>'
     '<p>Our <a href="/insights/cloud-migration-checklist-for-growing-businesses/">cloud migration checklist</a> explains the process step by step.</p>'),
    ('What is Remote Infrastructure Management?', 'cloud', False,
     '<p>It means we look after your servers, network and systems remotely: 24/7 monitoring, patching, backups, user administration, performance tuning and capacity planning. '
     'Problems are often fixed before anyone notices them. Learn more about <a href="/services/remote-infrastructure-management/">Remote Infrastructure Management</a>.</p>'),
    ('Do you help with backup and disaster recovery?', 'cloud', False,
     '<p>Yes. We agree how quickly each system must be restored (RTO) and how much data you can afford to lose (RPO), then design backups and recovery to match, '
     'including ransomware-proof copies. Just as important, we test recovery regularly.</p>'
     '<p>Read our <a href="/insights/disaster-recovery-planning-rto-rpo-backups/">disaster recovery planning guide</a>.</p>'),

    # ---- Security & compliance
    ('How do you ensure data security?', 'security', False,
     '<p>We use layered security, so no single failure exposes your data:</p>'
     '<ul><li>Identity and access management with multi-factor authentication.</li>'
     '<li>Encryption of data in transit and at rest.</li>'
     '<li>Firewalls, network segmentation and endpoint protection.</li>'
     '<li>Continuous threat monitoring and incident response.</li>'
     '<li>Regular VAPT and policies aligned with ISO 27001, CERT-In guidelines and the DPDP Act.</li></ul>'),
    ('Can you help us comply with SEBI\'s CSCRF?', 'security', True,
     '<p>Yes. We help SEBI-regulated entities such as brokers, depository participants and fund houses meet the Cybersecurity and Cyber Resilience Framework: '
     'gap assessments, policies, access controls, a managed SOC, VAPT, and a cyber crisis management plan.</p>'
     '<p>Start with our <a href="/insights/understanding-cscrf-compliance-sebi-regulated-entities/">CSCRF compliance guide</a>.</p>'),
    ('Do you offer a managed Security Operations Centre (SOC)?', 'security', False,
     '<p>Yes. Our managed SOC monitors your logs, endpoints and cloud activity around the clock, investigates alerts and helps you respond, '
     'with audit-ready reports and data kept in India. Read about our <a href="/insights/ensuring-compliance-sebi-cybersecurity-framework-managed-soc/">managed SOC for stock brokers</a>.</p>'),
    ('How often should we run VAPT?', 'security', False,
     '<p>At least once a year, and after any major change such as a new application, a big release or a network redesign. Regulated businesses may have set frequencies. '
     'Our <a href="/insights/vapt-explained-vulnerability-assessment-penetration-testing/">VAPT guide</a> explains what is tested and what a good report includes.</p>'),

    # ---- Support & AMC
    ('Do you provide 24/7 support?', 'support', True,
     '<p>Yes. Our managed services include 24/7 monitoring, so critical issues are detected and escalated at any hour. '
     'Support hours and response times for other requests are set out in your service level agreement, and can be extended to 24/7 where your business needs it.</p>'),
    ('What does an Annual Maintenance Contract (AMC) cover?', 'support', False,
     '<p>An AMC typically covers preventive maintenance visits, breakdown support, on-site L1 and L2 engineers, and help with warranty claims and replacements. '
     'The exact devices, response times and visits are listed in your contract. See our <a href="/services/it-hardware-var/annual-maintenance-service-amc/">AMC service</a>.</p>'),
    ('How do I raise a support request?', 'support', False,
     '<p>Existing clients can use the support channel agreed in their contract. You can also email '
     '<a href="mailto:info@tmsolutech.com">info@tmsolutech.com</a> or call <a href="tel:+917947717070">+91 79 4771 7070</a>. '
     'Include what happened, when it started and how many people are affected, so we can prioritise correctly.</p>'),
]


def seed(apps, schema_editor):
    FAQCategory = apps.get_model('core', 'FAQCategory')
    FAQ = apps.get_model('core', 'FAQ')

    cats = {}
    for order, (slug, name, icon, desc) in enumerate(CATEGORIES, start=1):
        cats[slug], _ = FAQCategory.objects.get_or_create(
            slug=slug, defaults={'name': name, 'icon': icon, 'description': desc, 'display_order': order})

    for faq in FAQ.objects.filter(category__isnull=True):
        faq.category = cats.get(LEGACY.get(faq.legacy_category, 'general'), cats['general'])
        faq.save(update_fields=['category'])

    for order, (question, cat, popular, answer) in enumerate(FAQS, start=1):
        faq = FAQ.objects.filter(question=question).first()
        if faq is None:
            FAQ.objects.create(question=question, answer=answer, category=cats[cat], is_popular=popular,
                               display_order=order, is_active=True)
            continue
        original = ORIGINAL.get(question)
        if original and strip_tags(faq.answer or '').strip().startswith(original):
            faq.answer = answer
            faq.category = cats[cat]
            faq.is_popular = popular
            faq.display_order = order
            faq.save()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0012_faq_categories'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
