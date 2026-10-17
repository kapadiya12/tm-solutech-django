"""Restructure the service catalog to the client's six service areas.

AI Modernization comes first. Existing services keep their page content and
URLs and only get the client's titles and order. 20 new services are created
with full page content. Next-Generation Firewalls is not on the client's list,
so it is hidden (is_active=False), not deleted.

Safe to run on a database edited in the dashboard: new rows are only created
when their slug is missing, and existing content is never overwritten.
"""
import json

from django.db import migrations


LAYOUT = [('ai-modernization',
  None,
  ['ai-strategy-consulting',
   'custom-ai-copilot-development',
   'predictive-analytics-forecasting',
   'ai-powered-mobile-app-intelligence',
   'intelligent-data-processing',
   'ai-integration-existing-systems']),
 ('cloud-solutions',
  'Cloud Solutions',
  [('cloud-support-managed-services', 'Cloud Support & Managed Services'),
   ('cloud-security-compliance', 'Cloud Security & Compliance'),
   'cloud-migration-services',
   ('business-continuity-disaster-recovery', 'Business Continuity & Disaster Recovery'),
   ('office-365-solutions', 'Office 365 & Collaboration Tools'),
   ('sharepoint-development-intranet-solutions', 'SharePoint & Intranet Development')]),
 ('cybersecurity-excellence',
  None,
  ['threat-monitoring-detection',
   'vulnerability-assessment-penetration-testing',
   'endpoint-security',
   'incident-response-recovery',
   'security-policy-compliance-support']),
 ('network-security',
  'Network & Security',
  [('firewalls', 'Firewall Security'),
   ('ipsec-ssl-vpn', 'Secure VPN Solutions (Remote Access)'),
   ('routing-switching', 'Routing & Switching'),
   ('wireless-networking', 'Wireless Networking (Wi-Fi Solutions)'),
   ('quality-of-service', 'QoS & Bandwidth Optimization'),
   ('wan-optimization', 'WAN Optimization')]),
 ('remote-infrastructure-management',
  'Remote Infrastructure Management',
  [('it-asset-management-lifecycle-support', 'IT Asset Management & Lifecycle Support'),
   ('it-strategy-consulting', 'IT Strategy & Consulting'),
   ('performance-optimization-capacity-planning', 'Performance Optimization & Capacity Planning'),
   ('proactive-monitoring-incident-management', 'Proactive Monitoring & Incident Management'),
   ('remote-system-administration', 'Remote System Administration'),
   ('security-monitoring-compliance', 'Security Monitoring & Compliance')]),
 ('it-hardware-var',
  None,
  ['hardware-procurement',
   'software-licensing',
   'installation-configuration',
   'warranty-renewal-management',
   'after-sales-technical-support',
   'product-consultation-recommendations',
   'annual-maintenance-service-amc',
   'on-site-l1-l2-support-services'])]

RETIRED = ['next-generation-firewalls']

# New categories and services (content for rows that don't exist yet).
CATALOG = json.loads(r'''
{
 "categories": {
  "ai-modernization": {
   "slug": "ai-modernization",
   "name": "AI Modernization",
   "short_description": "Practical AI adoption for enterprises, from strategy and copilots to forecasting, document automation, and AI built into the systems you already run.",
   "description": "We help organizations move from AI interest to working AI capability, with clear business cases, secure architectures, and solutions grounded in real business data. Our team designs, builds, and integrates AI into the applications, workflows, and systems your people already depend on.",
   "icon": "fas fa-brain"
  },
  "cybersecurity-excellence": {
   "slug": "cybersecurity-excellence",
   "name": "Cybersecurity Excellence",
   "short_description": "Threat monitoring, penetration testing, endpoint protection, incident response and compliance support that keep your business resilient against cyber risk.",
   "description": "Cybersecurity Excellence brings together the services that protect your data, users and devices beyond the network perimeter, from continuous threat detection and VAPT to endpoint defense and incident response. We help organizations build a measurable security posture and align it with frameworks such as ISO 27001, CERT-In guidelines and the DPDP Act.",
   "icon": "fas fa-user-shield"
  },
  "it-hardware-var": {
   "slug": "it-hardware-var",
   "name": "IT Hardware & VAR",
   "short_description": "End-to-end IT hardware and software sourcing, deployment, licensing and lifecycle support, delivered with the added value of an experienced reseller.",
   "description": "As a value added reseller, TM Solutech helps organizations source the right hardware and software, deploy it correctly and keep it supported throughout its working life. We combine product consultation, procurement, installation, warranty management and on-site support so your IT estate is handled by one accountable partner.",
   "icon": "fas fa-boxes-stacked"
  }
 },
 "services": {
  "ai-strategy-consulting": {
   "slug": "ai-strategy-consulting",
   "title": "AI Strategy & Consulting",
   "icon": "fas fa-lightbulb",
   "short_description": "AI readiness assessments, use-case prioritization, and practical adoption roadmaps that connect AI investment to measurable business outcomes.",
   "description": "<p>Many organizations know AI matters but are unsure where it will genuinely pay off. We work with your leadership and operational teams to assess data maturity, existing systems, and business priorities, then identify the specific use cases where AI can deliver real, defensible value for your business.</p><p>Our team turns that assessment into a phased roadmap covering architecture, governance, build-versus-buy decisions, and change management. The result is a clear, realiztic plan your stakeholders can approve and your teams can execute, without chasing trends or committing budget to experiments that never reach production.</p>",
   "feature_items": [
    {
     "icon": "fas fa-magnifying-glass-chart",
     "title": "AI Readiness Assessment",
     "text": "A structured review of your data quality, infrastructure, skills, and processes against AI requirements."
    },
    {
     "icon": "fas fa-bullseye",
     "title": "Use-Case Prioritization",
     "text": "Candidate use cases scored on business value, feasibility, data availability, and delivery risk."
    },
    {
     "icon": "fas fa-route",
     "title": "Adoption Roadmap",
     "text": "A phased plan sequencing pilots, platform choices, and scale-up milestones across the business."
    },
    {
     "icon": "fas fa-shield-halved",
     "title": "Governance Framework",
     "text": "Policies for responsible AI use, data privacy, model oversight, and access control from day one."
    }
   ],
   "benefit_items": [
    {
     "title": "Focused Investment",
     "text": "Budget directed to use cases with a clear and defensible business case."
    },
    {
     "title": "Reduced Delivery Risk",
     "text": "Feasibility and data gaps identified before any build work begins."
    },
    {
     "title": "Leadership Alignment",
     "text": "A shared AI vision that business and IT stakeholders can stand behind."
    }
   ],
   "process_items": [
    {
     "title": "Discovery Workshops",
     "text": "Interview stakeholders and map business goals, pain points, and current processes."
    },
    {
     "title": "Readiness Evaluation",
     "text": "Assess data sources, systems, security posture, and team capability for AI adoption."
    },
    {
     "title": "Opportunity Prioritization",
     "text": "Score and shortlist use cases by value, effort, and risk to define pilot candidates."
    },
    {
     "title": "Roadmap & Handover",
     "text": "Deliver a phased roadmap, governance model, and business case for executive approval."
    }
   ],
   "faq_items": [
    {
     "question": "Do we need clean, well-organized data before engaging on AI strategy?",
     "answer": "No. Assessing your data landscape is part of the engagement, and our roadmap includes the data preparation steps needed before each use case moves forward."
    },
    {
     "question": "Is the strategy tied to a specific AI vendor or platform?",
     "answer": "Our recommendations are vendor-neutral. We evaluate platforms such as OpenAI, Azure OpenAI, and open-source models against your requirements for cost, security, and control."
    }
   ],
   "meta_title": "AI Strategy & Consulting | TM Solutech",
   "meta_description": "AI readiness assessments, use-case prioritization, and practical adoption roadmaps from TM Solutech that connect AI investment to real business outcomes."
  },
  "custom-ai-copilot-development": {
   "slug": "custom-ai-copilot-development",
   "title": "Custom AI Copilot Development",
   "icon": "fas fa-robot",
   "short_description": "Secure AI assistants trained on your own documents and data, helping employees and customers find answers, draft content, and complete tasks faster.",
   "description": "<p>Generic chatbots rarely understand your products, policies, or internal processes. We build custom AI copilots grounded in your own knowledge base, using retrieval-augmented generation to deliver accurate, source-referenced answers drawn from your documents, wikis, and business systems.</p><p>Our team designs each copilot around a specific role, whether that is customer support, sales enablement, HR queries, or technical documentation. We build in role-based access, conversation logging, and guardrails, and deploy the copilot where your people already work: your website, intranet, Microsoft Teams, or the internal applications your teams use every day.</p>",
   "feature_items": [
    {
     "icon": "fas fa-database",
     "title": "Knowledge Base Grounding",
     "text": "Retrieval-augmented generation that answers from your approved documents and cites its sources."
    },
    {
     "icon": "fas fa-lock",
     "title": "Role-Based Access",
     "text": "Users only receive answers drawn from content they are already authorized to view."
    },
    {
     "icon": "fas fa-comments",
     "title": "Multi-Channel Deployment",
     "text": "Copilots delivered through web chat, Microsoft Teams, intranet portals, or embedded app widgets."
    },
    {
     "icon": "fas fa-sliders",
     "title": "Configurable Guardrails",
     "text": "Topic restrictions, tone controls, and fallback rules that keep responses on-brand and on-policy."
    }
   ],
   "benefit_items": [
    {
     "title": "Faster Answers",
     "text": "Staff and customers find information in seconds instead of searching manually."
    },
    {
     "title": "Consistent Responses",
     "text": "Every answer draws on the same approved, up-to-date source material."
    },
    {
     "title": "Lower Support Load",
     "text": "Routine queries are resolved without pulling skilled staff away from core work."
    }
   ],
   "process_items": [
    {
     "title": "Use-Case Definition",
     "text": "Define the copilot's audience, tasks, knowledge sources, and success criteria with your team."
    },
    {
     "title": "Knowledge Preparation",
     "text": "Collect, clean, and index your documents and data sources for accurate retrieval."
    },
    {
     "title": "Build & Evaluate",
     "text": "Develop the copilot and test responses against real questions for accuracy and safety."
    },
    {
     "title": "Deploy & Refine",
     "text": "Launch in your chosen channels and improve answers using feedback and usage insights."
    }
   ],
   "faq_items": [
    {
     "question": "Will our confidential documents be used to train public AI models?",
     "answer": "No. We design copilots so your data is retrieved at query time and not used to train public models, and we can deploy on enterprise services such as Azure OpenAI or self-hosted models where required."
    },
    {
     "question": "How do you prevent the copilot from giving incorrect answers?",
     "answer": "Responses are grounded in your indexed content with source references, and guardrails instruct the copilot to decline or escalate when it cannot find a reliable answer."
    }
   ],
   "meta_title": "Custom AI Copilot Development | TM Solutech",
   "meta_description": "TM Solutech builds secure custom AI copilots grounded in your own documents and data, deployed on your website, intranet, Microsoft Teams, or applications."
  },
  "predictive-analytics-forecasting": {
   "slug": "predictive-analytics-forecasting",
   "title": "Predictive Analytics & Forecasting",
   "icon": "fas fa-chart-line",
   "short_description": "Machine learning models that forecast demand, sales, inventory, and risk from your historical data, giving teams earlier and better-informed decisions.",
   "description": "<p>Most organizations already hold years of valuable operational data, yet decisions are still driven by spreadsheets and instinct. We build machine learning models that learn from your historical sales, inventory, financial, and operational data to forecast what is likely to happen next.</p><p>Our team handles the full pipeline, from data preparation and feature engineering to model training, validation, and deployment. Forecasts are delivered into the tools your teams already use, such as Power BI dashboards or your ERP, and models are monitored and retrained so accuracy holds up as business conditions change.</p>",
   "feature_items": [
    {
     "icon": "fas fa-chart-column",
     "title": "Demand Forecasting",
     "text": "Models that project product, regional, and seasonal demand to guide purchasing and production."
    },
    {
     "icon": "fas fa-eye",
     "title": "Anomaly Detection",
     "text": "Automated alerts when transactions, costs, or operational metrics move outside expected patterns."
    },
    {
     "icon": "fas fa-users",
     "title": "Customer Behavior Models",
     "text": "Churn risk, purchase propensity, and segmentation models that sharpen sales and retention efforts."
    },
    {
     "icon": "fas fa-chart-pie",
     "title": "Dashboard Integration",
     "text": "Forecasts and model outputs surfaced in Power BI or your existing reporting and ERP screens."
    }
   ],
   "benefit_items": [
    {
     "title": "Earlier Decisions",
     "text": "Teams act on likely outcomes rather than reacting after the fact."
    },
    {
     "title": "Leaner Inventory",
     "text": "Better demand visibility helps reduce both stock-outs and excess stock."
    },
    {
     "title": "Data-Backed Planning",
     "text": "Budgets and targets grounded in evidence drawn from your own history."
    }
   ],
   "process_items": [
    {
     "title": "Data Assessment",
     "text": "Review available historical data, its quality, and the business questions to be answered."
    },
    {
     "title": "Data Engineering",
     "text": "Clean, combine, and structure data from multiple sources into a reliable modeling dataset."
    },
    {
     "title": "Model Development",
     "text": "Train and validate forecasting models, comparing approaches to select the best performer."
    },
    {
     "title": "Deploy & Monitor",
     "text": "Integrate forecasts into business tools and track accuracy with scheduled retraining."
    }
   ],
   "faq_items": [
    {
     "question": "How much historical data do we need for accurate forecasting?",
     "answer": "It depends on the use case and seasonality, but we assess your data during the first phase and give a realiztic view of achievable accuracy before any model build begins."
    },
    {
     "question": "Can forecasts appear inside our existing dashboards?",
     "answer": "Yes. We deliver model outputs into Power BI, your ERP, or other reporting tools so teams can use forecasts without learning a new system."
    }
   ],
   "meta_title": "Predictive Analytics & Forecasting | TM Solutech",
   "meta_description": "Machine learning forecasting for demand, sales, inventory, and risk from TM Solutech, delivered into Power BI dashboards and the ERP systems you use."
  },
  "ai-powered-mobile-app-intelligence": {
   "slug": "ai-powered-mobile-app-intelligence",
   "title": "AI-Powered Mobile App Intelligence",
   "icon": "fas fa-mobile-screen-button",
   "short_description": "Smart features for Android and iOS apps, including personalized recommendations, conversational assistants, image recognition, and voice interaction.",
   "description": "<p>Users now expect mobile apps to understand context and anticipate needs. We add AI capabilities to new and existing Android and iOS applications, including personalized recommendations, in-app conversational assistants, image and document recognition, and voice-driven interaction for everyday tasks.</p><p>Our team selects the right balance between on-device and cloud processing for each feature, weighing speed, cost, offline availability, and data privacy. We integrate AI cleanly into your app architecture and backend APIs, so new intelligence improves the user experience without slowing performance or compromising the security of your users' personal data.</p>",
   "feature_items": [
    {
     "icon": "fas fa-wand-magic-sparkles",
     "title": "Personalized Recommendations",
     "text": "Content, product, and action suggestions tailored to each user's behavior and preferences."
    },
    {
     "icon": "fas fa-comments",
     "title": "In-App AI Assistants",
     "text": "Conversational help that answers questions and guides users through tasks inside the app."
    },
    {
     "icon": "fas fa-camera",
     "title": "Image & Document Recognition",
     "text": "Camera-based scanning that reads documents, identifies products, and captures data automatically."
    },
    {
     "icon": "fas fa-microchip",
     "title": "On-Device Processing",
     "text": "Lightweight models running locally for faster responses, offline use, and stronger data privacy."
    }
   ],
   "benefit_items": [
    {
     "title": "Higher Engagement",
     "text": "Relevant, personalized experiences give users reasons to keep returning."
    },
    {
     "title": "Faster Task Completion",
     "text": "Smart input and guidance reduce manual steps for every mobile user."
    },
    {
     "title": "Privacy by Design",
     "text": "Sensitive processing kept on-device wherever the use case allows it."
    }
   ],
   "process_items": [
    {
     "title": "App & User Review",
     "text": "Analyze your app, user journeys, and data to pinpoint high-value AI opportunities."
    },
    {
     "title": "Feature Design",
     "text": "Define AI features, choose on-device or cloud models, and plan the integration approach."
    },
    {
     "title": "Build & Integrate",
     "text": "Develop AI features within your app and backend APIs, testing on real devices throughout."
    },
    {
     "title": "Release & Optimize",
     "text": "Roll out through app stores and refine models using real usage and performance data."
    }
   ],
   "faq_items": [
    {
     "question": "Can you add AI features to an app that is already live?",
     "answer": "Yes. We work with existing Android, iOS, and cross-platform codebases and introduce AI features incrementally without disrupting your current users."
    },
    {
     "question": "Will AI features increase app size or slow it down?",
     "answer": "We choose model sizes and processing locations carefully, using cloud inference for heavier tasks and compact on-device models where responsiveness matters most."
    }
   ],
   "meta_title": "AI-Powered Mobile App Intelligence | TM Solutech",
   "meta_description": "TM Solutech adds AI to Android and iOS apps, including personalized recommendations, in-app assistants, image recognition, and secure on-device processing."
  },
  "intelligent-data-processing": {
   "slug": "intelligent-data-processing",
   "title": "Intelligent Data Processing",
   "icon": "fas fa-file-lines",
   "short_description": "AI-driven extraction, classification, and validation of invoices, forms, contracts, and emails, replacing slow manual data entry with automated workflows.",
   "description": "<p>Invoices, purchase orders, contracts, and customer emails still consume hours of manual data entry in most organizations. We build intelligent document processing solutions that combine OCR with AI language models to read, classify, and extract structured data from documents in a wide range of formats and layouts.</p><p>Our team adds validation rules and confidence scoring, so uncertain items are routed to a person for review rather than passed through unchecked. Extracted data flows directly into your ERP, CRM, or databases, turning a slow, error-prone process into a dependable and auditable workflow.</p>",
   "feature_items": [
    {
     "icon": "fas fa-magnifying-glass",
     "title": "Smart Data Extraction",
     "text": "OCR and AI models that capture key fields from invoices, forms, receipts, and contracts."
    },
    {
     "icon": "fas fa-layer-group",
     "title": "Document Classification",
     "text": "Incoming documents and emails sorted automatically by type, priority, and department."
    },
    {
     "icon": "fas fa-list-check",
     "title": "Validation & Review Queues",
     "text": "Business rules and confidence scores that route uncertain items to human reviewers."
    },
    {
     "icon": "fas fa-arrows-rotate",
     "title": "System Synchronization",
     "text": "Verified data pushed straight into your ERP, CRM, accounting software, or databases."
    }
   ],
   "benefit_items": [
    {
     "title": "Less Manual Entry",
     "text": "Teams spend their time on exceptions instead of retyping documents."
    },
    {
     "title": "Fewer Data Errors",
     "text": "Automated validation catches mismatches before they reach core systems."
    },
    {
     "title": "Full Audit Trail",
     "text": "Every document, extraction, and approval is logged and traceable."
    }
   ],
   "process_items": [
    {
     "title": "Document Discovery",
     "text": "Catalog document types, volumes, formats, and the downstream systems they feed."
    },
    {
     "title": "Pipeline Design",
     "text": "Define extraction fields, validation rules, review thresholds, and integration points."
    },
    {
     "title": "Build & Train",
     "text": "Configure extraction models and test them against your real sample documents for accuracy."
    },
    {
     "title": "Go-Live & Tuning",
     "text": "Deploy into production and refine accuracy using reviewer corrections over time."
    }
   ],
   "faq_items": [
    {
     "question": "Can the solution handle scanned and handwritten documents?",
     "answer": "Scanned documents are well supported, and clearly written handwriting can often be processed; we test with your actual samples to confirm accuracy before go-live."
    },
    {
     "question": "What happens when the AI is unsure about a value?",
     "answer": "Low-confidence fields are flagged and sent to a review queue, so a team member verifies them before the data enters your systems."
    }
   ],
   "meta_title": "Intelligent Data Processing | TM Solutech",
   "meta_description": "AI-driven document processing from TM Solutech that extracts, classifies, and validates invoices, forms, and contracts, then feeds your ERP or CRM."
  },
  "ai-integration-existing-systems": {
   "slug": "ai-integration-existing-systems",
   "title": "Integration with Existing Systems",
   "icon": "fas fa-plug",
   "short_description": "AI capabilities embedded into your existing ERP, CRM, and legacy applications through secure APIs, so teams gain intelligence without replacing core systems.",
   "description": "<p>Replacing core business systems to adopt AI is rarely practical or necessary. We connect AI capabilities directly to your existing ERP, CRM, and legacy applications through secure APIs and middleware, adding features such as smart search, automated summaries, intelligent recommendations, and natural-language reporting.</p><p>Our team maps your current architecture, data flows, and security requirements before designing the integration layer. We prioritize stability, access control, and clear audit logging, so AI features enhance the systems your people already know while your existing business processes and data remain protected and fully under your control throughout.</p>",
   "feature_items": [
    {
     "icon": "fas fa-diagram-project",
     "title": "Integration Architecture",
     "text": "API and middleware layers that connect AI services safely to ERP, CRM, and legacy platforms."
    },
    {
     "icon": "fas fa-server",
     "title": "Legacy System Enablement",
     "text": "Adapters and connectors that bring AI features to older applications without risky rewrites."
    },
    {
     "icon": "fas fa-gears",
     "title": "Workflow Automation",
     "text": "AI-assisted steps added to approvals, ticket routing, and data updates across connected systems."
    },
    {
     "icon": "fas fa-shield-halved",
     "title": "Secure Data Handling",
     "text": "Access controls, data masking, and audit logging applied to every AI interaction and request."
    }
   ],
   "benefit_items": [
    {
     "title": "Protected Investment",
     "text": "Gain AI capability while keeping the core systems you rely on today."
    },
    {
     "title": "Familiar Interfaces",
     "text": "Users access new features inside tools they already know well."
    },
    {
     "title": "Controlled Rollout",
     "text": "Phased integration keeps business operations stable throughout."
    }
   ],
   "process_items": [
    {
     "title": "Systems Mapping",
     "text": "Document your applications, data flows, APIs, and security constraints in detail."
    },
    {
     "title": "Integration Design",
     "text": "Define AI features, connection methods, data boundaries, and fallback behavior."
    },
    {
     "title": "Build & Test",
     "text": "Develop connectors and AI services, testing in a staging environment before release."
    },
    {
     "title": "Phased Rollout",
     "text": "Release features to user groups in stages, with monitoring and support at each step."
    }
   ],
   "faq_items": [
    {
     "question": "Our ERP is old and has limited APIs. Can it still be integrated with AI?",
     "answer": "Often, yes. We can work through database-level connectors, middleware, or file-based exchanges where modern APIs are not available, after assessing what your system safely supports."
    },
    {
     "question": "Will integrating AI disrupt our day-to-day operations?",
     "answer": "We build and test in a staging environment first and release in phases, so core business processes continue running normally throughout the project."
    }
   ],
   "meta_title": "AI Integration with Existing Systems | TM Solutech",
   "meta_description": "TM Solutech embeds AI into your existing ERP, CRM, and legacy applications through secure APIs, adding intelligence without replacing core systems."
  },
  "threat-monitoring-detection": {
   "slug": "threat-monitoring-detection",
   "title": "Threat Monitoring & Detection",
   "icon": "fas fa-satellite-dish",
   "short_description": "Continuous monitoring of logs, endpoints and cloud activity to detect suspicious behavior early and escalate real threats before they become breaches.",
   "description": "<p>Most attacks leave traces long before they cause damage. Our team sets up centralized log collection and correlation across your servers, endpoints, cloud workloads and business applications, so suspicious activity is spotted while there is still time to act. We tune detection rules to your environment to reduce noise and focus attention on genuine risk.</p><p>Every alert is triaged against context such as user behavior, asset criticality and known threat intelligence. Confirmed incidents are escalated with clear evidence and recommended actions, and we share regular reports so your leadership can see how your security posture is improving over time.</p>",
   "feature_items": [
    {
     "icon": "fas fa-eye",
     "title": "Centralized Log Monitoring",
     "text": "SIEM-based collection and correlation of logs from servers, endpoints, firewalls and cloud services."
    },
    {
     "icon": "fas fa-bell",
     "title": "Prioritized Alerting",
     "text": "Detection rules tuned to your environment so analysts act on real threats, not background noise."
    },
    {
     "icon": "fas fa-user-secret",
     "title": "Threat Intelligence",
     "text": "Alerts enriched with known indicators of compromise and attacker techniques mapped to MITRE ATT&CK."
    },
    {
     "icon": "fas fa-chart-line",
     "title": "Posture Reporting",
     "text": "Regular dashboards and reports on alerts, trends and open risks for IT and leadership teams."
    }
   ],
   "benefit_items": [
    {
     "title": "Earlier Detection",
     "text": "Spot intrusions and misuse while they are still contained and recoverable."
    },
    {
     "title": "Less Alert Fatigue",
     "text": "Tuned rules and triage keep your team focused on threats that matter."
    },
    {
     "title": "Audit-Ready Logs",
     "text": "Retained, searchable logs that support investigations and compliance reviews."
    }
   ],
   "process_items": [
    {
     "title": "Environment Assessment",
     "text": "Identify critical assets, log sources and the threats most relevant to your business."
    },
    {
     "title": "Platform Onboarding",
     "text": "Connect log sources to the monitoring platform and validate data quality and coverage."
    },
    {
     "title": "Rule Tuning",
     "text": "Build and refine detection use cases to cut false positives and close visibility gaps."
    },
    {
     "title": "Ongoing Monitoring",
     "text": "Triage alerts, escalate confirmed incidents and review detection performance regularly."
    }
   ],
   "faq_items": [
    {
     "question": "Do we need to replace our existing security tools?",
     "answer": "Usually not. We integrate logs from the firewalls, antivirus and cloud services you already run, and recommend additions only where there are clear visibility gaps."
    },
    {
     "question": "Can monitoring help with CERT-In incident reporting?",
     "answer": "Yes. Centralized, time-synchronized logs and documented escalations make it easier to meet CERT-In reporting and log retention expectations."
    }
   ],
   "meta_title": "Threat Monitoring & Detection | TM Solutech",
   "meta_description": "SIEM-based threat monitoring and detection from TM Solutech. Centralized logging, tuned alerts and clear escalation to catch attacks early."
  },
  "vulnerability-assessment-penetration-testing": {
   "slug": "vulnerability-assessment-penetration-testing",
   "title": "Vulnerability Assessment & Penetration Testing (VAPT)",
   "icon": "fas fa-bug",
   "short_description": "Structured vulnerability scanning and manual penetration testing of networks, web apps and APIs, with prioritized findings and practical remediation guidance.",
   "description": "<p>Attackers look for the weakest point in your systems, so we look for it first. Our team combines automated vulnerability scanning with manual penetration testing across your external and internal networks, web applications, APIs and cloud configurations. Testing follows recognized methodologies such as the OWASP Top 10 and is carried out within an agreed scope and schedule.</p><p>We do not just hand over a scanner report. Each finding is validated, rated by business risk and paired with clear remediation steps your developers and IT team can act on. Once fixes are in place, we retest to confirm the gaps are genuinely closed.</p>",
   "feature_items": [
    {
     "icon": "fas fa-magnifying-glass",
     "title": "Vulnerability Scanning",
     "text": "Authenticated and external scans that find missing patches, weak configurations and exposed services."
    },
    {
     "icon": "fas fa-crosshairs",
     "title": "Manual Penetration Testing",
     "text": "Hands-on testing that chains weaknesses together to show how a real attacker could gain access."
    },
    {
     "icon": "fas fa-laptop-code",
     "title": "Web & API Testing",
     "text": "Application testing aligned with the OWASP Top 10, covering authentication, injection and access control."
    },
    {
     "icon": "fas fa-list-check",
     "title": "Remediation & Retesting",
     "text": "Risk-rated findings with fix guidance, followed by retesting to confirm each issue is resolved."
    }
   ],
   "benefit_items": [
    {
     "title": "Known Risk Exposure",
     "text": "See exactly where your systems are vulnerable before attackers do."
    },
    {
     "title": "Focused Remediation",
     "text": "Risk-based ratings help you fix the most critical issues first."
    },
    {
     "title": "Compliance Evidence",
     "text": "Documented test reports support audits, client reviews and tenders."
    }
   ],
   "process_items": [
    {
     "title": "Scoping & Authorization",
     "text": "Agree targets, test windows, rules of engagement and written authorization upfront."
    },
    {
     "title": "Discovery & Scanning",
     "text": "Map the attack surface and run vulnerability scans across all in-scope assets."
    },
    {
     "title": "Exploitation & Validation",
     "text": "Manually verify findings and safely demonstrate impact without disrupting operations."
    },
    {
     "title": "Reporting & Retest",
     "text": "Deliver executive and technical reports, then retest once remediation is complete."
    }
   ],
   "faq_items": [
    {
     "question": "Will penetration testing disrupt our live systems?",
     "answer": "Testing is planned with your team, run in agreed windows and avoids destructive techniques, so business operations continue normally."
    },
    {
     "question": "How often should we run VAPT?",
     "answer": "We recommend at least once a year and after any major change, such as a new application release, infrastructure migration or merger."
    }
   ],
   "meta_title": "VAPT Services | TM Solutech",
   "meta_description": "Vulnerability assessment and penetration testing for networks, web apps and APIs. Validated findings, clear remediation and retesting by TM Solutech."
  },
  "endpoint-security": {
   "slug": "endpoint-security",
   "title": "Endpoint Security (Device Protection)",
   "icon": "fas fa-laptop",
   "short_description": "Protect laptops, desktops, servers and mobile devices with EDR/XDR, device encryption, patch management and central policy control across every location.",
   "description": "<p>Every laptop, desktop, server and mobile device is a potential entry point, especially with hybrid and remote working. Our team deploys and manages modern endpoint protection that goes beyond traditional antivirus, using EDR/XDR capabilities to detect malicious behavior, isolate compromised devices and stop ransomware before it spreads.</p><p>We combine this with disk encryption, patch management, application control and mobile device management, all governed from a central console. Policies are designed around how your people actually work, so protection stays consistently strong without slowing users down or overloading your IT team.</p>",
   "feature_items": [
    {
     "icon": "fas fa-shield-virus",
     "title": "EDR/XDR Protection",
     "text": "Behavior-based detection that identifies ransomware, fileless malware and suspicious processes in real time."
    },
    {
     "icon": "fas fa-lock",
     "title": "Device Encryption",
     "text": "Full-disk encryption and secure configuration so lost or stolen devices do not expose company data."
    },
    {
     "icon": "fas fa-arrows-rotate",
     "title": "Patch Management",
     "text": "Automated operating system and application updates to close known vulnerabilities on schedule."
    },
    {
     "icon": "fas fa-mobile-screen",
     "title": "Mobile Device Management",
     "text": "Central enrolment, policy enforcement and remote wipe for company and BYOD smartphones and tablets."
    }
   ],
   "benefit_items": [
    {
     "title": "Ransomware Resilience",
     "text": "Detect and isolate infected devices before threats spread across the network."
    },
    {
     "title": "Secure Remote Work",
     "text": "Consistent protection for users in the office, at home or travelling."
    },
    {
     "title": "Central Visibility",
     "text": "One console to see device health, threats and compliance status."
    }
   ],
   "process_items": [
    {
     "title": "Device Inventory",
     "text": "Discover all endpoints and assess current protection, patch levels and configuration gaps."
    },
    {
     "title": "Policy Design",
     "text": "Define protection, encryption and access policies suited to each user group and device type."
    },
    {
     "title": "Phased Rollout",
     "text": "Deploy agents in controlled waves, validating compatibility with business applications."
    },
    {
     "title": "Managed Operations",
     "text": "Monitor alerts, maintain patches and review policies as your device estate evolves."
    }
   ],
   "faq_items": [
    {
     "question": "Is EDR different from traditional antivirus?",
     "answer": "Yes. Antivirus mainly matches known malware signatures, while EDR monitors behavior on the device and can detect, investigate and contain previously unseen attacks."
    },
    {
     "question": "Can you secure employee-owned devices?",
     "answer": "Yes. With mobile device management we can separate and protect company data on personal devices without accessing the user's private content."
    }
   ],
   "meta_title": "Endpoint Security & EDR | TM Solutech",
   "meta_description": "Endpoint security with EDR/XDR, encryption, patch management and MDM. TM Solutech protects laptops, servers and mobile devices across your business."
  },
  "incident-response-recovery": {
   "slug": "incident-response-recovery",
   "title": "Incident Response & Recovery",
   "icon": "fas fa-truck-medical",
   "short_description": "Structured incident response that contains attacks quickly, investigates root cause and restores systems and data safely so your business can resume operations.",
   "description": "<p>When a security incident strikes, speed and clarity matter more than anything. Our team helps you contain the threat, preserve evidence and understand exactly what happened, whether it is ransomware, a compromised account or a data leak. We work alongside your IT staff and management to keep decisions clear and communication controlled.</p><p>Once the threat is removed, we restore systems and data from clean backups, harden the weaknesses that were exploited and document lessons learned. We can also prepare response plans and run tabletop exercises in advance, so your organization knows its roles before an incident occurs.</p>",
   "feature_items": [
    {
     "icon": "fas fa-triangle-exclamation",
     "title": "Rapid Containment",
     "text": "Isolate affected systems and accounts quickly to stop an attack from spreading further."
    },
    {
     "icon": "fas fa-fingerprint",
     "title": "Forensic Investigation",
     "text": "Evidence collection and analysis to establish root cause, timeline and scope of the compromise."
    },
    {
     "icon": "fas fa-database",
     "title": "Clean Recovery",
     "text": "Restore systems and data from verified backups and rebuild compromised hosts securely."
    },
    {
     "icon": "fas fa-book",
     "title": "Response Playbooks",
     "text": "Incident response plans, escalation matrices and tabletop exercises prepared before you need them."
    }
   ],
   "benefit_items": [
    {
     "title": "Reduced Downtime",
     "text": "Structured response gets critical systems back online faster."
    },
    {
     "title": "Clear Root Cause",
     "text": "Understand how the attack happened so it does not happen again."
    },
    {
     "title": "Reporting Support",
     "text": "Documentation that helps meet CERT-In and regulatory reporting duties."
    }
   ],
   "process_items": [
    {
     "title": "Triage & Containment",
     "text": "Assess the incident, isolate affected assets and preserve evidence for investigation."
    },
    {
     "title": "Investigation",
     "text": "Analyze logs, endpoints and accounts to determine root cause, scope and data impact."
    },
    {
     "title": "Eradication & Recovery",
     "text": "Remove attacker access, restore from clean backups and verify systems before reconnecting."
    },
    {
     "title": "Post-Incident Review",
     "text": "Document findings, close exploited gaps and update response plans with lessons learned."
    }
   ],
   "faq_items": [
    {
     "question": "Should we pay the ransom in a ransomware attack?",
     "answer": "We advise against making that decision under pressure. Our first priority is containment and assessing whether clean backups allow recovery without engaging the attackers."
    },
    {
     "question": "Can you help before an incident happens?",
     "answer": "Yes. We prepare incident response plans, review backup readiness and run tabletop exercises so your team knows exactly what to do."
    }
   ],
   "meta_title": "Incident Response & Recovery | TM Solutech",
   "meta_description": "Cyber incident response from TM Solutech: rapid containment, forensic investigation, clean recovery and response planning for ransomware and breaches."
  },
  "security-policy-compliance-support": {
   "slug": "security-policy-compliance-support",
   "title": "Security Policy & Compliance Support",
   "icon": "fas fa-clipboard-check",
   "short_description": "Practical security policies, gap assessments and audit preparation aligned with ISO 27001, CERT-In guidelines and the DPDP Act, tailored to how your business works.",
   "description": "<p>Strong security depends on clear rules that people actually follow. Our team helps you define and document information security policies, access controls, data handling and acceptable use standards that fit your organization's size and risk profile. We map these against frameworks such as ISO 27001, CERT-In guidelines and the Digital Personal Data Protection (DPDP) Act.</p><p>We run gap assessments, build practical remediation roadmaps and help you prepare evidence for internal and external audits. Alongside documentation, we support security awareness training so policies become everyday habits rather than files that sit unread.</p>",
   "feature_items": [
    {
     "icon": "fas fa-scale-balanced",
     "title": "Gap Assessment",
     "text": "Review current controls against ISO 27001, CERT-In and DPDP Act requirements to identify gaps."
    },
    {
     "icon": "fas fa-file-contract",
     "title": "Policy Development",
     "text": "Clear, practical security policies and procedures written for your organization, not generic templates."
    },
    {
     "icon": "fas fa-gavel",
     "title": "Audit Preparation",
     "text": "Evidence collection, control documentation and readiness reviews ahead of audits and client assessments."
    },
    {
     "icon": "fas fa-graduation-cap",
     "title": "Awareness Training",
     "text": "Security awareness sessions that help employees recognize phishing, social engineering and data risks."
    }
   ],
   "benefit_items": [
    {
     "title": "Regulatory Readiness",
     "text": "Stay prepared for evolving Indian data protection and cyber rules."
    },
    {
     "title": "Smoother Audits",
     "text": "Organized evidence and documented controls reduce audit effort."
    },
    {
     "title": "Customer Confidence",
     "text": "Demonstrate mature security practices to clients and partners."
    }
   ],
   "process_items": [
    {
     "title": "Current State Review",
     "text": "Understand your business, data flows, existing controls and applicable compliance obligations."
    },
    {
     "title": "Gap Analysis",
     "text": "Compare current practices against chosen frameworks and rate each gap by business risk."
    },
    {
     "title": "Roadmap & Policies",
     "text": "Deliver prioritized remediation plans along with tailored policies and procedures."
    },
    {
     "title": "Implementation Support",
     "text": "Assist with control rollout, staff training and audit readiness reviews over time."
    }
   ],
   "faq_items": [
    {
     "question": "Does the DPDP Act apply to our business?",
     "answer": "If you collect or process digital personal data of individuals in India, it very likely does. We help you assess your obligations and the controls needed to meet them."
    },
    {
     "question": "Can you help us prepare for ISO 27001 certification?",
     "answer": "Yes. We support gap assessment, policy development and audit readiness, while the certification audit itself is carried out by an accredited certification body."
    }
   ],
   "meta_title": "Security Policy & Compliance Support | TM Solutech",
   "meta_description": "Security policy and compliance support aligned with ISO 27001, CERT-In guidelines and the DPDP Act. Gap assessments, policies and audit readiness."
  },
  "hardware-procurement": {
   "slug": "hardware-procurement",
   "title": "Hardware Procurement",
   "icon": "fas fa-cart-shopping",
   "short_description": "Sourcing of servers, laptops, desktops, printers, firewalls and networking gear from leading OEMs, matched to your specifications and budget.",
   "description": "<p>We handle the full procurement cycle for business IT hardware, from servers, desktops and laptops to printers, storage, firewalls and networking equipment from leading OEMs such as Dell, HP and Lenovo. Our team translates your technical and commercial requirements into clear, comparable quotations so you can buy with confidence.</p><p>Beyond price, we focus on the right configuration, genuine products, correct warranty terms and coordinated delivery to one or many locations. Whether you are equipping a new office, running a refresh program or replacing a single critical device, we keep the process transparent, documented and aligned with your internal approval workflows.</p>",
   "feature_items": [
    {
     "icon": "fas fa-server",
     "title": "Broad Product Coverage",
     "text": "Servers, storage, end-user devices, printers and networking gear sourced through one point of contact."
    },
    {
     "icon": "fas fa-file-invoice",
     "title": "Clear Comparable Quotations",
     "text": "Itemized quotes with configurations, warranty terms and options laid out for easy internal approval."
    },
    {
     "icon": "fas fa-microchip",
     "title": "Specification Matching",
     "text": "Each device is configured around your workloads, users and standards rather than generic catalog builds."
    },
    {
     "icon": "fas fa-truck-fast",
     "title": "Coordinated Delivery",
     "text": "Shipments planned and tracked to your offices, branches or data center, with documentation at every step."
    }
   ],
   "benefit_items": [
    {
     "title": "Single Accountable Partner",
     "text": "One team manages sourcing, paperwork and delivery across all your hardware."
    },
    {
     "title": "Right-Sized Spend",
     "text": "Configurations matched to need, avoiding both under-buying and over-specification."
    },
    {
     "title": "Genuine Products",
     "text": "Hardware sourced through proper channels with valid manufacturer warranty."
    }
   ],
   "process_items": [
    {
     "title": "Requirement Gathering",
     "text": "Capture device types, quantities, specifications, locations and timelines with your team."
    },
    {
     "title": "Quotation & Options",
     "text": "Share itemized quotations with configuration choices and warranty options for review."
    },
    {
     "title": "Order & Fulfilment",
     "text": "Place orders on approval, track shipments and coordinate delivery windows with each site."
    },
    {
     "title": "Handover & Records",
     "text": "Hand over equipment with invoices, serial numbers and warranty details for your asset register."
    }
   ],
   "faq_items": [
    {
     "question": "Can you procure hardware for multiple office locations?",
     "answer": "Yes. We coordinate orders and deliveries to multiple sites and keep the documentation organized so each location's assets are clearly recorded."
    },
    {
     "question": "Do you only supply one brand?",
     "answer": "No. We source from a range of leading OEMs and recommend the option that best fits your requirements, standards and budget."
    }
   ],
   "meta_title": "Hardware Procurement | TM Solutech",
   "meta_description": "IT hardware procurement from TM Solutech: servers, laptops, printers, firewalls and networking gear sourced, configured and delivered to your sites."
  },
  "software-licensing": {
   "slug": "software-licensing",
   "title": "Software Licensing",
   "icon": "fas fa-key",
   "short_description": "Guidance and procurement for operating system, productivity, security and business software licenses, keeping your organization compliant and cost-aware.",
   "description": "<p>Software licensing is often complex, with different editions, subscription models and usage rules for each product. We help you procure the right licenses for operating systems, productivity suites, security tools, databases and business applications, explaining the options in plain terms so you only pay for what you actually need.</p><p>Our team keeps track of license quantities, entitlements and renewal dates, and helps you plan true-ups as your headcount and infrastructure change. The result is a licensing position that is compliant, well documented and easier to manage, with fewer surprises at renewal time or during an audit.</p>",
   "feature_items": [
    {
     "icon": "fas fa-scale-balanced",
     "title": "Edition & Model Guidance",
     "text": "Clear comparison of perpetual, subscription and per-user or per-device options for each product you need."
    },
    {
     "icon": "fas fa-receipt",
     "title": "License Procurement",
     "text": "Ordering of new licenses, add-ons and upgrades with entitlement records organized for your team."
    },
    {
     "icon": "fas fa-clipboard-list",
     "title": "Entitlement Tracking",
     "text": "A consolidated view of what you own, where it is deployed and when each subscription is due for renewal."
    },
    {
     "icon": "fas fa-shield-halved",
     "title": "Compliance Support",
     "text": "Help aligning actual usage with license terms to reduce the risk of shortfalls during vendor reviews."
    }
   ],
   "benefit_items": [
    {
     "title": "Lower Licensing Waste",
     "text": "Avoid paying for unused seats or editions with features you never use."
    },
    {
     "title": "Audit Readiness",
     "text": "Organized records make it easier to demonstrate compliance when asked."
    },
    {
     "title": "Predictable Renewals",
     "text": "Upcoming renewals are visible early so budgets can be planned in advance."
    }
   ],
   "process_items": [
    {
     "title": "Usage Assessment",
     "text": "Review current software, users and devices to understand what licenses are genuinely required."
    },
    {
     "title": "Option Recommendation",
     "text": "Present suitable editions and licensing models with clear notes on cost and terms."
    },
    {
     "title": "Procurement & Activation",
     "text": "Procure approved licenses and support activation and assignment across your environment."
    },
    {
     "title": "Ongoing Tracking",
     "text": "Maintain entitlement records and flag renewals, true-ups and expiring subscriptions in good time."
    }
   ],
   "faq_items": [
    {
     "question": "Can you help us move from perpetual licenses to subscriptions?",
     "answer": "Yes. We explain the cost and operational differences, then help you plan a transition that suits your budget cycle and existing investments."
    },
    {
     "question": "Do you help if we are unsure whether we are fully licensed?",
     "answer": "We can review your current software usage against your entitlements and highlight any gaps so you can address them proactively."
    }
   ],
   "meta_title": "Software Licensing | TM Solutech",
   "meta_description": "Software licensing guidance and procurement from TM Solutech: right editions, compliant usage, tracked entitlements and planned renewals for your business."
  },
  "installation-configuration": {
   "slug": "installation-configuration",
   "title": "Installation & Configuration",
   "icon": "fas fa-screwdriver-wrench",
   "short_description": "Professional installation and configuration of servers, end-user devices, printers and network equipment so new hardware is productive from day one.",
   "description": "<p>New hardware only delivers value once it is set up correctly. Our engineers install and configure servers, storage, desktops, laptops, printers, firewalls and network devices at your premises, following your standards for naming, security, domain membership and software images.</p><p>We plan each deployment to minimize disruption, whether that means working after hours, staging devices in advance or rolling out in phases across departments. On completion, we test functionality with your users, document the configuration and hand over a clean, working setup that your internal team can confidently manage going forward.</p>",
   "feature_items": [
    {
     "icon": "fas fa-desktop",
     "title": "Device Setup & Imaging",
     "text": "Desktops and laptops prepared with your OS image, applications, policies and user profiles ready to work."
    },
    {
     "icon": "fas fa-hard-drive",
     "title": "Server & Storage Deployment",
     "text": "Rack, cable and configure servers and storage, including RAID, firmware updates and base OS installation."
    },
    {
     "icon": "fas fa-plug",
     "title": "Network & Peripheral Setup",
     "text": "Switches, access points, firewalls and printers configured and integrated into your existing network."
    },
    {
     "icon": "fas fa-list-check",
     "title": "Testing & Documentation",
     "text": "Functional checks with users and a documented record of configurations, credentials handover and settings."
    }
   ],
   "benefit_items": [
    {
     "title": "Faster Time to Value",
     "text": "Equipment is ready for productive use as soon as it is handed over."
    },
    {
     "title": "Consistent Standards",
     "text": "Every device follows the same configuration rules and security baseline."
    },
    {
     "title": "Minimal Disruption",
     "text": "Planned rollouts reduce downtime for users and business operations."
    }
   ],
   "process_items": [
    {
     "title": "Site & Scope Review",
     "text": "Confirm devices, locations, configuration standards and any constraints on working hours."
    },
    {
     "title": "Staging & Preparation",
     "text": "Prepare images, firmware and configurations in advance to shorten time spent on site."
    },
    {
     "title": "On-Site Deployment",
     "text": "Install, connect and configure equipment, integrating it with your network and directory."
    },
    {
     "title": "Validation & Handover",
     "text": "Test with users, resolve any issues and hand over configuration documentation to your team."
    }
   ],
   "faq_items": [
    {
     "question": "Can you install hardware that was not purchased through you?",
     "answer": "Yes. We can install and configure equipment sourced elsewhere, subject to a quick review of the devices and your requirements."
    },
    {
     "question": "Can deployments be scheduled outside office hours?",
     "answer": "Yes. We can plan installations after hours or on weekends where needed to keep disruption to your teams to a minimum."
    }
   ],
   "meta_title": "Installation & Configuration | TM Solutech",
   "meta_description": "Hardware installation and configuration by TM Solutech: servers, desktops, printers and network devices set up to your standards, ready to use."
  },
  "warranty-renewal-management": {
   "slug": "warranty-renewal-management",
   "title": "Warranty & Renewal Management",
   "icon": "fas fa-calendar-check",
   "short_description": "Tracking and renewal of hardware warranties, support contracts and software subscriptions so critical assets never fall out of coverage unnoticed.",
   "description": "<p>Expired warranties and lapsed subscriptions often go unnoticed until something fails. We maintain a clear record of warranty periods, extended support contracts and software subscription dates across your hardware and software estate, giving you visibility of what is covered and what is approaching expiry.</p><p>Our team alerts you well ahead of each renewal, shares options for extending or upgrading coverage, and handles the paperwork once you decide. Where devices are nearing end of life, we help you weigh the cost of extended support against replacement, so renewal decisions are made deliberately rather than under pressure.</p>",
   "feature_items": [
    {
     "icon": "fas fa-clipboard-list",
     "title": "Coverage Register",
     "text": "A consolidated record of warranty, support and subscription dates mapped to each asset and location."
    },
    {
     "icon": "fas fa-bell",
     "title": "Advance Renewal Alerts",
     "text": "Timely reminders before expiry so there is enough time for budgeting, approvals and processing."
    },
    {
     "icon": "fas fa-file-signature",
     "title": "Renewal Processing",
     "text": "Quotations, orders and documentation for warranty extensions and contract renewals handled for you."
    },
    {
     "icon": "fas fa-scale-balanced",
     "title": "Renew or Replace Advice",
     "text": "Practical guidance on whether extending support or refreshing ageing equipment makes more sense."
    }
   ],
   "benefit_items": [
    {
     "title": "No Coverage Gaps",
     "text": "Critical servers and devices stay under valid warranty or support."
    },
    {
     "title": "Better Budget Planning",
     "text": "Upcoming renewals are known early and can be planned into budgets."
    },
    {
     "title": "Less Admin Burden",
     "text": "Your team no longer needs to chase dates, quotes and contract paperwork."
    }
   ],
   "process_items": [
    {
     "title": "Asset & Contract Audit",
     "text": "Collect serial numbers, warranty terms and subscription details across your hardware and software."
    },
    {
     "title": "Register Setup",
     "text": "Build a coverage register showing status, expiry dates and owners for each asset or contract."
    },
    {
     "title": "Proactive Alerts",
     "text": "Notify you ahead of upcoming expiries with renewal options and indicative costs for review."
    },
    {
     "title": "Renewal Execution",
     "text": "Process approved renewals, update the register and file confirmations for your records."
    }
   ],
   "faq_items": [
    {
     "question": "Can you track warranties for equipment we bought elsewhere?",
     "answer": "Yes. We can add existing assets to the coverage register regardless of where they were purchased, provided serial and purchase details are available."
    },
    {
     "question": "What happens when a device can no longer be covered?",
     "answer": "We let you know in advance and recommend suitable replacement options, or an alternative support arrangement such as an AMC where appropriate."
    }
   ],
   "meta_title": "Warranty & Renewal Management | TM Solutech",
   "meta_description": "Warranty and renewal management from TM Solutech: track hardware warranties, support contracts and subscriptions, with advance alerts and handled renewals."
  },
  "after-sales-technical-support": {
   "slug": "after-sales-technical-support",
   "title": "After Sales Technical Support",
   "icon": "fas fa-headset",
   "short_description": "Dependable technical support after purchase, covering troubleshooting, warranty claims and coordination with manufacturers for your hardware and software.",
   "description": "<p>Our relationship does not end when equipment is delivered. We provide after sales technical support for the hardware and software you procure through us, helping your team troubleshoot issues, apply updates and get devices back into service as quickly as possible.</p><p>When a fault requires manufacturer involvement, our team logs and follows up warranty claims on your behalf, coordinating diagnostics, part replacements and engineer visits. You get a single point of contact who understands your environment and keeps you informed, instead of navigating multiple vendor support lines on your own.</p>",
   "feature_items": [
    {
     "icon": "fas fa-comments",
     "title": "Remote Troubleshooting",
     "text": "Phone, email and remote session support to diagnose and resolve common hardware and software issues."
    },
    {
     "icon": "fas fa-ticket",
     "title": "Warranty Claim Handling",
     "text": "We log manufacturer cases, share diagnostics and follow up until the replacement or repair is complete."
    },
    {
     "icon": "fas fa-arrows-rotate",
     "title": "Updates & Patching Help",
     "text": "Guidance on firmware, driver and software updates to keep devices stable, secure and supported."
    },
    {
     "icon": "fas fa-user-check",
     "title": "Single Point of Contact",
     "text": "One familiar team that knows your purchases and environment, handling issues from start to finish."
    }
   ],
   "benefit_items": [
    {
     "title": "Faster Issue Resolution",
     "text": "Problems are diagnosed and escalated by people who know your setup."
    },
    {
     "title": "Less Vendor Chasing",
     "text": "We manage manufacturer communication so your team can stay focused."
    },
    {
     "title": "Longer Device Life",
     "text": "Timely fixes and updates keep equipment running well for longer."
    }
   ],
   "process_items": [
    {
     "title": "Issue Reported",
     "text": "Your team raises an issue by phone or email with device details and a description of the fault."
    },
    {
     "title": "Remote Diagnosis",
     "text": "Our engineers troubleshoot remotely to identify the cause and attempt a first-level resolution."
    },
    {
     "title": "Escalation & Claims",
     "text": "Where needed, we raise and manage a manufacturer warranty case or arrange an on-site visit."
    },
    {
     "title": "Resolution & Closure",
     "text": "Confirm the fix with your users, record the outcome and close the case with clear notes."
    }
   ],
   "faq_items": [
    {
     "question": "Is after sales support only for products bought from TM Solutech?",
     "answer": "It is primarily designed for equipment and software procured through us; support for other assets can be arranged through an AMC or on-site support engagement."
    },
    {
     "question": "Will you deal with the manufacturer on our behalf?",
     "answer": "Yes. We log and follow up warranty cases with the manufacturer and keep you updated until the issue is resolved."
    }
   ],
   "meta_title": "After Sales Technical Support | TM Solutech",
   "meta_description": "After sales technical support from TM Solutech: troubleshooting, updates and managed warranty claims for the hardware and software you buy through us."
  },
  "product-consultation-recommendations": {
   "slug": "product-consultation-recommendations",
   "title": "Product Consultation & Recommendations",
   "icon": "fas fa-lightbulb",
   "short_description": "Independent, practical advice on choosing the right hardware and software for your workloads, users, growth plans and budget before you buy.",
   "description": "<p>With so many models, editions and specifications on the market, choosing the right IT products can be difficult. We start by understanding how your teams work, what your applications demand and where your business is heading, then recommend hardware and software that genuinely fits those needs.</p><p>Our team compares options across leading OEMs and software publishers, explains trade-offs in plain language and highlights the total cost of ownership, not just the purchase price. You receive a clear, reasoned recommendation that your technical and finance stakeholders can review together, helping you invest with confidence and avoid costly mismatches.</p>",
   "feature_items": [
    {
     "icon": "fas fa-route",
     "title": "Needs Discovery",
     "text": "Structured conversations to understand users, workloads, applications, growth plans and constraints."
    },
    {
     "icon": "fas fa-scale-balanced",
     "title": "Side-by-Side Comparisons",
     "text": "Shortlisted products compared on performance, compatibility, support terms and long-term running costs."
    },
    {
     "icon": "fas fa-chart-line",
     "title": "Total Cost View",
     "text": "Recommendations that account for warranty, licensing, power and maintenance, not only upfront cost."
    },
    {
     "icon": "fas fa-users-gear",
     "title": "Stakeholder-Ready Proposals",
     "text": "Clear written recommendations suitable for review by IT, finance and management teams together."
    }
   ],
   "benefit_items": [
    {
     "title": "Fit-for-Purpose Choices",
     "text": "Products are selected around real requirements, not sales targets."
    },
    {
     "title": "Fewer Costly Mistakes",
     "text": "Compatibility and sizing are considered before any purchase is made."
    },
    {
     "title": "Future-Ready Investment",
     "text": "Recommendations account for growth so equipment stays useful longer."
    }
   ],
   "process_items": [
    {
     "title": "Discovery Discussion",
     "text": "Understand your business goals, users, applications and existing infrastructure in detail."
    },
    {
     "title": "Requirement Definition",
     "text": "Translate needs into clear technical specifications and evaluation criteria for each product."
    },
    {
     "title": "Option Evaluation",
     "text": "Shortlist and compare suitable products from leading brands against the agreed criteria."
    },
    {
     "title": "Recommendation Report",
     "text": "Present a reasoned recommendation with costs, trade-offs and next steps for your approval."
    }
   ],
   "faq_items": [
    {
     "question": "Is there an obligation to buy after a consultation?",
     "answer": "No. Our recommendations are yours to use, and you can decide independently whether to proceed with procurement through us."
    },
    {
     "question": "Can you advise on a mix of brands?",
     "answer": "Yes. We recommend whichever combination of products best meets your requirements, while checking compatibility across your environment."
    }
   ],
   "meta_title": "Product Consultation & Recommendations | TM Solutech",
   "meta_description": "IT product consultation from TM Solutech: practical, reasoned hardware and software recommendations matched to your workloads, users, growth and budget."
  },
  "annual-maintenance-service-amc": {
   "slug": "annual-maintenance-service-amc",
   "title": "Annual Maintenance Service (AMC)",
   "icon": "fas fa-toolbox",
   "short_description": "Annual maintenance contracts covering preventive upkeep, breakdown support and repairs for servers, desktops, laptops, printers and network equipment.",
   "description": "<p>Our Annual Maintenance Contracts give you planned, predictable care for your IT hardware beyond the manufacturer warranty. We cover servers, desktops, laptops, printers, UPS units and networking equipment with scheduled preventive maintenance and breakdown support, helping reduce unexpected failures and extend the useful life of your assets.</p><p>Each AMC is scoped around your asset list, locations and business priorities, with clearly defined coverage and visit schedules. Our engineers keep service records for every device, so you have a clear history of maintenance, repairs and recurring issues to guide future refresh and budgeting decisions.</p>",
   "feature_items": [
    {
     "icon": "fas fa-calendar-check",
     "title": "Preventive Maintenance",
     "text": "Scheduled health checks, cleaning, firmware updates and inspections to catch issues before they escalate."
    },
    {
     "icon": "fas fa-wrench",
     "title": "Breakdown Support",
     "text": "Diagnosis and repair of hardware faults, with part replacement arranged as defined in your contract."
    },
    {
     "icon": "fas fa-laptop",
     "title": "Multi-Device Coverage",
     "text": "Servers, desktops, laptops, printers, UPS units and network devices covered under a single agreement."
    },
    {
     "icon": "fas fa-clipboard-list",
     "title": "Service Records",
     "text": "A maintained history of visits, repairs and recurring faults for each asset to support planning."
    }
   ],
   "benefit_items": [
    {
     "title": "Predictable Costs",
     "text": "A fixed annual arrangement makes maintenance spend easier to budget."
    },
    {
     "title": "Fewer Unplanned Failures",
     "text": "Regular preventive care reduces the likelihood of sudden breakdowns."
    },
    {
     "title": "Extended Asset Life",
     "text": "Well-maintained hardware stays productive for longer after warranty ends."
    }
   ],
   "process_items": [
    {
     "title": "Asset Inventory",
     "text": "Record every device to be covered, with location, condition, age and current warranty status."
    },
    {
     "title": "Contract Scoping",
     "text": "Agree coverage, visit frequency, inclusions and exclusions based on your priorities."
    },
    {
     "title": "Scheduled Maintenance",
     "text": "Carry out preventive visits on the agreed schedule and respond to reported breakdowns."
    },
    {
     "title": "Review & Reporting",
     "text": "Share service records and observations to guide repairs, upgrades and replacement planning."
    }
   ],
   "faq_items": [
    {
     "question": "Can an AMC cover equipment from different brands?",
     "answer": "Yes. Our AMCs can cover a mix of brands and device types, subject to an initial assessment of the equipment's condition."
    },
    {
     "question": "Are spare parts included in the AMC?",
     "answer": "That depends on the contract type you choose; we offer options with and without parts and define the inclusions clearly before you sign."
    }
   ],
   "meta_title": "Annual Maintenance Service (AMC) | TM Solutech",
   "meta_description": "IT hardware AMC from TM Solutech: preventive maintenance, breakdown support and service records for servers, desktops, laptops, printers and network gear."
  },
  "on-site-l1-l2-support-services": {
   "slug": "on-site-l1-l2-support-services",
   "title": "On-Site L1 & L2 Support Services",
   "icon": "fas fa-user-gear",
   "short_description": "Dedicated or scheduled on-site engineers delivering L1 and L2 IT support for users, devices, networks and servers at your offices and branches.",
   "description": "<p>Some issues are best solved in person. We provide on-site engineers who deliver L1 and L2 support at your premises, either as a dedicated resident engineer or through scheduled visits. They handle everyday user requests, device and printer problems, network connectivity, email and application issues, and routine server administration.</p><p>Our engineers follow your processes and ticketing tools, document their work and escalate complex problems to our senior specializts when needed. This gives your organization a dependable, familiar support presence on the ground, while we manage staffing, skills development and backup cover behind the scenes.</p>",
   "feature_items": [
    {
     "icon": "fas fa-person-walking",
     "title": "Resident or Visiting Engineers",
     "text": "Choose a full-time on-site engineer or scheduled visits, depending on your user base and locations."
    },
    {
     "icon": "fas fa-life-ring",
     "title": "L1 User Support",
     "text": "Hands-on help with logins, devices, printers, email, connectivity and everyday application issues."
    },
    {
     "icon": "fas fa-gears",
     "title": "L2 Technical Support",
     "text": "Deeper troubleshooting of servers, network devices, directory services and recurring technical faults."
    },
    {
     "icon": "fas fa-building",
     "title": "Process Alignment",
     "text": "Engineers work within your ticketing, escalation and reporting processes for consistent service."
    }
   ],
   "benefit_items": [
    {
     "title": "Hands-On Support",
     "text": "Users get in-person help for issues that are hard to resolve remotely."
    },
    {
     "title": "Flexible Staffing",
     "text": "Scale engineer presence up or down without hiring overheads."
    },
    {
     "title": "Continuity of Service",
     "text": "Backup cover is arranged when your regular engineer is unavailable."
    }
   ],
   "process_items": [
    {
     "title": "Support Needs Review",
     "text": "Assess users, sites, systems and ticket patterns to define the right level of on-site support."
    },
    {
     "title": "Engagement Design",
     "text": "Agree engineer profile, working hours, scope of L1 and L2 tasks and escalation paths."
    },
    {
     "title": "Engineer Onboarding",
     "text": "Deploy engineers and familiarize them with your environment, tools, policies and key contacts."
    },
    {
     "title": "Ongoing Review",
     "text": "Review ticket trends and feedback regularly, adjusting scope or staffing as your needs evolve."
    }
   ],
   "faq_items": [
    {
     "question": "What is the difference between L1 and L2 support?",
     "answer": "L1 covers first-line user requests and common device issues, while L2 handles deeper technical troubleshooting of servers, networks and recurring problems."
    },
    {
     "question": "What happens if our on-site engineer is on leave?",
     "answer": "We arrange backup cover so your support continues, and our senior specializts remain available for escalations."
    }
   ],
   "meta_title": "On-Site L1 & L2 Support Services | TM Solutech",
   "meta_description": "On-site L1 and L2 IT support from TM Solutech: resident or visiting engineers for user, device, network and server support at your offices and branches."
  },
  "cloud-migration-services": {
   "slug": "cloud-migration-services",
   "title": "Cloud Migration Services",
   "icon": "fas fa-cloud-arrow-up",
   "short_description": "Planned migration of on-premise servers, applications and data to AWS, Microsoft Azure or private cloud, with minimal downtime and no surprises after cutover.",
   "description": "<p>Moving to the cloud should reduce complexity, not add to it. Our team assesses your existing servers, applications and data, then recommends the right target for each workload, whether that is AWS, Microsoft Azure or a private cloud. We choose the appropriate approach for every system, from straightforward rehosting to replatforming where it adds real value.</p><p>Migrations are executed in planned waves with tested rollback options, data validation and cutovers scheduled around your business hours. After go-live, we optimize performance, security and cost, and hand over clear documentation so your team is confident running the new environment.</p>",
   "feature_items": [
    {
     "icon": "fas fa-server",
     "title": "Workload Assessment",
     "text": "Inventory of servers, applications and dependencies to determine cloud readiness and target sizing."
    },
    {
     "icon": "fas fa-route",
     "title": "Migration Strategy",
     "text": "Rehost, replatform or refactor decisions made per workload based on cost, risk and business value."
    },
    {
     "icon": "fas fa-arrow-right-arrow-left",
     "title": "Data Migration",
     "text": "Secure transfer and synchronization of databases and file data with integrity checks before cutover."
    },
    {
     "icon": "fas fa-gears",
     "title": "Post-Migration Optimization",
     "text": "Right-sizing, monitoring, backup and security configuration once workloads are live in the cloud."
    }
   ],
   "benefit_items": [
    {
     "title": "Minimal Downtime",
     "text": "Phased cutovers scheduled around your business operations."
    },
    {
     "title": "Controlled Cloud Costs",
     "text": "Right-sized resources avoid paying for capacity you do not use."
    },
    {
     "title": "Scalable Infrastructure",
     "text": "Add capacity on demand as your business and workloads grow."
    }
   ],
   "process_items": [
    {
     "title": "Discovery & Assessment",
     "text": "Map current infrastructure, application dependencies and business priorities for migration."
    },
    {
     "title": "Migration Planning",
     "text": "Design the target architecture, migration waves, rollback plans and cutover schedule."
    },
    {
     "title": "Pilot & Migrate",
     "text": "Validate the approach with a pilot workload, then migrate remaining systems in waves."
    },
    {
     "title": "Optimize & Handover",
     "text": "Tune performance and costs, then hand over documentation and operational support."
    }
   ],
   "faq_items": [
    {
     "question": "How do you keep downtime to a minimum during migration?",
     "answer": "We replicate data ahead of time, test each workload in the cloud before cutover and schedule the final switch during agreed low-usage windows."
    },
    {
     "question": "Should we choose AWS, Azure or a private cloud?",
     "answer": "It depends on your applications, licensing, compliance needs and budget. We assess these factors and recommend the best fit for each workload, including hybrid options."
    }
   ],
   "meta_title": "Cloud Migration Services | TM Solutech",
   "meta_description": "Migrate on-premise servers, applications and data to AWS, Microsoft Azure or private cloud with minimal downtime. Planned, tested migration by TM Solutech."
  }
 }
}
''')

SERVICE_FIELDS = (
    'short_description', 'description', 'icon', 'feature_items', 'benefit_items',
    'process_items', 'faq_items', 'meta_title', 'meta_description',
)


def apply_catalog(apps, schema_editor):
    ServiceCategory = apps.get_model('services', 'ServiceCategory')
    Service = apps.get_model('services', 'Service')

    for cat_order, (cat_slug, cat_name, services) in enumerate(LAYOUT, start=1):
        new_cat = CATALOG['categories'].get(cat_slug)
        if new_cat:
            category, _ = ServiceCategory.objects.get_or_create(
                slug=cat_slug,
                defaults={
                    'name': new_cat['name'],
                    'short_description': new_cat['short_description'],
                    'description': new_cat['description'],
                    'icon': new_cat['icon'],
                    'is_active': True,
                    'show_in_nav': True,
                },
            )
        else:
            category = ServiceCategory.objects.filter(slug=cat_slug).first()
            if category is None:
                continue  # Removed in this environment; nothing to reorder.
            if cat_name:
                category.name = cat_name
        category.display_order = cat_order
        category.save()

        for svc_order, entry in enumerate(services, start=1):
            if isinstance(entry, str):
                content = CATALOG['services'][entry]
                service, _ = Service.objects.get_or_create(
                    slug=entry,
                    defaults=dict(
                        {field: content[field] for field in SERVICE_FIELDS},
                        category=category,
                        title=content['title'],
                        is_active=True,
                        show_in_nav=True,
                    ),
                )
            else:
                slug, title = entry
                service = Service.objects.filter(slug=slug).first()
                if service is None:
                    continue
                service.title = title
            service.category = category
            service.display_order = svc_order
            service.is_active = True
            service.save()

    Service.objects.filter(slug__in=RETIRED).update(is_active=False, show_in_nav=False)


def noop(apps, schema_editor):
    # Not reversed automatically: the catalog may have been edited in the dashboard since.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_convert_sections_to_items'),
    ]

    operations = [
        migrations.RunPython(apply_catalog, noop),
    ]
