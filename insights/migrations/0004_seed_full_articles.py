"""
Full, SEO-ready versions of the launch articles plus three new ones.

- Existing posts are only rewritten while they still hold the short launch
  text (under 200 words), so edits made from the dashboard are never lost.
- New posts are only created when their slug doesn't exist yet.
- Cover images come from tracked files in static/images/blog/.
"""
import os
from datetime import datetime, timezone as dt_tz

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations
from django.utils.html import strip_tags


def _cover(post, filename):
    src = os.path.join(settings.BASE_DIR, 'static', 'images', 'blog', filename)
    if post.featured_image or not os.path.exists(src):
        return
    with open(src, 'rb') as f:
        post.featured_image.save(filename, ContentFile(f.read()), save=False)


COPILOT = """
<p>A doctor asks a medical representative how a new formulation compares with an older molecule in patients with renal impairment. The answer exists, buried in a clinical study report, a patent filing and two internal research summaries. Without help, the rep promises to "get back to you", and the conversation that could have changed a prescription is lost. A <strong>custom copilot</strong> built on the company's own research closes that gap in seconds.</p>
<p>TM Solutech designs and deploys private generative AI assistants for pharmaceutical field teams. This article explains how a custom copilot for medical reps works, why we deploy it on-premises, and what it takes to roll one out safely.</p>

<h2>Why medical rep conversations need a custom copilot</h2>
<p>Doctors and specialists increasingly expect evidence, not brochures. They ask about mechanisms of action, trial endpoints, contraindications, dosing in special populations and how a product differs from competitors. Medical reps are trained well, but no one can memorise every study a company has published or sponsored.</p>
<p>The traditional fallback is a query to the medical affairs team. That works, but it is slow: answers can take days, the doctor has moved on, and the same questions are answered again and again across regions. Generic chatbots are not an option either. They can invent references, they don't know the company's internal data, and sending confidential research to a public AI service is a compliance risk.</p>

<h2>How the custom copilot works</h2>
<p>The copilot uses an approach called retrieval-augmented generation (RAG). Instead of relying on what a language model happens to remember, it searches the company's own approved documents first and then writes an answer grounded in what it found.</p>
<ul>
<li><strong>Indexing:</strong> research papers, clinical trial summaries, product monographs, patent documents and approved FAQs are split into passages and indexed for semantic search.</li>
<li><strong>Retrieval:</strong> when a rep asks a question, the copilot finds the most relevant passages, filtered by the rep's product portfolio and access rights.</li>
<li><strong>Answer with citations:</strong> the model writes a short, plain-language answer and links every statement to the source document and page, so the rep can show the evidence.</li>
<li><strong>Guardrails:</strong> if the documents don't contain an answer, the copilot says so and routes the question to medical affairs instead of guessing.</li>
</ul>
<p>Reps use it from a tablet or phone during the visit. Medical affairs teams can review frequently asked questions, spot gaps in the content library and approve new answers centrally.</p>

<h2>100% on-premises: keeping research IP inside your walls</h2>
<p>For a pharmaceutical company, clinical data and unpublished patent material are among its most valuable assets. That is why TM Solutech deploys the copilot entirely inside the client's own environment, either on their servers or in their private cloud account.</p>
<ul>
<li>Open-weight language models run on the client's hardware, so prompts and documents never reach a public AI provider.</li>
<li>Single sign-on and role-based access ensure each rep only sees content for the products they represent.</li>
<li>Every question and answer is logged for audit, and logs stay within the client's infrastructure.</li>
<li>Encryption in transit and at rest, plus regular security reviews from our <a href="/services/cybersecurity-excellence/threat-monitoring-detection/">threat monitoring team</a>.</li>
</ul>

<h2>What changes for field teams</h2>
<p>The most visible change is speed: questions that used to wait for a reply from head office can be answered during the visit, with the source on screen. Over time, companies also see more consistent messaging across regions, fewer repetitive queries to medical affairs, and faster onboarding for new reps, who can learn the product library by asking questions rather than reading binders.</p>
<p>Just as important, the copilot creates a feedback loop. The questions doctors ask most often show where training, content or even product positioning needs attention.</p>

<h2>Rolling out a custom copilot safely</h2>
<p>We recommend a phased approach:</p>
<ol>
<li><strong>Discovery:</strong> agree the use cases, the document sources and the compliance rules with medical, legal and IT teams.</li>
<li><strong>Pilot:</strong> index one therapy area, test with a small group of reps and have medical affairs review the answers.</li>
<li><strong>Harden:</strong> tune retrieval, add guardrails for off-label questions and connect single sign-on.</li>
<li><strong>Scale:</strong> add therapy areas and languages, and integrate with CRM so insights flow back to marketing.</li>
</ol>
<p>A custom copilot is not a replacement for medical expertise. It is a way to put the company's best knowledge into every conversation, safely. To explore what this could look like for your field force, see our <a href="/services/ai-modernization/custom-ai-copilot-development/">Custom AI Copilot Development</a> service or <a href="/contact/">talk to our team</a>.</p>
"""

SOC = """
<p>Stock brokers face constant cyber threats: phishing aimed at dealers, credential theft, ransomware and attacks on trading and back-office systems. SEBI's Cybersecurity and Cyber Resilience Framework (CSCRF) now expects regulated entities to detect and respond to these threats continuously. For most brokers, a <strong>managed SOC</strong> is the most practical way to get there without building a large in-house security team.</p>
<p>This article explains what CSCRF expects around security monitoring, what a managed Security Operations Centre actually does, and how to choose a provider.</p>

<h2>What CSCRF expects from stock brokers</h2>
<p>SEBI issued CSCRF in August 2024 to bring its earlier cybersecurity circulars together under one framework. Requirements scale with the size and category of the regulated entity, but the themes are common to all brokers:</p>
<ul>
<li>A board-approved cybersecurity and cyber resilience policy, with clear ownership.</li>
<li>Continuous security monitoring, either through an in-house SOC, a market SOC or a third-party managed SOC, depending on the entity's category.</li>
<li>Timely incident reporting, including the six-hour reporting window set by CERT-In for notifiable incidents.</li>
<li>Regular vulnerability assessment and penetration testing, and periodic cyber audits.</li>
<li>Log retention and storage of regulated data within India.</li>
</ul>
<p>Our <a href="/insights/understanding-cscrf-compliance-sebi-regulated-entities/">CSCRF compliance guide</a> covers the full framework. Here we focus on the monitoring piece, because it is where most brokers need outside help.</p>

<h2>What a managed SOC does</h2>
<p>A Security Operations Centre is the team and technology that watch your environment for signs of attack, around the clock. With a managed SOC, a specialist provider runs it for you.</p>
<ul>
<li><strong>Log collection:</strong> firewalls, servers, endpoints, email, Active Directory and trading applications send logs to a central SIEM platform.</li>
<li><strong>Detection:</strong> correlation rules and threat intelligence flag suspicious behaviour, such as impossible logins, privilege changes or data leaving the network.</li>
<li><strong>Triage:</strong> analysts investigate alerts, filter out noise and escalate real incidents with clear next steps.</li>
<li><strong>Response:</strong> isolating an infected device, blocking an IP or disabling a compromised account, following agreed playbooks.</li>
<li><strong>Reporting:</strong> regular reports for management and the evidence auditors ask for.</li>
</ul>

<h2>Why brokers choose a managed SOC over building one</h2>
<p>Running a SOC in-house means hiring analysts for three shifts, licensing a SIEM, writing detection rules and keeping them current. For a mid-size or small broker, that cost is hard to justify, and skilled security analysts are scarce. A managed SOC spreads that cost across clients while giving each one 24/7 coverage, mature processes and analysts who see attack patterns across many organisations.</p>

<h2>TM Solutech's managed SOC for brokers</h2>
<p>We built our service around the realities of Indian capital market firms:</p>
<ul>
<li>24/7 monitoring by our security team, with defined response times for critical alerts.</li>
<li>Logs and data stored within India, aligned with CSCRF data localisation expectations.</li>
<li>Use cases tuned for brokers: dealer terminal abuse, back-office access, API keys and trading platform anomalies.</li>
<li>Incident reporting support so you can meet CERT-In and SEBI timelines.</li>
<li>Audit-ready monthly reports mapped to CSCRF requirements.</li>
<li>Integration with our <a href="/services/cybersecurity-excellence/incident-response-recovery/">incident response</a> and <a href="/services/cybersecurity-excellence/vulnerability-assessment-penetration-testing/">VAPT</a> services.</li>
</ul>

<h2>What to expect in the first 90 days</h2>
<p>Onboarding usually happens in stages. In the first weeks, critical systems such as firewalls, domain controllers and trading servers are connected and baseline alerts are tuned. Next, endpoints, email and cloud services are added. By the end of the first quarter, you should have stable alerting, agreed escalation paths and your first audit-ready report.</p>

<h2>How to choose a managed SOC provider</h2>
<p>Ask every provider these questions before you sign:</p>
<ol>
<li>Where are logs and data stored, and who can access them?</li>
<li>What are the response times for critical, high and medium alerts?</li>
<li>Which of our systems will be monitored on day one, and which later?</li>
<li>Do you help with regulatory incident reporting and audits?</li>
<li>Can we see the dashboard and raw alerts, or only monthly reports?</li>
</ol>
<p>A good provider answers these clearly and puts them in the contract. If you'd like to see how our managed SOC would fit your setup, <a href="/contact/">book a consultation</a> and we'll walk you through a sample report.</p>
"""

CSCRF = """
<p>SEBI's Cybersecurity and Cyber Resilience Framework, known as CSCRF, changes how regulated entities in India's securities market must protect their systems and data. This guide explains what <strong>CSCRF compliance</strong> means, who it applies to, and how to build a practical roadmap to meet it.</p>

<h2>What is CSCRF?</h2>
<p>SEBI issued CSCRF in August 2024. It replaces a patchwork of earlier cybersecurity circulars with a single framework built around five resilience goals: anticipate, withstand, contain, recover and evolve. Instead of one rulebook for everyone, it sets requirements proportionate to each entity's size and risk.</p>
<p>The framework is organised around familiar security functions: governance, identify, protect, detect, respond and recover. Each comes with standards and, for larger entities, measurable expectations.</p>

<h2>Who must achieve CSCRF compliance?</h2>
<p>CSCRF applies to SEBI-regulated entities, including stock exchanges, clearing corporations and depositories, stock brokers, depository participants, mutual funds and asset management companies, portfolio managers, investment advisers, research analysts, KYC registration agencies and registrars.</p>
<p>Entities are grouped into categories: market infrastructure institutions, qualified regulated entities, mid-size, small-size and self-certification entities. The category decides how deep the requirements go and which deadlines apply, so the first step is to confirm yours against SEBI's latest circulars.</p>

<h2>Key requirements at a glance</h2>
<ul>
<li><strong>Governance:</strong> a board-approved cybersecurity policy, a designated CISO or equivalent, and an IT committee that reviews cyber risk.</li>
<li><strong>Identify:</strong> an up-to-date inventory of hardware, software and data, with critical systems clearly marked.</li>
<li><strong>Protect:</strong> multi-factor authentication, privileged access management, network segmentation, patching and encrypted backups.</li>
<li><strong>Detect:</strong> continuous monitoring through a security operations centre, with logs retained as required.</li>
<li><strong>Respond and recover:</strong> a cyber crisis management plan, tested incident response, and timely reporting to CERT-In and SEBI.</li>
<li><strong>Assurance:</strong> periodic VAPT and cyber audits, with findings tracked to closure.</li>
</ul>

<h2>A practical roadmap to CSCRF compliance</h2>
<ol>
<li><strong>Gap assessment:</strong> compare your current controls with the requirements for your category and list what is missing.</li>
<li><strong>Prioritise:</strong> fix the high-risk gaps first, usually access control, monitoring and backups.</li>
<li><strong>Policies and governance:</strong> write or update the policies, assign owners and take them to the board.</li>
<li><strong>Implement controls:</strong> deploy MFA, PAM, firewalls, endpoint protection and logging.</li>
<li><strong>Monitor:</strong> connect systems to a SOC so threats are detected around the clock.</li>
<li><strong>Test:</strong> run VAPT, rehearse the crisis plan and fix what the tests reveal.</li>
<li><strong>Evidence:</strong> keep reports, logs and sign-offs ready for auditors.</li>
</ol>

<h2>Timelines and staying current</h2>
<p>SEBI has issued clarifications and adjusted timelines for different categories since CSCRF was first published, and it is likely to keep refining the framework. Treat your compliance plan as a living document: assign someone to track SEBI and CERT-In circulars, review your category each year as your business grows, and update policies and controls when requirements change. Building controls that genuinely reduce risk, rather than ticking boxes, also makes each future change easier to absorb.</p>

<h2>How TM Solutech helps</h2>
<p>We work with regulated entities end to end, from the first gap assessment to ongoing monitoring:</p>
<ul>
<li><strong>Governance and access control:</strong> multi-factor authentication, privileged access management and zero-trust policies.</li>
<li><strong>Continuous monitoring:</strong> our <a href="/insights/ensuring-compliance-sebi-cybersecurity-framework-managed-soc/">managed SOC</a> with SIEM and 24/7 analysts.</li>
<li><strong>Network defence:</strong> <a href="/services/network-security/firewalls/">next-generation firewalls</a>, web application firewalls and VLAN segmentation.</li>
<li><strong>Data protection:</strong> encrypted backups, email authentication and mobile device management.</li>
<li><strong>Assurance:</strong> scheduled VAPT, automated patching and a tested cyber crisis management plan.</li>
</ul>

<h2>Common CSCRF mistakes to avoid</h2>
<p>The most common problem we see is treating CSCRF as a documentation exercise. Policies matter, but auditors look for evidence that controls actually work: alerts investigated, patches applied, backups restored in tests. Other pitfalls include an incomplete asset inventory, shared admin accounts, and third-party vendors with broad access that nobody reviews.</p>
<p>CSCRF compliance is a continuous programme, not a one-time project. Need help finding where you stand? <a href="/contact/">Contact us</a> for a CSCRF gap assessment.</p>
"""

CLOUD = """
<p>Moving to the cloud can cut infrastructure costs, improve uptime and make it easier to scale. But a rushed move can do the opposite: surprise bills, slow applications and security gaps. This <strong>cloud migration</strong> checklist walks through the seven steps we follow with clients, so you can plan a move that delivers what it promised.</p>

<h2>Why plan before you migrate?</h2>
<p>Most failed migrations share the same causes: nobody knew exactly what was running on-premises, applications were moved without being tested, and costs were estimated from list prices rather than real usage. A short planning phase prevents all three. It also gives the business confidence, because everyone knows what will move, when, and how to roll back if something goes wrong.</p>

<h2>The 7-step cloud migration checklist</h2>
<h3>1. Take inventory</h3>
<p>List every server, application, database, licence and integration. Note who owns each one, how critical it is and what depends on it. Discovery tools help, but talk to the teams too: undocumented scripts and file shares are often what break after a move.</p>

<h3>2. Define goals and success measures</h3>
<p>Be specific. "Reduce hardware refresh costs", "recover from an outage within four hours" or "let staff work securely from anywhere" are goals you can measure. They also help you decide which workloads to move first.</p>

<h3>3. Choose a strategy for each workload</h3>
<p>Not everything should move the same way. The common options are:</p>
<ul>
<li><strong>Rehost:</strong> lift and shift the server as-is. Fastest, but saves the least.</li>
<li><strong>Replatform:</strong> make small changes, such as moving a database to a managed service.</li>
<li><strong>Refactor:</strong> rebuild the application to use cloud-native services.</li>
<li><strong>Repurchase:</strong> replace it with a SaaS product, for example moving email to Microsoft 365.</li>
<li><strong>Retire or retain:</strong> switch off what nobody uses, and keep on-premises what must stay.</li>
</ul>

<h3>4. Design security and compliance in</h3>
<p>Plan identity and access, network segmentation, encryption, logging and backup before the first workload moves. If you are regulated, confirm where data will be stored. Our <a href="/services/cloud-solutions/cloud-security-compliance/">cloud security and compliance</a> team builds this landing zone so every workload inherits the same controls.</p>

<h3>5. Estimate costs realistically</h3>
<p>Size cloud resources on actual usage, not on the specification of old servers, which are often oversized. Include storage, backup, data transfer and support. Then look at reserved capacity or savings plans for steady workloads.</p>

<h3>6. Migrate in waves and test</h3>
<p>Start with a low-risk application to prove the process, then move in waves. For each wave, test performance and integrations, agree a cut-over window and keep a rollback plan ready. Communicate early with users about any downtime.</p>

<h3>7. Optimise after go-live</h3>
<p>Migration day is the start, not the finish. Review usage monthly, rightsize resources, switch off what is idle and set budget alerts. Monitor performance and security continuously.</p>

<h2>Do you have to move everything?</h2>
<p>No. Many businesses settle on a hybrid model: customer-facing applications, email and collaboration move to the cloud, while specialised systems, latency-sensitive workloads or equipment-linked applications stay on-premises. The right mix depends on cost, performance and regulation. A good cloud migration plan states clearly what stays, why, and how the two environments will be secured, monitored and backed up together.</p>

<h2>Common cloud migration mistakes</h2>
<ul>
<li>Moving everything at once instead of in planned waves.</li>
<li>Forgetting licensing rules, which can change when software runs in the cloud.</li>
<li>Leaving storage or databases publicly accessible by mistake.</li>
<li>No backup or disaster recovery plan for cloud workloads. Read our <a href="/insights/disaster-recovery-planning-rto-rpo-backups/">disaster recovery planning guide</a>.</li>
</ul>

<h2>How TM Solutech helps</h2>
<p>We handle assessment, planning, migration and ongoing management, so your team can stay focused on the business. Learn more about our <a href="/services/cloud-solutions/cloud-migration-services/">cloud migration services</a> or <a href="/contact/">contact us</a> for a free migration readiness review.</p>
"""

VAPT = """
<p>Every business with a website, a network or a mobile app has weaknesses it doesn't know about. <strong>VAPT</strong>, short for Vulnerability Assessment and Penetration Testing, is how you find them before attackers do. This guide explains what VAPT covers, how the two parts differ, how often you need it and what a good report looks like.</p>

<h2>What is VAPT?</h2>
<p>VAPT combines two complementary security tests:</p>
<ul>
<li><strong>Vulnerability assessment:</strong> a broad, largely automated scan that finds known weaknesses, such as missing patches, outdated software, weak configurations and exposed services. It answers the question "what could be wrong?"</li>
<li><strong>Penetration testing:</strong> a focused, manual exercise in which ethical hackers try to exploit those weaknesses, just as a real attacker would. It answers "what could an attacker actually do?"</li>
</ul>
<p>A scan alone produces long lists with many false positives. A penetration test alone may miss issues outside its scope. Together, they give you both breadth and real-world proof.</p>

<h2>Types of VAPT</h2>
<ul>
<li><strong>Network and infrastructure:</strong> servers, firewalls, routers, Wi-Fi and cloud environments, from outside and inside the network.</li>
<li><strong>Web applications:</strong> testing for issues such as broken access control, injection and insecure authentication, typically guided by the OWASP Top 10.</li>
<li><strong>Mobile applications:</strong> the app itself, the data it stores on the device and the APIs it talks to.</li>
<li><strong>APIs:</strong> authentication, authorisation and data exposure in the services your apps and partners use.</li>
</ul>
<p>Tests can be black box (the tester knows nothing, like an outside attacker), grey box (some access, like a regular user) or white box (full information, for the deepest coverage).</p>

<h2>How often do you need VAPT?</h2>
<p>As a baseline, test at least once a year, and always after major changes: a new application, a significant release, a network redesign or a move to the cloud. Regulated businesses may have set frequencies. SEBI's framework, for example, requires periodic VAPT for regulated entities, and payment card standards require regular testing too. Our <a href="/insights/understanding-cscrf-compliance-sebi-regulated-entities/">CSCRF compliance guide</a> covers the securities market rules.</p>

<h2>The VAPT process, step by step</h2>
<ol>
<li><strong>Scoping:</strong> agree what will be tested, how, and when, with written authorisation.</li>
<li><strong>Discovery:</strong> map the systems, services and entry points in scope.</li>
<li><strong>Vulnerability assessment:</strong> run scans and review the results to remove false positives.</li>
<li><strong>Exploitation:</strong> safely attempt to exploit the important findings to prove impact.</li>
<li><strong>Reporting:</strong> document each finding with evidence, severity and clear fix steps.</li>
<li><strong>Retesting:</strong> confirm that fixes work after your team applies them.</li>
</ol>

<h2>What a good VAPT report includes</h2>
<p>A useful report is written for two audiences. Management gets a short summary of overall risk and the most important issues. Technical teams get each finding with its severity, affected systems, proof, business impact and step-by-step remediation. Be wary of reports that are just raw scanner output: they are hard to act on and don't show what an attacker could really achieve.</p>

<h2>Common VAPT myths</h2>
<ul>
<li><strong>"We're too small to be a target."</strong> Most attacks are automated and scan the whole internet for known weaknesses. Size doesn't matter; exposure does.</li>
<li><strong>"Our firewall protects us."</strong> Firewalls don't stop attacks through your website, stolen passwords or a vulnerable application that must be reachable from the internet.</li>
<li><strong>"We passed last year."</strong> New vulnerabilities are published every day, and every software update or configuration change can introduce new risk.</li>
<li><strong>"Testing will disrupt our systems."</strong> Experienced testers agree safe methods and time windows in advance, and avoid destructive techniques on production systems.</li>
</ul>

<h2>VAPT with TM Solutech</h2>
<p>Our security team performs network, web, mobile and API testing, maps findings to the frameworks you need to meet, and includes a free retest so you can close issues with confidence. Testing is planned around your business hours to avoid disruption. Learn more about our <a href="/services/cybersecurity-excellence/vulnerability-assessment-penetration-testing/">VAPT services</a> or <a href="/contact/">request a quote</a>.</p>
"""

DR = """
<p>Ransomware, a failed storage array, a fire or a simple mistake by an administrator can stop a business in minutes. <strong>Disaster recovery</strong> planning decides how quickly you get back up and how much data you lose when that happens. This guide explains the two numbers that matter most, RTO and RPO, how to build a backup strategy around them, and how to test that it actually works.</p>

<h2>Disaster recovery vs business continuity</h2>
<p>The two are related but different. Business continuity is the wider plan for keeping the organisation running during a disruption: people, offices, suppliers and communication. Disaster recovery is the IT part of that plan: restoring systems, applications and data. You need both, and the IT plan should be built from the business priorities, not the other way around.</p>

<h2>RTO and RPO: the two numbers to agree first</h2>
<ul>
<li><strong>Recovery Time Objective (RTO):</strong> how long a system can be down before the impact becomes unacceptable. An online trading platform might need an RTO of minutes; an archive server might tolerate two days.</li>
<li><strong>Recovery Point Objective (RPO):</strong> how much data you can afford to lose, measured in time. An RPO of one hour means backups or replication must capture changes at least every hour.</li>
</ul>
<p>Agree RTO and RPO for each important system with business owners. Shorter targets cost more, so it is normal to have tiers: a few critical systems with near-zero targets, and the rest with hours or a day.</p>

<h2>Building a backup strategy for disaster recovery</h2>
<p>A widely used starting point is the 3-2-1 rule: keep three copies of your data, on two different types of storage, with one copy offsite. Today we recommend going further:</p>
<ul>
<li><strong>Immutable or offline copies:</strong> backups that cannot be changed or deleted, even by an administrator, so ransomware can't destroy them.</li>
<li><strong>Separate credentials:</strong> backup systems should not share admin accounts with production.</li>
<li><strong>Encryption:</strong> protect backups in transit and at rest.</li>
<li><strong>Retention:</strong> keep enough history to recover from problems discovered late, such as slow data corruption.</li>
</ul>

<h2>Choosing a disaster recovery site</h2>
<p>Backups protect data; a recovery site restores service. The main options are a secondary data centre, a cloud-based recovery environment, or Disaster Recovery as a Service, where a provider keeps replicas of your systems ready to start. Cloud-based recovery has made short RTOs affordable for mid-size businesses, because you pay mostly for storage until you actually need to fail over. If you are moving workloads anyway, our <a href="/insights/cloud-migration-checklist-for-growing-businesses/">cloud migration checklist</a> shows how to build recovery in from day one.</p>

<h2>Writing the disaster recovery plan</h2>
<ol>
<li>List critical systems with their RTO, RPO, owners and dependencies.</li>
<li>Document step-by-step recovery procedures that someone other than the usual administrator could follow.</li>
<li>Define who declares a disaster and how staff, customers and regulators are informed.</li>
<li>Keep contact lists and the plan itself available offline.</li>
</ol>

<h2>Test, test and test again</h2>
<p>An untested plan is only a hope. Run tabletop exercises to walk through scenarios, restore individual files and full servers regularly, and perform a full failover test at least once a year. Record how long each step took, compare it with your RTO and fix what was slow. Many organisations discover during their first test that a backup was incomplete or that a key password was missing.</p>

<h2>Quick disaster recovery checklist</h2>
<ul>
<li>RTO and RPO agreed and signed off for every critical system.</li>
<li>At least one immutable or offline backup copy.</li>
<li>Recovery steps written down and stored offline.</li>
<li>A full restore tested in the last twelve months.</li>
<li>Clear decision-makers and a communication plan for staff and customers.</li>
</ul>

<h2>How TM Solutech helps</h2>
<p>We assess your current setup, agree RTO and RPO with your teams, design backup and recovery on-premises or in the cloud, and run recovery tests with you. Explore our <a href="/services/cloud-solutions/business-continuity-disaster-recovery/">business continuity and disaster recovery services</a> or <a href="/contact/">talk to an expert</a>.</p>
"""

UPDATES = {
    'custom-copilot-transforming-medical-rep-conversations': dict(
        title='Custom Copilot for Medical Reps: Instant, Private AI Answers',
        excerpt='Medical reps face research-heavy questions from doctors every day. A custom copilot built on your own clinical documents gives them verified answers in seconds, deployed fully on-premises to protect your IP.',
        content=COPILOT, focus_keyword='custom copilot', tags='AI, Generative AI, Pharma, Copilot',
        meta_title='Custom Copilot for Medical Reps | Private GenAI',
        meta_description='How a custom copilot gives pharma medical reps instant, cited answers from clinical research, deployed fully on-premises so your IP stays private.',
    ),
    'ensuring-compliance-sebi-cybersecurity-framework-managed-soc': dict(
        title='Managed SOC for Stock Brokers: Meeting SEBI CSCRF Rules',
        excerpt="SEBI's CSCRF expects stock brokers to monitor and respond to cyber threats around the clock. Here's what a managed SOC does, why most brokers choose one, and how to pick the right provider.",
        content=SOC, focus_keyword='managed SOC', tags='SOC, SEBI, CSCRF, Cybersecurity, Stock Brokers',
        meta_title='Managed SOC for Stock Brokers | SEBI CSCRF',
        meta_description='What SEBI CSCRF expects from stock brokers on security monitoring, how a managed SOC delivers 24/7 detection and response, and how to choose a provider.',
    ),
    'understanding-cscrf-compliance-sebi-regulated-entities': dict(
        title='CSCRF Compliance Guide for SEBI-Regulated Entities',
        excerpt="A plain-language guide to SEBI's Cybersecurity and Cyber Resilience Framework: who it applies to, the key requirements, and a seven-step roadmap to CSCRF compliance.",
        content=CSCRF, focus_keyword='CSCRF compliance', tags='CSCRF, SEBI, Compliance, Cybersecurity',
        meta_title='CSCRF Compliance Guide | SEBI-Regulated Entities',
        meta_description="CSCRF compliance explained: who SEBI's framework applies to, the key requirements by function, and a practical seven-step roadmap for regulated entities.",
    ),
}

NEW_POSTS = [
    dict(
        slug='cloud-migration-checklist-for-growing-businesses', category='cloud-computing',
        title='Cloud Migration Checklist: 7 Steps for Growing Businesses',
        excerpt='Planning a move to the cloud? This seven-step cloud migration checklist covers inventory, strategy, security, costs and testing, so your move delivers what it promised.',
        content=CLOUD, focus_keyword='cloud migration', tags='Cloud, Cloud Migration, Azure, AWS',
        meta_title='Cloud Migration Checklist: 7 Steps | TM Solutech',
        meta_description='A practical cloud migration checklist: take inventory, choose a strategy per workload, design security in, estimate costs and migrate in tested waves.',
        cover='cloud-migration.jpg', published_at=datetime(2026, 10, 2, 10, 0, tzinfo=dt_tz.utc),
    ),
    dict(
        slug='vapt-explained-vulnerability-assessment-penetration-testing', category='cybersecurity',
        title='VAPT Explained: Why Every Business Needs Regular Testing',
        excerpt='VAPT finds the weaknesses in your network, website and apps before attackers do. Learn what it covers, how often you need it and what a useful report looks like.',
        content=VAPT, focus_keyword='VAPT', tags='VAPT, Penetration Testing, Cybersecurity, Compliance',
        meta_title='VAPT Explained | Vulnerability Assessment & Pen Testing',
        meta_description='VAPT explained: how vulnerability assessment and penetration testing differ, the types of testing, how often you need it and what a good report includes.',
        cover='vapt.jpg', published_at=datetime(2026, 10, 9, 10, 0, tzinfo=dt_tz.utc),
    ),
    dict(
        slug='disaster-recovery-planning-rto-rpo-backups', category='cloud-computing',
        title='Disaster Recovery Planning: RTO, RPO and Backups Explained',
        excerpt='How quickly can you recover from ransomware or an outage, and how much data would you lose? A practical guide to disaster recovery planning, RTO, RPO and testing.',
        content=DR, focus_keyword='disaster recovery', tags='Disaster Recovery, Backup, Business Continuity, Ransomware',
        meta_title='Disaster Recovery Planning: RTO, RPO & Backups',
        meta_description='A practical disaster recovery guide: agree RTO and RPO, build ransomware-proof backups, choose a recovery site and test your plan so it works on the day.',
        cover='disaster-recovery.jpg', published_at=datetime(2026, 10, 15, 10, 0, tzinfo=dt_tz.utc),
    ),
]


def seed(apps, schema_editor):
    BlogPost = apps.get_model('insights', 'BlogPost')
    BlogCategory = apps.get_model('insights', 'BlogCategory')

    for slug, fields in UPDATES.items():
        post = BlogPost.objects.filter(slug=slug).first()
        if not post or len(strip_tags(post.content or '').split()) >= 200:
            continue
        for k, v in fields.items():
            setattr(post, k, v.strip() if isinstance(v, str) else v)
        post.save()

    for data in NEW_POSTS:
        data = dict(data)
        if BlogPost.objects.filter(slug=data['slug']).exists():
            continue
        cover = data.pop('cover')
        category = BlogCategory.objects.filter(slug=data.pop('category')).first()
        post = BlogPost(category=category, is_published=True, **{k: (v.strip() if isinstance(v, str) else v) for k, v in data.items()})
        _cover(post, cover)
        post.save()


class Migration(migrations.Migration):
    dependencies = [
        ('insights', '0003_blogpost_focus_keyword'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
