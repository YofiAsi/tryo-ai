import logging
from datetime import datetime, timezone

from app.consts.enums import (
    DegreeType,
    LanguageLevel,
    SeniorityLevel,
    WorkArrangement,
)
from app.consts.models import EducationRequirement, Language
from app.entity.job_position_entity import (
    EmploymentType,
    JobPosition,
    JobSkill,
    JobStatus,
    JobTournament,
    JobTournamentStatus,
    Requirements,
)

log = logging.getLogger(__name__)


POSITIONS = [
    {
        "title": "Senior Backend Engineer (Python)",
        "company": "Nimbus Labs",
        "status": JobStatus.OPEN,
        "city": "Tel Aviv",
        "country": "Israel",
        "employment_type": EmploymentType.FULL_TIME,
        "seniority_level": SeniorityLevel.SENIOR,
        "work_arrangement": WorkArrangement.REMOTE,
        "summary": (
            "Nimbus Labs is hiring a Senior Backend Engineer for a full-time remote role based in "
            "Tel Aviv to own and scale async Python services on a FastAPI + MongoDB ingestion platform "
            "processing roughly 50k events per second. You will design reliable pipelines, strengthen "
            "tracing and metrics, mentor mid-level engineers, and partner with platform, ML, and SRE on "
            "capacity planning and rollouts. Core stack: Python (6+ years), FastAPI, MongoDB, Docker, "
            "and Kafka. Bachelor's in Computer Science required; AWS Certified Developer preferred. "
            "Fluent English and native Hebrew. Annual compensation around 180,000 ILS. Best fit for "
            "engineers with production async/await experience who care about clean domain boundaries "
            "and pragmatic testing."
        ),
        "original_text": (
            "Nimbus Labs is hiring a Senior Backend Engineer to lead the design of our FastAPI + MongoDB "
            "ingestion services. You'll partner with platform and ML teams to ship reliable async pipelines, "
            "improve observability, and mentor mid-level engineers. We operate at ~50k events/s and care "
            "deeply about clean domain boundaries and pragmatic testing."
        ),
        "responsibilities": [
            "Design and ship FastAPI services backing our ingestion platform",
            "Drive code review standards and mentor mid-level engineers",
            "Improve tracing, metrics, and on-call ergonomics",
            "Partner with SRE on capacity planning and rollout strategy",
        ],
        "recruiter_notes": "Prefers candidates with prior async/await production experience; no on-site requirement.",
        "salary": 180000,
        "contact_email": "hiring@nimbuslabs.example",
        "contact_name": "Dana Levi",
        "contact_phone": "+972-3-555-0142",
        "skills": [
            JobSkill(name="Python", years_of_experience=6, weight=10),
            JobSkill(name="FastAPI", years_of_experience=3, weight=8),
            JobSkill(name="MongoDB", years_of_experience=4, weight=7),
            JobSkill(name="Docker", years_of_experience=4, weight=6),
            JobSkill(name="Kafka", years_of_experience=2, weight=5),
        ],
        "requirements": Requirements(
            certifications=["AWS Certified Developer – Associate"],
            educations=[
                EducationRequirement(degree=DegreeType.BACHELOR, field_of_study="Computer Science")
            ],
            languages=[
                Language(name="English", level=LanguageLevel.FLUENT),
                Language(name="Hebrew", level=LanguageLevel.NATIVE),
            ],
        ),
    },
    {
        "title": "Frontend Engineer (React/TypeScript)",
        "company": "Brightline",
        "status": JobStatus.OPEN,
        "city": "Berlin",
        "country": "Germany",
        "employment_type": EmploymentType.FULL_TIME,
        "seniority_level": SeniorityLevel.MID,
        "work_arrangement": WorkArrangement.HYBRID,
        "summary": (
            "Brightline is looking for a mid-level Frontend Engineer to join a small senior team in "
            "Berlin on a full-time hybrid schedule (two days per week on-site). You will own feature "
            "areas of our B2B analytics product, shipping production React and TypeScript with "
            "Tailwind, collaborating with designers on accessible components, refactoring legacy class "
            "components to hooks, and testing with Vitest and Playwright. Required skills include "
            "React and TypeScript (3+ years each), Tailwind CSS, and Vite as a plus. Bachelor's in "
            "Software Engineering; fluent English and intermediate German. Salary around 85,000 EUR "
            "with visa relocation support. Ideal for engineers who prioritize accessibility, polish, "
            "and developer experience."
        ),
        "original_text": (
            "Brightline is looking for a mid-level Frontend Engineer to join a small, senior team. You'll own "
            "feature areas of our analytics product, working closely with designers and backend engineers to "
            "ship production-quality React + TypeScript code with strong attention to accessibility and DX."
        ),
        "responsibilities": [
            "Develop new product features in React + TypeScript",
            "Collaborate with designers on accessible component design",
            "Refactor legacy class components to hooks",
            "Write unit and integration tests with Vitest and Playwright",
        ],
        "recruiter_notes": "Hybrid 2 days/week in the Berlin office. Visa relocation supported.",
        "salary": 85000,
        "contact_email": "talent@brightline.example",
        "contact_name": "Markus Weber",
        "contact_phone": "+49-30-555-0199",
        "skills": [
            JobSkill(name="React", years_of_experience=3, weight=10),
            JobSkill(name="TypeScript", years_of_experience=3, weight=9),
            JobSkill(name="Tailwind CSS", years_of_experience=2, weight=6),
            JobSkill(name="Vite", years_of_experience=1, weight=4),
        ],
        "requirements": Requirements(
            certifications=None,
            educations=[
                EducationRequirement(degree=DegreeType.BACHELOR, field_of_study="Software Engineering")
            ],
            languages=[
                Language(name="English", level=LanguageLevel.FLUENT),
                Language(name="German", level=LanguageLevel.INTERMEDIATE),
            ],
        ),
    },
    {
        "title": "DevOps / Site Reliability Engineer",
        "company": "Vector Cloud",
        "status": JobStatus.OPEN,
        "city": "London",
        "country": "United Kingdom",
        "employment_type": EmploymentType.FULL_TIME,
        "seniority_level": SeniorityLevel.SENIOR,
        "work_arrangement": WorkArrangement.ON_SITE,
        "summary": (
            "Vector Cloud's platform team in London needs a Senior DevOps / Site Reliability Engineer "
            "on a full-time on-site arrangement (Monday through Thursday on-site, Friday remote) to "
            "operate and harden a multi-region EKS estate supporting hundreds of internal services. "
            "You will own Terraform modules for EKS, RDS, and networking, run GitOps deployments via "
            "ArgoCD, lead post-incident reviews, and coach product teams on SLOs and on-call practice. "
            "Key skills: Kubernetes (5+ years), Terraform, AWS, Prometheus, and ArgoCD. CKA "
            "certification and a bachelor's in Computer Science required; UK right-to-work mandatory. "
            "Salary around 110,000 GBP. Suited to reliability-focused engineers who enjoy hands-on "
            "infrastructure ownership in a high-scale environment."
        ),
        "original_text": (
            "Vector Cloud's platform team operates a multi-region EKS estate. We're hiring a Senior SRE to own "
            "Terraform modules, GitOps pipelines, and incident response practices. The role is on-site in our "
            "London HQ four days/week."
        ),
        "responsibilities": [
            "Own Terraform modules for EKS, RDS, and networking",
            "Run GitOps deployments via ArgoCD",
            "Lead post-incident reviews and reliability initiatives",
            "Coach product teams on SLOs and on-call practice",
        ],
        "recruiter_notes": "Must hold UK right-to-work. On-site Mon–Thu; Friday remote.",
        "salary": 110000,
        "contact_email": "careers@vectorcloud.example",
        "contact_name": "Priya Shah",
        "contact_phone": "+44-20-7946-0312",
        "skills": [
            JobSkill(name="Kubernetes", years_of_experience=5, weight=10),
            JobSkill(name="Terraform", years_of_experience=4, weight=9),
            JobSkill(name="AWS", years_of_experience=5, weight=8),
            JobSkill(name="Prometheus", years_of_experience=3, weight=6),
            JobSkill(name="ArgoCD", years_of_experience=2, weight=5),
        ],
        "requirements": Requirements(
            certifications=["CKA – Certified Kubernetes Administrator"],
            educations=[
                EducationRequirement(degree=DegreeType.BACHELOR, field_of_study="Computer Science")
            ],
            languages=[Language(name="English", level=LanguageLevel.FLUENT)],
        ),
    },
    {
        "title": "Machine Learning Engineer",
        "company": "Helix AI",
        "status": JobStatus.DRAFT,
        "city": "New York",
        "country": "United States",
        "employment_type": EmploymentType.CONTRACT,
        "seniority_level": SeniorityLevel.LEAD,
        "work_arrangement": WorkArrangement.REMOTE,
        "summary": (
            "Helix AI is engaging a Lead Machine Learning Engineer on a 12-month full-time remote "
            "contract (US timezone overlap required) based in New York to improve retrieval and "
            "re-ranking for our enterprise search product. You will design experiments, prototype in "
            "PyTorch, productionize models with vLLM or TGI, build offline and online evaluation "
            "pipelines, and mentor two mid-level MLEs. Deep experience in Python (7+ years), PyTorch "
            "(5+ years), LLM fine-tuning, vector databases, and MLOps expected. Master's in Machine "
            "Learning or a PhD in Computer Science; native English. Contract compensation around "
            "220,000 USD with extension option. Role is in draft status—ideal for leaders who own "
            "model quality and deployment end-to-end."
        ),
        "original_text": (
            "Helix AI is engaging a Lead ML Engineer on a 12-month contract to ship retrieval and re-ranking "
            "improvements to our search stack. You'll prototype with PyTorch, productionize with vLLM/TGI, and "
            "own evaluation harnesses end-to-end."
        ),
        "responsibilities": [
            "Design retrieval and re-ranking experiments",
            "Productionize models with vLLM or TGI",
            "Build offline and online evaluation pipelines",
            "Mentor two mid-level MLEs on the team",
        ],
        "recruiter_notes": "12-month contract with extension option. US-timezone overlap required.",
        "salary": 220000,
        "contact_email": "ml-hiring@helix.example",
        "contact_name": "Ethan Park",
        "contact_phone": "+1-212-555-0173",
        "skills": [
            JobSkill(name="Python", years_of_experience=7, weight=10),
            JobSkill(name="PyTorch", years_of_experience=5, weight=10),
            JobSkill(name="LLM Fine-tuning", years_of_experience=2, weight=8),
            JobSkill(name="Vector Databases", years_of_experience=2, weight=7),
            JobSkill(name="MLOps", years_of_experience=3, weight=6),
        ],
        "requirements": Requirements(
            certifications=None,
            educations=[
                EducationRequirement(degree=DegreeType.MASTER, field_of_study="Machine Learning"),
                EducationRequirement(degree=DegreeType.DOCTORATE, field_of_study="Computer Science"),
            ],
            languages=[Language(name="English", level=LanguageLevel.NATIVE)],
        ),
    },
    {
        "title": "Junior Full-Stack Developer",
        "company": "Pebble Studio",
        "status": JobStatus.CLOSED,
        "city": "Lisbon",
        "country": "Portugal",
        "employment_type": EmploymentType.FULL_TIME,
        "seniority_level": SeniorityLevel.JUNIOR,
        "work_arrangement": WorkArrangement.HYBRID,
        "summary": (
            "Pebble Studio, a 12-person product studio in Lisbon, sought a Junior Full-Stack Developer "
            "on a full-time hybrid basis to build Node.js APIs and React frontends for media and "
            "culture clients across Europe. Responsibilities included shipping features end-to-end, "
            "pair-programming with senior engineers, writing tests, participating in code review, and "
            "triaging bug reports. Required: JavaScript, Node.js, React, and SQL (roughly one year "
            "each). Bachelor's in Computer Science or a diploma in Web Development; advanced English "
            "and native Portuguese. Salary around 32,000 EUR. This position is closed and retained as "
            "demo data—it was a strong entry role for developers growing into full-stack ownership "
            "in a small, mentorship-heavy studio."
        ),
        "original_text": (
            "Pebble Studio is a 12-person product studio in Lisbon. We're hiring a junior full-stack developer "
            "to ship features across Node.js APIs and React frontends. You'll be paired with a senior engineer "
            "and own progressively larger slices of client projects."
        ),
        "responsibilities": [
            "Implement features across Node.js and React stacks",
            "Pair-program with senior engineers on client projects",
            "Write tests and participate in code review",
            "Help triage incoming bug reports",
        ],
        "recruiter_notes": "Position has been filled — kept here as a closed example for the demo.",
        "salary": 32000,
        "contact_email": "jobs@pebblestudio.example",
        "contact_name": "Sofia Almeida",
        "contact_phone": "+351-21-555-0188",
        "skills": [
            JobSkill(name="JavaScript", years_of_experience=1, weight=8),
            JobSkill(name="Node.js", years_of_experience=1, weight=7),
            JobSkill(name="React", years_of_experience=1, weight=7),
            JobSkill(name="SQL", years_of_experience=1, weight=5),
        ],
        "requirements": Requirements(
            certifications=None,
            educations=[
                EducationRequirement(degree=DegreeType.BACHELOR, field_of_study="Computer Science"),
                EducationRequirement(degree=DegreeType.DIPLOMA, field_of_study="Web Development"),
            ],
            languages=[
                Language(name="English", level=LanguageLevel.ADVANCED),
                Language(name="Portuguese", level=LanguageLevel.NATIVE),
            ],
        ),
    },
]


async def init_job_position(data: dict) -> None:
    existing = await JobPosition.find_one(
        JobPosition.title == data["title"],
        JobPosition.company == data["company"],
    )
    if existing:
        log.info(f"Job position '{data['title']}' at '{data['company']}' already exists")
        return

    now = datetime.now(timezone.utc)
    job_position = JobPosition(
        status=data["status"],
        title=data["title"],
        original_text=data["original_text"],
        summary=data["summary"],
        company=data["company"],
        city=data.get("city"),
        country=data.get("country"),
        employment_type=data["employment_type"],
        seniority_level=data["seniority_level"],
        work_arrangement=data["work_arrangement"],
        responsibilities=data.get("responsibilities"),
        recruiter_notes=data.get("recruiter_notes"),
        salary=data.get("salary"),
        contact_email=data.get("contact_email"),
        contact_name=data.get("contact_name"),
        contact_phone=data.get("contact_phone"),
        skills=data.get("skills"),
        requirements=data.get("requirements"),
        tournament=JobTournament(
            status=JobTournamentStatus.PENDING,
            task=None,
            candidates=[],
        ),
        created_at=now,
        updated_at=now,
    )
    await JobPosition.create(job_position)
    log.info(f"Job position '{data['title']}' at '{data['company']}' created")


async def init_default_job_positions() -> None:
    log.info("Initializing default job positions")
    for position in POSITIONS:
        await init_job_position(position)
    log.info("Default job positions initialized")


async def init_job_position_migration() -> None:
    log.info("Initializing job position migration")
    await init_default_job_positions()
    log.info("Job position migration initialized")
