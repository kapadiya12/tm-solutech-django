from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import SiteSettings, Statistic, WhyUsReason, Leadership, FAQ, Testimonial
from services.models import ServiceCategory, Service, Industry
from insights.models import BlogCategory, BlogPost
from cms.models import Page


class Command(BaseCommand):
    help = 'Seed the database with TM Solutech content'

    def handle(self, *args, **options):
        self.stdout.write('Seeding TM Solutech data...')

        # Site Settings
        settings, _ = SiteSettings.objects.get_or_create(pk=1)
        settings.company_name = 'TM Solutech Private Limited'
        settings.tagline = 'Smart IT Solutions for Modern Businesses'
        settings.phone = '+91 79 4771 7070'
        settings.email = 'info@tmsolutech.com'
        settings.address = '805/806 Aditya Building, Near Mithakhali Six Roads, Ellisbridge, Ahmedabad, Gujarat 380006'
        settings.linkedin_url = 'https://www.linkedin.com/company/tmsolutech'
        settings.facebook_url = 'https://www.facebook.com/tmsolutech'
        settings.footer_description = 'TM Solutech Private Limited is a leading IT solutions company specializing in Cloud Solutions, Network & Security, and Remote Infrastructure Management. With heritage dating back to 1985, we deliver customized, cost-effective technology solutions that help businesses grow and thrive.'
        settings.copyright_text = f'© {timezone.now().year} TM Solutech Private Limited. All Rights Reserved.'
        settings.meta_title = 'TM Solutech | Smart IT Solutions for Modern Businesses'
        settings.meta_description = 'TM Solutech provides enterprise Cloud Solutions, Network & Security, and Remote Infrastructure Management services. Trusted IT partner since 1985.'
        settings.google_maps_embed = '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3671.9!2d72.56!3d23.03!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMjPCsDAyJzA2LjEiTiA3MsKwMzMnMzYuNCJF!5e0!3m2!1sen!2sin!4v1" width="100%" height="400" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'
        settings.save()
        self.stdout.write(self.style.SUCCESS('  ✓ Site Settings'))

        # Statistics
        stats_data = [
            {'label': 'Organizations Served', 'value': '150', 'suffix': '+', 'icon': 'fas fa-building', 'display_order': 1},
            {'label': 'Team Members', 'value': '250', 'suffix': '+', 'icon': 'fas fa-users', 'display_order': 2},
            {'label': 'Years of Heritage', 'value': '35', 'suffix': '+', 'icon': 'fas fa-calendar', 'display_order': 3},
            {'label': 'Expert Support', 'value': '24', 'suffix': '/7', 'icon': 'fas fa-headset', 'display_order': 4},
        ]
        for s in stats_data:
            Statistic.objects.get_or_create(label=s['label'], defaults=s)
        self.stdout.write(self.style.SUCCESS('  ✓ Statistics'))

        # Why Us Reasons
        reasons = [
            {'title': 'Cross-Industry Expertise', 'description': 'Deep experience across Banking, Hi-Tech, Medical, Industrial, and SME sectors. We bring specialized knowledge to deliver solutions tailored to your industry\'s unique challenges, having served 150+ banking institutions and enterprises across multiple verticals.', 'icon': 'fas fa-globe', 'display_order': 1},
            {'title': 'Deep Expertise & Leadership', 'description': 'Backed by experienced leaders with 30+ years in IT, including software development, hardware architecture, networking, and cybersecurity. Our leadership team brings decades of hands-on experience to every project.', 'icon': 'fas fa-users-cog', 'display_order': 2},
            {'title': 'Dedicated IT Solutions', 'description': 'Every project is unique because we prioritize your specific needs. Our philosophy of \'growing together\' drives us to deliver custom-tailored solutions with time efficiency and cost-effectiveness, without compromising on quality.', 'icon': 'fas fa-handshake', 'display_order': 3},
            {'title': 'Quality Without Compromise', 'description': 'Our working systems are tailored to reduce timescales and costs while maintaining the highest quality standards. We help clients reach their full potential through efficient, reliable technology solutions.', 'icon': 'fas fa-award', 'display_order': 4},
            {'title': 'End-to-End Solutions', 'description': 'From cloud strategy and migration to cybersecurity and infrastructure management, we provide comprehensive IT solutions under one roof, ensuring seamless integration and consistent quality.', 'icon': 'fas fa-layer-group', 'display_order': 5},
            {'title': '24/7 Support & Monitoring', 'description': 'Our managed services include continuous infrastructure monitoring, automated incident response, and SLA-backed support to ensure your IT systems run smoothly around the clock.', 'icon': 'fas fa-headset', 'display_order': 6},
        ]
        for r in reasons:
            WhyUsReason.objects.get_or_create(title=r['title'], defaults=r)
        self.stdout.write(self.style.SUCCESS('  ✓ Why Us Reasons'))

        # Leadership
        leaders = [
            {
                'name': 'Saumil Shah',
                'designation': 'CEO, TM Systems',
                'short_bio': 'Fresh out of MBA school, Saumil wanted to design high performing software. Beginning with a team of only 2 members in 1985, the company under him has grown to over 250 team members serving 150+ banks across Gujarat, Madhya Pradesh, and Rajasthan.',
                'linkedin_url': 'https://www.linkedin.com/in/saumil-shah-898598a/',
                'display_order': 1,
            },
            {
                'name': 'Binit Shah',
                'designation': 'Director',
                'short_bio': 'With 30+ years of experience in licensed software distribution and management, Binit is focused on providing actionable insights to business teams. He has been instrumental in promoting a large portfolio of licensed software products from both Indian and international vendors.',
                'linkedin_url': 'https://www.linkedin.com/in/binit-shah-9a63113/',
                'display_order': 2,
            },
            {
                'name': 'Saurin Shah',
                'designation': 'Director',
                'short_bio': 'With 24+ years in IT, Saurin specializes in hardware architecture and networking planning and implementation. He possesses extensive experience implementing turnkey Data Center projects and complex networking infrastructure for enterprises.',
                'linkedin_url': '',
                'display_order': 3,
            },
            {
                'name': 'Maunish Shah',
                'designation': 'Director, Software Department',
                'short_bio': 'Joined in 1991, Maunish possesses vast experience across the complete SDLC. Under his leadership, the organization expanded across educational institutions, club management, banking, and industrial enterprises.',
                'linkedin_url': 'https://www.linkedin.com/in/maunish-shah-87a9465/',
                'display_order': 4,
            },
            {
                'name': 'Divyesh Doshi',
                'designation': 'Security Specialist & Product Development',
                'short_bio': 'Specialist in web application security, network security assessments, VAPT, and security training. Experienced in enterprise firewalls, mail servers, and campus management solutions for leading educational institutions.',
                'linkedin_url': '',
                'display_order': 5,
            },
        ]
        for l in leaders:
            Leadership.objects.get_or_create(name=l['name'], defaults=l)
        self.stdout.write(self.style.SUCCESS('  ✓ Leadership'))

        # Service Categories
        categories = [
            {
                'name': 'Cloud Solutions',
                'slug': 'cloud-solutions',
                'short_description': 'Customized and cost-effective cloud computing services covering strategy, maintenance, migration, architecture design, security, and disaster recovery.',
                'description': 'TM Solutech delivers customized and cost-effective cloud computing services. Our cloud solutions cover cloud strategy, maintenance, migration, architecture design, cloud security, and disaster recovery. We follow a three-step engagement methodology: Pre-sales assessment & architecture design, Seamless Cloud Migration with No Downtime guarantee, and Post-migration Managed Support.',
                'icon': 'fas fa-cloud',
                'display_order': 1,
            },
            {
                'name': 'Network & Security',
                'slug': 'network-security',
                'short_description': 'Enterprise-grade network infrastructure and cybersecurity solutions to protect your digital assets and ensure business continuity.',
                'description': 'Our Network & Security solutions provide enterprise-grade protection for your digital infrastructure. From firewalls and VPN to next-generation security and QoS, we design, implement, and manage robust network architectures.',
                'icon': 'fas fa-shield-alt',
                'display_order': 2,
            },
            {
                'name': 'Remote Infrastructure Management',
                'slug': 'remote-infrastructure-management',
                'short_description': 'Cost-effective, continuous remote operations management for enterprise IT environments without requiring dedicated on-premise administrators.',
                'description': 'Our Remote Infrastructure Management services provide cost-effective, continuous remote operations management for global enterprise and SME IT environments, without requiring dedicated on-premise administrators.',
                'icon': 'fas fa-server',
                'display_order': 3,
            },
        ]
        cat_objects = {}
        for c in categories:
            obj, _ = ServiceCategory.objects.get_or_create(slug=c['slug'], defaults=c)
            cat_objects[c['slug']] = obj
        self.stdout.write(self.style.SUCCESS('  ✓ Service Categories'))

        # Services - Cloud Solutions
        cloud_services = [
            {'title': 'Cloud Support & Managed Services', 'slug': 'cloud-support-managed-services', 'icon': 'fas fa-cogs',
             'short_description': '24/7 continuous infrastructure monitoring, automated patch rollouts, cloud cost governance, and SLA-backed helpdesk support.', 'display_order': 1, 'is_featured': True},
            {'title': 'Cloud Security & Compliance', 'slug': 'cloud-security-compliance', 'icon': 'fas fa-lock',
             'short_description': 'Identity and Access Management, data encryption, cloud penetration testing, continuous threat detection, and compliance advisory.', 'display_order': 2, 'is_featured': True},
            {'title': 'Business Continuity & Disaster Recovery', 'slug': 'business-continuity-disaster-recovery', 'icon': 'fas fa-sync-alt',
             'short_description': 'BCDR strategy planning, secondary DR site deployment, automated cloud backup, high-availability failover, and 24/7 recovery monitoring.', 'display_order': 3},
            {'title': 'SharePoint Development & Intranet Solutions', 'slug': 'sharepoint-development-intranet-solutions', 'icon': 'fas fa-sitemap',
             'short_description': 'Custom corporate intranet portals, document management systems, workflow automation, Microsoft 365 integration, and legacy migrations.', 'display_order': 4},
            {'title': 'Office 365 Solutions', 'slug': 'office-365-solutions', 'icon': 'fab fa-microsoft',
             'short_description': 'Microsoft 365 licensing, tenant setup, email migration, Microsoft Teams deployment, SharePoint Online, and license optimization.', 'display_order': 5},
        ]
        for s in cloud_services:
            Service.objects.get_or_create(slug=s['slug'], defaults={**s, 'category': cat_objects['cloud-solutions']})

        # Services - Network & Security
        network_services = [
            {'title': 'Firewalls', 'slug': 'firewalls', 'icon': 'fas fa-fire',
             'short_description': 'Stateful and Deep Packet Inspection, Intrusion Detection & Prevention Systems, perimeter defense, and ongoing firmware hardening.', 'display_order': 1, 'is_featured': True},
            {'title': 'IPsec & SSL VPN', 'slug': 'ipsec-ssl-vpn', 'icon': 'fas fa-key',
             'short_description': 'Remote workforce secure connectivity, enterprise identity integration, split tunneling, role-based access, and VPN session auditing.', 'display_order': 2},
            {'title': 'Next-Generation Firewalls', 'slug': 'next-generation-firewalls', 'icon': 'fas fa-shield-virus',
             'short_description': 'Application awareness, dynamic threat intelligence, user identity profiling, SSL/TLS inspection, and centralized compliance auditing.', 'display_order': 3},
            {'title': 'Quality of Service', 'slug': 'quality-of-service', 'icon': 'fas fa-tachometer-alt',
             'short_description': 'Application bandwidth reservation, traffic classification and shaping for VoIP, video, Core Banking, and ERP systems.', 'display_order': 4},
            {'title': 'Routing & Switching', 'slug': 'routing-switching', 'icon': 'fas fa-network-wired',
             'short_description': 'Enterprise LAN/WAN architecture, L2/L3 switch configuration, VLAN segmentation, redundant routing, and latency minimization.', 'display_order': 5},
            {'title': 'WAN Optimization', 'slug': 'wan-optimization', 'icon': 'fas fa-bolt',
             'short_description': 'Network traffic profiling, WAN acceleration appliances, data deduplication, compression, and latency mitigation for remote branches.', 'display_order': 6},
            {'title': 'Wireless Networking', 'slug': 'wireless-networking', 'icon': 'fas fa-wifi',
             'short_description': 'Site RF surveys, enterprise Wi-Fi with WPA3, centralized WLC management, isolated guest networks, and redundant access points.', 'display_order': 7},
        ]
        for s in network_services:
            Service.objects.get_or_create(slug=s['slug'], defaults={**s, 'category': cat_objects['network-security']})

        # Services - Remote Infrastructure Management
        rim_services = [
            {'title': 'IT Asset Management & Lifecycle Support', 'slug': 'it-asset-management-lifecycle-support', 'icon': 'fas fa-boxes',
             'short_description': 'End-to-end hardware and software inventory tracking, procurement advisory, warranty lifecycle tracking, and compliant EOL decommissioning.', 'display_order': 1},
            {'title': 'IT Strategy & Consulting', 'slug': 'it-strategy-consulting', 'icon': 'fas fa-chess',
             'short_description': 'Technology roadmap development, digital transformation strategy, cloud adoption planning, IT governance, and vendor management.', 'display_order': 2, 'is_featured': True},
            {'title': 'Performance Optimization & Capacity Planning', 'slug': 'performance-optimization-capacity-planning', 'icon': 'fas fa-chart-bar',
             'short_description': 'Server and network bottleneck diagnosis, resource forecasting, load balancing, and periodic capacity consumption reporting.', 'display_order': 3},
            {'title': 'Proactive Monitoring & Incident Management', 'slug': 'proactive-monitoring-incident-management', 'icon': 'fas fa-desktop',
             'short_description': '24/7 continuous health tracking, real-time alerting, rapid incident remediation, root-cause analysis, and ITSM integration.', 'display_order': 4, 'is_featured': True},
            {'title': 'Remote System Administration', 'slug': 'remote-system-administration', 'icon': 'fas fa-terminal',
             'short_description': 'Remote server provisioning, OS patch management, performance tuning, Active Directory management, and backup orchestration.', 'display_order': 5},
            {'title': 'Security Monitoring & Compliance', 'slug': 'security-monitoring-compliance', 'icon': 'fas fa-user-shield',
             'short_description': 'Continuous threat hunting, security log aggregation, vulnerability assessment, regulatory auditing, and incident containment.', 'display_order': 6},
        ]
        for s in rim_services:
            Service.objects.get_or_create(slug=s['slug'], defaults={**s, 'category': cat_objects['remote-infrastructure-management']})
        self.stdout.write(self.style.SUCCESS('  ✓ Services (18 total)'))

        # Industries
        industries = [
            {'name': 'Hi-Tech', 'slug': 'hi-tech', 'icon': 'fas fa-microchip',
             'short_description': 'Cloud data migration, custom mobile application integration, and high-volume data processing infrastructure for technology companies.', 'display_order': 1},
            {'name': 'Banking & Financial Services', 'slug': 'banking', 'icon': 'fas fa-university',
             'short_description': 'Deep domain expertise in cyber fraud prevention, core banking security, SEBI/CSCRF compliance, and specialized banking software serving 150+ banks.', 'display_order': 2},
            {'name': 'Medical & Pharmaceuticals', 'slug': 'medical', 'icon': 'fas fa-heartbeat',
             'short_description': 'On-site engineering support, compute and data storage deployment, and specialized GenAI tools including Custom Copilot for Medical Representatives.', 'display_order': 3},
            {'name': 'Industrial & Manufacturing', 'slug': 'industrial', 'icon': 'fas fa-cog',
             'short_description': 'SAP sizing, ERP infrastructure planning, server/network deployments allowing manufacturing plants to focus on core operations.', 'display_order': 4},
            {'name': 'Small & Medium Enterprises', 'slug': 'sme', 'icon': 'fas fa-briefcase',
             'short_description': 'End-to-end IT modernization, managed network security, and infrastructure outsourcing tailored for growing businesses.', 'display_order': 5},
        ]
        for i in industries:
            Industry.objects.get_or_create(slug=i['slug'], defaults=i)
        self.stdout.write(self.style.SUCCESS('  ✓ Industries'))

        # Blog Categories
        blog_cats = [
            {'name': 'Cybersecurity', 'slug': 'cybersecurity'},
            {'name': 'Cloud Computing', 'slug': 'cloud-computing'},
            {'name': 'AI & Innovation', 'slug': 'ai-innovation'},
            {'name': 'Compliance', 'slug': 'compliance'},
        ]
        blog_cat_objects = {}
        for bc in blog_cats:
            obj, _ = BlogCategory.objects.get_or_create(slug=bc['slug'], defaults=bc)
            blog_cat_objects[bc['slug']] = obj
        self.stdout.write(self.style.SUCCESS('  ✓ Blog Categories'))

        # Blog Posts
        admin_user = User.objects.filter(is_superuser=True).first()
        posts = [
            {
                'title': 'Custom Copilot: Transforming Medical Rep Conversations with AI and Privacy',
                'slug': 'custom-copilot-transforming-medical-rep-conversations',
                'category': blog_cat_objects['ai-innovation'],
                'excerpt': 'Medical representatives frequently face technical, research-heavy questions from doctors. Our proprietary GenAI Custom Copilot gives MRs instant, verified answers from indexed clinical research — deployed 100% on-premises to protect proprietary IP.',
                'content': '<p>Medical representatives (MRs) frequently face technical, research-heavy questions from doctors and specialists regarding drug formulations and clinical patents. Waiting for back-office teams delays the sales cycle significantly.</p><p>TM Solutech developed a proprietary Generative AI (GenAI) Custom Copilot that indexes the pharmaceutical company\'s research papers, clinical trials, and patent documentation to give MRs instant, verified answers.</p><h3>Key Differentiator</h3><p>Implemented <strong>100% on-premises / in the client\'s own private environment</strong>, guaranteeing that proprietary patent and clinical IP never leaves the client\'s infrastructure.</p>',
                'is_published': True,
                'is_featured': True,
                'published_at': timezone.now(),
                'author': admin_user,
            },
            {
                'title': 'Ensuring Compliance with SEBI\'s Cybersecurity Framework: Managed SOC Solution for Stock Brokers',
                'slug': 'ensuring-compliance-sebi-cybersecurity-framework-managed-soc',
                'category': blog_cat_objects['compliance'],
                'excerpt': 'SEBI\'s Cybersecurity and Cyber Resilience Framework (CSCRF) mandates comprehensive security for market intermediaries. TM Solutech offers a 100% SEBI-compliant Managed Security Operations Center with 24/7 threat monitoring.',
                'content': '<p>SEBI\'s Cybersecurity and Cyber Resilience Framework (CSCRF) introduces comprehensive security mandates for market intermediaries.</p><h3>Our Managed SOC Solution</h3><ul><li>100% SEBI-compliant Managed Security Operations Center</li><li>24/7 continuous threat monitoring and automated incident detection/response</li><li>Data localization strictly within Indian borders</li><li>Automated regulatory compliance reporting</li></ul>',
                'is_published': True,
                'published_at': timezone.now(),
                'author': admin_user,
            },
            {
                'title': 'Understanding CSCRF Compliance: How TM Solutech Empowers SEBI-Regulated Entities',
                'slug': 'understanding-cscrf-compliance-sebi-regulated-entities',
                'category': blog_cat_objects['cybersecurity'],
                'excerpt': 'SEBI-regulated entities including stock exchanges, brokers, depositories, and mutual funds must comply with the CSCRF framework. Learn how TM Solutech delivers comprehensive compliance solutions.',
                'content': '<p>The CSCRF framework targets stock exchanges, brokers, depositories, mutual funds, asset management companies, and investment advisors.</p><h3>Framework Components Delivered by TM Solutech</h3><ul><li><strong>Governance & Access Control:</strong> Multi-Factor Authentication, Privileged Access Management, zero-trust policies</li><li><strong>Continuous Monitoring:</strong> Cyber SOC and SIEM real-time analytics</li><li><strong>Network Defense:</strong> NGFW, WAF, VLAN micro-segmentation</li><li><strong>Data Loss Prevention:</strong> Encrypted backups, email authentication, MDM</li><li><strong>Auditing & Resilience:</strong> Scheduled VAPT, automated patching, CCMP</li></ul>',
                'is_published': True,
                'published_at': timezone.now(),
                'author': admin_user,
            },
        ]
        for p in posts:
            BlogPost.objects.get_or_create(slug=p['slug'], defaults=p)
        self.stdout.write(self.style.SUCCESS('  ✓ Blog Posts'))

        # FAQs
        faqs = [
            {'question': 'What IT services does TM Solutech provide?', 'answer': 'TM Solutech provides comprehensive IT solutions including Cloud Solutions (managed services, security, disaster recovery, SharePoint, Office 365), Network & Security (firewalls, VPN, NGFW, routing, wireless), and Remote Infrastructure Management (monitoring, system administration, asset management, IT consulting).', 'category': 'general', 'display_order': 1},
            {'question': 'How long has TM Solutech been in business?', 'answer': 'TM Solutech Private Limited was incorporated in 2020, but carries forward a rich heritage originating in 1985 through TM Systems. Our leadership team brings over 30 years of combined IT experience.', 'category': 'general', 'display_order': 2},
            {'question': 'What industries does TM Solutech serve?', 'answer': 'We serve diverse verticals including Hi-Tech, Banking & Financial Services (150+ banks), Medical & Pharmaceuticals, Industrial & Manufacturing, Small & Medium Enterprises, and Educational institutions.', 'category': 'general', 'display_order': 3},
            {'question': 'Do you provide 24/7 support?', 'answer': 'Yes, our managed services include 24/7 continuous infrastructure monitoring, automated incident response, and SLA-backed helpdesk support to ensure your IT systems run smoothly around the clock.', 'category': 'support', 'display_order': 4},
            {'question': 'What cloud platforms do you support?', 'answer': 'We support major cloud platforms including Microsoft Azure, AWS, and Google Cloud. Our services cover cloud strategy, migration, architecture design, security, compliance, and ongoing managed support.', 'category': 'cloud', 'display_order': 5},
            {'question': 'How do you ensure data security?', 'answer': 'We implement multi-layered security including Identity & Access Management, data encryption, continuous threat detection, penetration testing, compliance advisory (GDPR, HIPAA, ISO, SOC2), and managed SOC services.', 'category': 'services', 'display_order': 6},
            {'question': 'What is your approach to project delivery?', 'answer': 'We follow a structured 5-step delivery framework: Define Scope, Plan, Build, Stabilize, and Execute. This methodology ensures risk mitigation, quality assurance, and timely delivery for every project.', 'category': 'general', 'display_order': 7},
            {'question': 'Where is TM Solutech located?', 'answer': '805/806 Aditya Building, Near Mithakhali Six Roads, Ellisbridge, Ahmedabad, Gujarat 380006, India. You can reach us at +91 79 4771 7070 or info@tmsolutech.com.', 'category': 'general', 'display_order': 8},
        ]
        for f in faqs:
            FAQ.objects.get_or_create(question=f['question'], defaults=f)
        self.stdout.write(self.style.SUCCESS('  ✓ FAQs'))

        # CMS Pages
        pages = [
            {
                'title': 'Privacy Policy',
                'slug': 'privacy-policy',
                'content': '<h2>Privacy Policy</h2><p>TM Solutech Private Limited ("we", "our", "us") is committed to protecting and respecting your privacy. This policy explains how we collect, use, and safeguard your personal information when you visit our website or use our services.</p><h3>Information We Collect</h3><p>We may collect personal data such as your name, email address, phone number, and company name when you fill out a contact form or subscribe to our services.</p><h3>How We Use Your Information</h3><ul><li>To respond to your inquiries and provide the services you request</li><li>To improve our website and services</li><li>To send relevant updates and communications (with your consent)</li><li>To comply with legal obligations</li></ul><h3>Data Security</h3><p>We implement appropriate technical and organizational measures to protect your personal data against unauthorized access, alteration, disclosure, or destruction.</p><h3>Contact</h3><p>For privacy-related inquiries, contact us at info@tmsolutech.com.</p>',
                'is_published': True,
                'show_in_footer': True,
            },
            {
                'title': 'Terms and Conditions',
                'slug': 'terms-and-conditions',
                'content': '<h2>Terms and Conditions</h2><p>These terms and conditions govern your use of the TM Solutech Private Limited website and services.</p><h3>Use of Website</h3><p>By accessing this website, you agree to be bound by these terms. The content is for general information purposes only.</p><h3>Intellectual Property</h3><p>All content, logos, images, and materials on this website are the property of TM Solutech Private Limited and protected by applicable intellectual property laws.</p><h3>Limitation of Liability</h3><p>TM Solutech shall not be liable for any indirect, incidental, or consequential damages arising from the use of our website or services.</p><h3>Governing Law</h3><p>These terms shall be governed by the laws of India. Any disputes shall be subject to the exclusive jurisdiction of courts in Ahmedabad, Gujarat.</p>',
                'is_published': True,
                'show_in_footer': True,
            },
        ]
        for p in pages:
            Page.objects.get_or_create(slug=p['slug'], defaults=p)
        self.stdout.write(self.style.SUCCESS('  ✓ CMS Pages'))

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write(f'  Services: {Service.objects.count()}')
        self.stdout.write(f'  Categories: {ServiceCategory.objects.count()}')
        self.stdout.write(f'  Industries: {Industry.objects.count()}')
        self.stdout.write(f'  Leaders: {Leadership.objects.count()}')
        self.stdout.write(f'  Blog Posts: {BlogPost.objects.count()}')
        self.stdout.write(f'  FAQs: {FAQ.objects.count()}')
