# Career Guru 🤖

**Career Guru** is a diploma-focused career-guidance web application built with **Flask, Jinja, Bootstrap, Flask-Login, bcrypt, Flask-Mail, and SQLite**. It helps students explore career options, understand how their interests relate to different paths, review resume evidence against a selected career, and request guidance from a human counselor.

The current release emphasizes explainable, local workflows. Career matching, quiz scoring, and resume evaluation work without a hosted language model or an AI API key. Several AI-powered modules are intentionally shown as **future features** and are disabled in this release.

**Repository:** [YashRajBansal/CareerGuru-ai](https://github.com/YashRajBansal/CareerGuru-ai)

---

## Table of contents

- [Current release at a glance](#current-release-at-a-glance)
- [Features available now](#features-available-now)
- [Future modules and contribution roadmap](#future-modules-and-contribution-roadmap)
- [AI and retrieval architecture: what is actually in the code](#ai-and-retrieval-architecture-what-is-actually-in-the-code)
- [Technology stack](#technology-stack)
- [Run locally](#run-locally)
- [Administrator setup](#administrator-setup)
- [Configuration](#configuration)
- [How career matching works](#how-career-matching-works)
- [How the resume checker works](#how-the-resume-checker-works)
- [Data, migrations, and privacy](#data-migrations-and-privacy)
- [Security notes](#security-notes)
- [Tests and verification](#tests-and-verification)
- [Contributing: build a future module on a branch](#contributing-build-a-future-module-on-a-branch)
- [Limitations](#limitations)
- [Maintainer](#maintainer)

---

## Current release at a glance

| Area | Current status |
|---|---|
| Career library and browsing | Available |
| Local career matching | Available; deterministic keyword and cosine-similarity scoring |
| Knowledge-base management | Available in the admin workspace |
| RAG-style counselor retrieval/context pipeline | Present in code, but behind the generation release lock |
| Local Ollama LLM generation adapter | Present for future development; generation locked |
| 12-question interest quiz | Available; transparent scoring |
| Resume upload and career-fit review | Available; deterministic text heuristics |
| Student profiles and authentication | Available |
| Human consultation requests | Available; manual staff review |
| Admin dashboard and record management | Available |
| Analytics, exports, review queue, audit log | Available |
| AI career counseling | Future feature; locked |
| AI mock interviews | Future feature; locked |
| AI-generated match explanations and quiz interpretation | Future feature; locked |
| AI resume feedback and bullet rewriting | Future feature; locked |
| AI consultation summaries and urgency tagging | Future feature; locked |

> **Release boundary:** AI/model generation is disabled by `GENERATION_LOCKED = True` in `app/services/ai.py`. Installing Ollama or configuring a model does not enable the locked features. There is no environment-variable or admin-toggle bypass in this release.

## Features available now

### 1. Career library and exploration

- Browse **80 individually scoped career profiles** across technology, design, engineering, health, education, business, the built environment, science, hospitality, trades, and sport.
- Explore the skills, interests, entry pathways, and typical work associated with each profile.
- Filter and search the career library, save career paths, and manage career content through the admin workspace.
- Career information is presented as editorial exploration material. It is not a verified admissions directory and does not invent salary or job-demand statistics.

### 2. Explainable career matching

- Enter comma-separated interests and skills, for example `cricket, drawing, computers` or `CAD, material testing`.
- Use suggestion chips to add common interests such as cricket, coding, drawing, and building design.
- The matching service evaluates entries separately against career titles, skills, and traits, using keyword weighting and local cosine-similarity matching.
- Results appear above the input form and show the interests that contributed to each match.
- Typed interests determine candidate matches. The latest quiz results are used only to break equally relevant ties.
- Career edits are reflected in the active recommender immediately. The separate local text-vector cache can also be rebuilt from the admin workspace for the retrieval pipeline.

Matching is an exploration aid, not a prediction of admission, eligibility, hiring, or employment outcomes. For example, cricket can rank **Cricketer** highly, while CAD and material-testing interests can rank **Civil Engineer** highly. These are examples of the current matching behavior, not guarantees for every input.

### 3. Interest quiz

- A 12-question quiz with responses on a 1–5 scale.
- Back and next controls, progress feedback, and a saved browser draft.
- Six transparent interest scores, each reported on a 0–10 scale.
- Quiz results support career exploration and matching; generated AI interpretations are not part of this release.

The quiz is not a clinically or psychometrically validated assessment.

### 4. Resume Studio

- Accept a PDF, DOCX, or TXT resume, or pasted resume text.
- Evaluate the resume against a selected career using target-skill matching and evidence from project or experience descriptions.
- Distinguish skills that are supported by task evidence, skills that are listed without task evidence, and skills that are not found.
- Save short supporting excerpts and actionable improvement notes in the user's private review history.
- Show a separate presentation-quality rubric alongside the career-fit score.

The checker is deterministic and English-language. It does not use a language model, send extracted resume text to a cloud AI service, verify credentials, or prove that a claim is authentic. Scanned PDFs require OCR and may not extract correctly; complex layouts can also reduce extraction quality. AI rewriting and generated feedback remain locked future modules.

### 5. Student accounts and profiles

- Student registration, sign-in, sign-out, and profile management.
- Existing user fields are retained through the migration process.
- Passwords are stored as bcrypt hashes.
- Email values are normalized and duplicate data is validated.
- Optional birthday handling and profile-avatar upload are supported.
- Uploaded profile images are verified/re-encoded before being stored.

### 6. Human consultations

- Authenticated users can submit consultation requests and manage or cancel their own requests.
- Staff can review requests and manually update their status from the admin workspace.
- Optional Flask-Mail/SMTP configuration can send human consultation confirmations.
- AI-generated summaries and urgency tagging are future features; manual staff review remains available now.

### 7. Administrator workspace

Administrators can:

- Create, edit, reorder, and manage career-library content.
- Create, edit, and delete knowledge-base entries used as reference documents by the dormant counselor retrieval pipeline. Managing these entries is available now; using them in AI-generated answers is locked in this release.
- Search, filter, export, and apply bulk actions to supported records.
- Review users and consultation requests.
- Resolve review-queue queries and inspect audit logs.
- Rebuild the local text index and inspect analytics based on database activity.

Admin access is role-protected. Student self-registration cannot grant administrator privileges. Legacy users without signup dates are identified as legacy records.

### 8. Responsive and accessible interface

- Shared responsive interface with charcoal/graphite dark mode and neutral-grey light mode.
- Theme selection is remembered by the browser after the initial theme update.
- Keyboard-friendly controls and reduced-motion support.
- Animated interaction feedback, with reduced-motion preferences respected.

---

## Future modules and contribution roadmap

The following modules are **planned extension points, not working features in the current release**. They are visible as future features in the interface, and generation requests are blocked on the server. Contributors can build them on separate branches and submit pull requests without treating them as already implemented.

| Future module | Intended contribution scope | Current release behavior |
|---|---|---|
| AI Career Counselor (RAG) | Retrieval-augmented career Q&A using relevant career profiles and approved knowledge-base records as context for a local language model | RAG-style retrieval/context code and local Ollama adapter are present, but `/api/chat` is release-locked and returns HTTP 501 |
| AI Mock Interview | Career-specific interview rounds, follow-up questions, and practice feedback | Locked; feature dialog and coming-soon fallback |
| Generated Match Explanations | Plain-language explanations of why a career matched the student's interests | Locked; current matches show the contributing interests instead |
| AI Interest Interpretation | Optional narrative interpretation of the six quiz scores | Locked; transparent numeric scores remain available |
| AI Resume Feedback and Bullet Rewriting | Suggestions for improving genuine resume evidence and rewriting user-approved bullets | Locked; deterministic career-fit and presentation review remain available |
| Consultation Auto-Summary and Urgency Tagging | Draft summaries and suggested priority labels for staff review | Locked; staff can review and update requests manually |

### Release-lock behavior

The release lock is deliberate:

- `GENERATION_LOCKED = True` in `app/services/ai.py` keeps model-powered generation disabled.
- `/api/chat` returns HTTP `501` with `future_feature: true` before the retrieval or generation path is run.
- Direct counselor/interview URLs show a coming-soon page.
- Direct AI-triage submissions receive the release-lock response.
- Ordinary career matching, quiz, resume-review, and consultation submissions do not call a generation provider.
- Clicking a locked feature does not create a conversation or review-queue entry.
- Ollama settings, if present, do not bypass the lock.

The codebase retains a dormant local-only Ollama adapter for future development and transport regression tests. The current application does not include an OpenAI SDK, OpenAI API-key configuration, or OpenAI API calls. **You do not need to install a model to run the current release.**

---

## AI and retrieval architecture: what is actually in the code

There is a **RAG-style (retrieval-augmented generation) pipeline scaffold** in the repository, but it is **not an active user-facing AI feature in this release**. The distinction matters: retrieval, context assembly, and a local LLM transport adapter are present in code, while the server-side release lock prevents the application from executing that pipeline.

### RAG flow present in the codebase

The intended counselor/interview request path in `app/routes.py` is structured to:

1. Receive a user's message.
2. Retrieve up to four relevant `Career` records and up to two relevant `Knowledge` records with `ai.rank(...)`.
3. Build reference context from those records and append it to the system prompt.
4. Pass the prompt, conversation history, and user message to the local Ollama streaming adapter in `app/services/ai.py`.
5. Stream generated response chunks back to the browser and save the conversation.

That is the core shape of **retrieval-augmented generation (RAG)**: retrieve relevant application content first, then provide it as context to a language model. The route exits with HTTP 501 while `GENERATION_LOCKED` is true, before steps 2–5 run. Treat this as a **dormant/locked RAG implementation path**, not as a working chatbot or live RAG service.

### What the retriever actually uses

The current retrieval implementation is deliberately lightweight and offline:

- It tokenizes each complete career or knowledge record and builds **term-frequency (bag-of-words) vectors**.
- It ranks query-to-document matches using **cosine similarity** over those vectors.
- It can cache the vectors in SQLite in the existing `embedding` fields, with a SHA-256 document fingerprint so stale cached terms can be detected.
- The admin **Rebuild local text index** action and the `refresh-embeddings` Flask CLI command rebuild these local caches for career and knowledge records.
- Each `Career` or `Knowledge` entry is treated as one document. The code shown here does not split documents into chunks before retrieval.

**Important terminology:** the project uses the field/command name `embedding` / `refresh-embeddings` for compatibility, but the current implementation explicitly stores local term-frequency vectors. These are **not learned semantic embeddings** from a transformer or embedding model. The repository does not use FAISS, Chroma, Pinecone, or another dedicated vector database for this retrieval path.

### Active recommender vs. dormant RAG retriever

These are two related but separate code paths:

| Component | Current implementation | Availability |
|---|---|---|
| Career recommender (`app/services/matching.py`) | Canonicalizes common terms, expands selected everyday phrases, weights career title/skills/traits, and scores interest coverage plus lexical cosine similarity | Active now; no LLM required |
| RAG retriever (`ai.rank` in `app/services/ai.py`) | Ranks complete Career and Knowledge records using local term-frequency vectors and cosine similarity | Present in code; used by the locked counselor/interview path |
| Context augmentation (`app/routes.py`) | Adds retrieved career and knowledge references to the LLM system prompt | Present in code; not reached while generation is locked |
| Local LLM adapter (`ai.stream` / `ai.complete`) | Sends prompts to an Ollama server restricted to localhost; supports streamed and non-streamed responses | Present in code; blocked by the release lock |
| Neural semantic embeddings / external vector DB | No learned embedding model or dedicated vector database in this implementation | Not implemented |

The resume checker is also **not an AI/LLM feature**: it uses deterministic rules, document-section parsing, skill aliases, action/task evidence checks, scoring, penalties, and score caps. The quiz uses a transparent RIASEC-style rubric, not an AI personality model.

### What this means for contributors

A contributor can branch from `main` to improve the retrieval layer (for example, add chunking, metadata filters, a proper embedding model, or a vector index) or to complete the locked RAG counselor. Such work should remain optional, preserve the no-model path, document any new dependencies and data processing, and include retrieval-quality and privacy tests. Do not describe any of those extensions as currently shipped until they are implemented, tested, and deliberately enabled in a release.

---

## Technology stack

| Technology | Purpose |
|---|---|
| Python 3.12+ | Application language |
| Flask | Web application and routing |
| Jinja | Server-rendered templates |
| Bootstrap | Responsive UI foundation |
| Flask-Login | User session and role-aware authentication |
| bcrypt | Password hashing |
| Flask-Mail | Optional SMTP email confirmations |
| Flask-WTF / CSRF protection | Protection for browser-originated mutations |
| SQLite | Persistent application database |
| Local lexical matching and cosine similarity | Active, deterministic career recommendations |
| SQLite term-frequency vector cache | Offline retrieval index for Career and Knowledge records |
| Ollama HTTP API adapter | Local-only LLM transport scaffold; locked in this release |
| Pytest | Automated tests |

The project does not require MongoDB for the current application. Legacy MongoDB chatbot data is left untouched; it is not a runtime dependency.

---

## Run locally

### Requirements

- Python **3.12 or newer**
- Git
- Windows PowerShell for the included launcher; other operating systems can use the Flask commands below

### Option A: Windows PowerShell launcher

From the repository root:

```powershell
.\Start-CareerGuru.ps1
```

Open the application at:

- **Career Guru:** http://127.0.0.1:5001
- **Admin sign-in:** http://127.0.0.1:5001/admin

The launcher creates missing local configuration, runs additive database migrations, and starts Flask without debug mode. It is designed not to delete existing records. The `app/venv` mentioned in the maintainer's local setup is a local environment; create your own virtual environment for a fresh checkout.

### Option B: Fresh checkout

Clone the repository and enter the application directory:

```powershell
git clone https://github.com/YashRajBansal/CareerGuru-ai.git
cd CareerGuru-ai\app
```

Create and install into a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create local configuration and initialize the database:

```powershell
.\venv\Scripts\python.exe setup_local.py
.\venv\Scripts\python.exe -m flask --app app init-db
```

Start the local server:

```powershell
.\venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5001
```

For macOS/Linux, activate the environment with `source venv/bin/activate`, install `requirements.txt`, run `python setup_local.py`, initialize with `flask --app app init-db`, and start with `flask --app app run --host 127.0.0.1 --port 5001`.

Create a student account at `/signup`. There are no default production users or administrator credentials.

---

## Administrator setup

There are **no default administrator credentials**. Student signup cannot create an admin account or promote a student.

From the repository root, run the following in PowerShell:

```powershell
cd app
.\venv\Scripts\python.exe -m flask --app app create-admin
```

Follow the prompts to enter a username, email address, and password of at least 12 characters. Password input is hidden. The command creates an account with administrator privileges and a bcrypt password hash; it will not silently promote an existing account.

1. Start the application with `Start-CareerGuru.ps1` or the Flask command above.
2. Open `/login` and sign in using the administrator account you created.
3. Successful administrator sign-in redirects to `/admin`.
4. Use the admin navigation to manage careers, knowledge, users, consultations, review queries, analytics, exports, and audit records.

If `/admin` returns **403**, the signed-in account is a student. Sign out and sign in with the administrator account. If an admin account has not been created, run `create-admin`; do not edit the database manually to promote a user.

---

## Configuration

Use `app/.env.example` as the configuration template. Local setup creates missing local configuration and generates a secret key without printing it.

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask session/signing key; generated locally by `setup_local.py` when missing |
| `DATABASE_URL` | Database location; defaults to `app/instance/users.db` |
| `MAIL_USERNAME` | Optional SMTP username for consultation confirmations |
| `MAIL_PASSWORD` | Optional SMTP password/app password |
| `MAIL_DEFAULT_SENDER` | Optional sender address |
| `COOKIE_SECURE` | Set to `true` when served over HTTPS; use `false` for local HTTP |
| `RATELIMIT_STORAGE_URI` | Rate-limit storage; memory storage is intended for single-process development |
| `OLLAMA_URL` | Reserved for future local-model development; does not unlock generation |
| `OLLAMA_MODEL` | Reserved for future local-model development; does not unlock generation |

For multi-worker hosting, configure a shared supported rate-limit store rather than relying on per-process memory. Never commit `.env`, database files, passwords, session secrets, or provider credentials.

---

## How career matching works

Career matching is local and does not depend on a language model.

1. The student enters interests and/or technical skills, separated by commas.
2. Each entry is evaluated against career titles, skills, and traits. Common everyday wording is mapped to relevant career vocabulary.
3. The active matching service combines title/skill/trait weighting, interest coverage, and lexical cosine similarity to rank relevant career profiles.
4. The result displays matching interests so students can see which of their entries contributed to a suggestion.
5. The latest interest-quiz result is used only to break equally relevant ties; it does not replace typed interests as the source of candidates.

The active career recommender calculates its scores directly from current career titles, skills, and traits. Separately, the dormant RAG retriever can use cached sparse term-frequency vectors stored in SQLite with document fingerprints. Admins can rebuild those career and knowledge caches from the admin workspace, or run `flask --app app refresh-embeddings`. The command name is retained for compatibility: it rebuilds local bag-of-words vectors and makes no network request; it does not call a hosted embedding API or create neural semantic embeddings.

---

## How the resume checker works

The main score is a **career-fit/evidence score**, not a formatting score. Its components are:

| Component | Maximum points |
|---|---:|
| Target skills mentioned, including tool/term aliases | 25 |
| Supporting tasks behind target skills | 40 |
| Relevant project or experience tasks | 20 |
| Resume presentation | 15 |
| **Total** | **100** |

A skill listed without a concrete supporting task loses 4 points, up to 20 points in total. Repeated descriptions can lose 10 points, and dense repeated keyword lists can lose 8 points. Keywords, project titles by themselves, certificates without applied tasks, and future plans do not earn task-evidence points. Evidence requires an action and a specific task or output linked to the skill in project or experience text. Scope and measured outcomes can strengthen evidence; numbers alone do not prove a skill.

The checker also applies evidence caps:

- If no target skills are found, the score is capped at 25.
- If target skills are found but none has supporting task evidence, the score is capped at 45.
- If fewer than half of target skills are supported, the score is capped at 60.

Scores are rounded after deductions and limits. Missing skills receive zero; they are not assumed to be present. If no target career is selected, the result is a general quality-and-evidence review, not a career-fit score.

The separate presentation rubric checks contact information, education, skill clarity, substantive task descriptions, scope/outcomes, readable length, and distinct content. It is the same for the same resume text regardless of the selected career and contributes only 15 points to the career-fit total.

Older saved reviews are preserved and labeled **legacy quality only**. Their earlier score must not be interpreted as the current career-fit score. Resubmit the original resume for the new scoring system; the application cannot reconstruct text it did not store.

This is a deterministic English-language heuristic. It checks whether the text contains supporting detail; it cannot establish that experience, numbers, or credentials are authentic. Review evidence excerpts and deductions carefully, and include only genuine experience. Scanned PDFs require OCR; extraction from complex layouts may be imperfect.

---

## Data, migrations, and privacy

- The default SQLite database is `app/instance/users.db`, unless `DATABASE_URL` points elsewhere.
- `migrations.py` adds fields and feature tables to the existing schema rather than replacing the database.
- Before upgrading a legacy SQLite database, the migration process saves a pre-upgrade copy as `users.pre-upgrade.db` beside it.
- Re-running `init-db` is designed not to duplicate the catalog or overwrite administrator edits.
- The base career catalog is seeded only when the career table is empty. A recorded one-time catalog update adds Cricketer and Civil Engineer to existing installations without overwriting other entries.
- Legacy consultations remain visible to administrators. They are not assigned to a user solely because the email address matches. New requests are associated with the authenticated user.
- The old MongoDB chatbot data is left untouched. The current app does not require MongoDB; any legacy knowledge needed should be reviewed and imported through the managed knowledge interface.
- The former destructive `main.py` reset behavior has been removed; `main.py` starts the app safely.

Original resume uploads and full extracted resume text are not retained. Private reviews store scores and selected short evidence excerpts and can be deleted. Chat messages, quiz responses, and consultation details persist in SQLite. Keep the database and backups private. Profile avatars are served by generated URLs and should not be treated as confidential file storage.

---

## Security notes

- Browser mutations use Flask-WTF CSRF protection.
- Login/signup and expensive endpoints are rate limited.
- Admin pages and legacy admin aliases enforce Flask-Login authorization.
- Private conversation/review records are checked for user ownership.
- User exports omit password hashes and escape spreadsheet formulas.
- AI Markdown is rendered using text-node-based formatting; raw HTML is not executed.
- The application should be hosted behind HTTPS using a production WSGI server, a private persistent database volume, and a shared rate-limit store for multi-worker deployments.
- Flask's built-in development server is for local use, not production hosting.

**Credential rotation warning:** Earlier versions of the source reportedly contained exposed provider credentials. Removing a secret from the current files does not revoke it or erase copies from Git history, clones, or backups. The maintainer must revoke any previously exposed AI API key and Gmail app password with the relevant provider. The current release does not need an AI API key; only optional SMTP mail delivery needs replacement mail credentials.

---

## Tests and verification

From the repository root, run:

```powershell
cd app
.\venv\Scripts\python.exe -m pytest tests -q
```

The test suite uses an in-memory database and disposable fixture users. The supplied release notes describe coverage for:

- Route rendering, authentication, bcrypt password handling, CSRF, and administrator authorization.
- Private-record ownership, recommendations, and quiz validation.
- Resume parsing/deletion and consultation ownership.
- Admin create/update/reorder actions and audit events.
- Rate limiting and model-generation release-lock behavior.
- Provider setup states and dormant local-model transport regression tests.

The tests do not require a downloaded model or send email. Local-model responses are stubbed for transport tests; the release lock remains active during normal application use.

For an isolated browser preview, run `python tests/browser_server.py` from the `app` directory. It uses a temporary database and test-only fixture accounts on localhost port `5002`. It does not open the normal `users.db` and is not a deployment entry point.

---

## Contributing: build a future module on a branch

Contributions are welcome, particularly for the future modules listed above. Please keep experimental work separate from the stable `main` branch so existing students continue to receive the current non-generative release.

### Recommended workflow

1. Fork this repository on GitHub.
2. Clone your fork and add the original project as the `upstream` remote.
3. Start from the latest `main` branch.
4. Create one focused branch for one module or improvement.
5. Implement the feature behind an explicit feature boundary and add tests.
6. Run the existing test suite and the relevant new tests.
7. Open a pull request targeting the upstream `main` branch. Explain the feature, configuration, privacy impact, tests, and any migration steps.

Example commands:

```bash
git clone https://github.com/<your-github-username>/CareerGuru-ai.git
cd CareerGuru-ai
git remote add upstream https://github.com/YashRajBansal/CareerGuru-ai.git
git fetch upstream
git switch main
git merge --ff-only upstream/main
git switch -c feature/ai-career-counselor
```

After making and testing your changes:

```bash
git add .
git commit -m "Add career counselor module"
git push -u origin feature/ai-career-counselor
```

Then open a pull request from your branch to `YashRajBansal/CareerGuru-ai:main`.

### Guidelines for future AI modules

- **Do not silently unlock generation.** Keep the current release locked unless the maintainer explicitly approves a release change. A future module should be developed and reviewed on its own branch.
- **Keep AI optional.** The existing career browser, quiz, deterministic matching, resume checker, profiles, and human-consultation workflows must continue to work without a model or AI API key.
- **Use a clear provider boundary.** Keep model transport, prompts, orchestration, and feature-specific business logic separate from Flask routes and templates. Do not scatter provider calls across page handlers.
- **Validate on the server.** Treat browser input and model output as untrusted. Validate request size, inputs, outputs, ownership, and authorization server-side.
- **Protect student data.** Send only the minimum necessary information to a provider, disclose external processing, avoid logging sensitive resume/chat content, and provide deletion/retention behavior. Never expose private records across users.
- **Keep generated output reviewable.** Label AI-generated guidance, show relevant source context where applicable, and avoid presenting career suggestions as eligibility, admission, salary, or employment guarantees.
- **Keep secrets out of Git.** Use environment configuration and update `.env.example` with placeholder names only. Never commit real API keys, SMTP passwords, database files, uploaded resumes, or personal data.
- **Add regression tests.** Cover enabled and disabled states, provider failures/timeouts, invalid output, rate limits, CSRF/auth checks, user ownership, and the no-provider/no-key path.
- **Make database changes additive.** Include migration tests and preserve existing users, career edits, consultations, and saved reviews.
- **Document setup and limitations.** State required services, environment variables, privacy implications, costs, and how to run the module locally.

Suggested branch names:

| Module | Example branch |
|---|---|
| AI career counselor | `feature/ai-career-counselor` |
| Mock interview practice | `feature/mock-interview` |
| Match explanations | `feature/match-explanations` |
| Quiz interpretation | `feature/ai-quiz-interpretation` |
| Resume feedback | `feature/ai-resume-feedback` |
| Consultation summaries | `feature/consultation-triage` |

A pull request should not claim a feature is available until it is implemented, tested, documented, and deliberately enabled in a reviewed release.

---

## Limitations

- Career profiles are editorial summaries, not a verified directory of institution admissions, licensing rules, or current job vacancies.
- Matching results are suggestions based on entered interests/skills, not guarantees of suitability or employment.
- The interest quiz is not a validated psychological assessment.
- Resume evaluation is a text heuristic, not a commercial ATS simulator, credential verifier, or proof of work history.
- Resume extraction may be imperfect for scanned PDFs and complex document layouts.
- AI-powered counselor, interview, explanation, quiz-interpretation, resume-rewriting, and consultation-triage features are not active in the current release.
- Optional email confirmations require the maintainer or deployer to configure SMTP credentials.

---

## Maintainer

**Yash Raj Bansal**  
GitHub: [@YashRajBansal](https://github.com/YashRajBansal)  
Project: [CareerGuru-ai](https://github.com/YashRajBansal/CareerGuru-ai)

If you find Career Guru useful, consider starring the repository and contributing improvements through a focused branch and pull request.
