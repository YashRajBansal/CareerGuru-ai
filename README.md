# Career Guru

A diploma career-guidance application built on the original **Flask, Jinja, Bootstrap, Flask-Login, bcrypt, Flask-Mail and SQLite** foundation. The application now has a shared responsive interface, light/dark themes, keyboard-friendly controls, reduced-motion support, animated feedback and real database-backed workflows.

## Run locally (Windows PowerShell)

The included `app/venv` environment has been updated on this computer. From this folder:

```powershell
.\Start-CareerGuru.ps1
```

Open [Career Guru](http://127.0.0.1:5001). The launcher creates missing local configuration, runs the additive migration and starts Flask without debug mode. It does not delete existing records.

For a fresh checkout, use Python 3.12 or newer:

```powershell
cd app
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe setup_local.py
.\venv\Scripts\python.exe -m flask --app app init-db
.\venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5001
```

Create your student account at `/signup`. There are **no default production users or admin credentials**. Existing usernames and bcrypt password hashes are retained.

## Current release: available tools and locked future features

The default interface now uses a charcoal, graphite and neutral grey palette. The theme toggle switches between charcoal dark mode and a neutral grey light mode. Existing browsers switch to the new default once, then remember subsequent theme choices.

Available now, without any model or AI API key:

- Career browsing, filtering, saved paths and local cosine-similarity matching.
- The 12-question interest quiz, transparent scoring and career recommendations.
- Resume text extraction, career-specific scoring, skill-evidence checks and a separate presentation-quality rubric.
- Profiles, consultation requests, staff email confirmations and all ordinary admin management.
- Local text-index rebuilding, analytics, exports, review queues and audit logs.

**Locked as future features:** AI career counseling, AI mock interviews, generated match explanations, AI interest interpretation, resume feedback/bullet rewriting and consultation auto-summary/urgency tagging.

Clicking a locked feature opens a **Future feature** dialog. Direct counselor/interview URLs display a coming-soon page. Generation requests are also blocked on the server: `/api/chat` returns HTTP 501 with `future_feature: true`; direct AI-triage submissions show the same release-lock message. Ordinary quiz, matching, resume and booking submissions skip all generation calls. Locked clicks do not create conversations or review-queue entries.

The release lock is enforced by `GENERATION_LOCKED = True` in `app/services/ai.py`. It remains active even if Ollama is installed or a model is configured. There is no environment variable or admin switch that enables these features in this release. **You do not need to install a model.** The dormant local-only adapter is retained for a future development release and its transport is tested separately. No OpenAI SDK, API key configuration or API calls are present.

My matches accepts comma-separated interests such as `cricket, drawing, computers` and technical skills such as `CAD, material testing`. Simple suggestion chips help build the list. Each entry is scored against career titles, skills and traits; everyday terms such as coding and building design are mapped to relevant vocabulary. Typed interests determine the candidates; quiz results only break equally relevant ties. Cricket ranks Cricketer first, and CAD plus material testing ranks Civil Engineer first. Matches and their matching interests appear above the input form. These are exploration suggestions, not eligibility or employment predictions. No language model is used. Admin edits take effect immediately. **Rebuild local text index** caches current vectors in SQLite with document fingerprints and makes no network request. The `refresh-embeddings` CLI name is retained as a compatibility alias for this offline rebuild.

Configuration in `app/.env.example`:

- `SECRET_KEY`: generated locally by `setup_local.py`, without printing it.
- `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`: optional SMTP credentials for human consultation confirmations.
- `DATABASE_URL`: defaults to `app/instance/users.db`.
- `COOKIE_SECURE=true` for an HTTPS deployment; false for local HTTP.
- `RATELIMIT_STORAGE_URI`: memory storage for single-process development; use a shared supported store for multiple workers.
- `OLLAMA_URL` / `OLLAMA_MODEL`: reserved for future development; they do not bypass the release lock.

## Administrator setup and sign-in

Admin address: [http://127.0.0.1:5001/admin](http://127.0.0.1:5001/admin).

There are **no default admin credentials**. Student signup cannot grant administrator access. To create a new admin, open PowerShell in this project folder and run:

```powershell
cd app
.\venv\Scripts\python.exe -m flask --app app create-admin
```

Enter a new username, email address and a password of at least 12 characters when prompted. Password input is hidden. The command creates an account with `is_admin=True` and a bcrypt password hash; it refuses to silently promote an existing account.

1. Start the app if needed (`.\Start-CareerGuru.ps1` from the project root).
2. Open [Sign in](http://127.0.0.1:5001/login) and use the admin credentials you created.
3. Admin sign-in redirects to `/admin`. You can also use **Admin sign in** in the public footer.
4. Use the management sidebar for the career library, knowledge base, users, consultations, review queue and audit log.

If `/admin` shows **403**, you are signed in as a student: sign out, then sign in with the admin account. If you have no admin account yet, use the command above. No database record needs to be edited manually.

Administrators can manage careers and knowledge, reorder the library, rebuild the local text index, search/filter/export records, apply bulk actions, resolve review queries and inspect audit logs. Charts use real database activity. Legacy users without signup dates are labeled as legacy records. AI consultation triage is visibly locked as a future feature; staff can still review requests and update their status manually.

## What is implemented

- **Career library:** 80 individually scoped editorial profiles, covering technology, design, engineering, health, education, business, built environment, science, hospitality, trades and sport. No invented salary or demand statistics. Profiles explain skills, interests, entry pathways, daily work and regional uncertainty. These are editorial exploration summaries, not a verified admissions directory; check qualification and licensing requirements locally.
- **Recommendations:** interests + latest quiz feed a bounded retrieval service. Matches appear first, with the interests that connect to each career. Comma-separated interests are evaluated individually using title/skill weighting and local similarity. Simple suggestions include cricket, coding, drawing and building design. Generated explanations remain locked as a future feature.
- **Interest quiz:** 12 questions, 1–5 responses, back/next controls, saved browser draft, progress feedback and six transparent interest scores out of 10. Generated interpretations are locked as a future feature. It is not a validated psychological assessment.
- **Career counselor:** locked as a future feature. Existing private conversation records remain stored; no generation requests run in this release.
- **Resume studio:** PDF/DOCX/TXT extraction or pasted text; career-specific scoring with task evidence, unsupported-claim deductions and a separate presentation rubric. Each target skill is marked supported in text, listed without task evidence or not found. Short supporting excerpts and actionable improvements are saved. AI rewriting remains locked as a future feature. This is not a commercial ATS simulator or a verifier of claims; scanned PDFs require OCR and complex layouts may extract imperfectly.
- **Mock interviews:** locked as a future feature, with a coming-soon dialog and a direct-link fallback page.
- **Human consultations:** original booking fields retained, user-owned requests, cancellation, manual admin review/status management and mail confirmation.
- **Profiles/authentication:** existing fields retained, optional birthday handling, duplicate validation, bcrypt passwords, normalized email, image verification/re-encoding and persistent avatars.

## How the resume checker scores a selected career

The main score is **career fit based on the text**, not formatting quality. A polished technology resume may have high presentation quality and low fit for Civil Engineer.

| Component | Maximum points |
| --- | ---: |
| Target skills mentioned (with tool/term aliases) | 25 |
| Supporting tasks behind target skills | 40 |
| Relevant project or experience tasks | 20 |
| Resume presentation | 15 |

A skill listed without a concrete supporting task loses **4 points**, up to **20 points** in total. Repeated descriptions can lose 10 points; dense repeated keyword lists can lose 8. Keywords, project titles alone, certificates without applied tasks and future plans do not earn task-evidence points. Evidence requires an action and a specific task or output, linked to the relevant skill in project/experience text. Real scope or measured outcomes can strengthen that evidence; numbers alone cannot prove a skill.

The checker applies evidence limits: no target skills found caps the score at 25; target skills without supporting tasks caps it at 45; fewer than half of target skills supported caps it at 60. Scores are rounded after deductions and limits. Missing skills earn zero rather than being assumed present. Selecting no career produces a clearly labeled general quality-and-evidence review, not a field-fit score.

The separate presentation rubric covers contact information, education, skills clarity, substantive task descriptions, scope/outcomes, readable length and distinct content. It is the same for the same text regardless of target career and contributes only 15 points to career fit.

Older saved reviews remain unchanged and are labeled **legacy quality only**. Their former 87/100 or similar score must not be interpreted as career fit. Resubmit the original resume to use the new scoring; the application cannot reconstruct text it never stored.

This is a deterministic English-language text heuristic. It checks whether the resume contains supporting detail, not whether the work, numbers or credentials are authentic. It can miss valid evidence due to wording, section structure or extraction. Review the excerpts and deductions and include only genuine experience. No model or cloud service runs for these checks.

## Migration and data preservation

`migrations.py` adds columns to the original `user` and `professional` tables and creates the new feature tables. Before changing a legacy SQLite database it saves `users.pre-upgrade.db` beside it. Re-running `init-db` does not duplicate the dataset or overwrite admin edits. The base catalog is seeded only when the career table is empty. A recorded, one-time catalog update adds Cricketer and Civil Engineer to existing installations without changing other entries. Once that update is recorded, deleting or editing these new entries in admin is respected on later starts. If you deliberately empty the entire career table, the next initialization seeds the base catalog again.

Legacy consultations remain visible to administrators. They are not assigned to a user based only on an email address. New bookings record the authenticated owner. The old MongoDB chatbot data is left untouched; the application no longer requires MongoDB. If existing Mongo knowledge is needed, review and import it through the managed knowledge UI.

The original destructive `main.py` reset behavior has been removed. `main.py` now starts the app safely. Legacy user/admin routes remain available where practical; deletion and logout actions now require CSRF-protected POST requests. Old templates/assets are retained for reference but are no longer served by the refreshed routes.

## Privacy and security

The original source contained exposed credentials. The local session key has been replaced, and the API/mail passwords have been removed from active configuration and source. **The owner must revoke the previously exposed AI API key and Gmail app password through their provider accounts. The AI API key is no longer needed by this application; only optional SMTP needs replacement credentials. File removal does not revoke them or remove copies from Git history or prior backups.** No provider account rotation or history rewrite was performed.

All browser mutations use Flask-WTF CSRF checks; login/signup and expensive AI endpoints are rate limited. All administrator pages and legacy aliases enforce Flask-Login roles. Private AI records are checked for user ownership. User exports omit password hashes and escape spreadsheet formulas. AI Markdown is rendered through text-node-based formatting; raw HTML cannot execute.

Original resume uploads and full extracted text are not saved. Scores and selected short evidence excerpts are saved in private reviews and can be deleted. Model-powered processing is release-locked; extracted resume text is not sent to a model or cloud AI service. Saved reports may contain rewritten excerpts and can be deleted. Chat messages, quiz responses and consultation details persist in SQLite. Keep the database, backups and uploads private; the generated `.gitignore` excludes them. Profile images are served by their generated URL and should not be treated as confidential storage. Use HTTPS, a production WSGI server, a private database volume and a shared rate-limit store before deployment. Flask's built-in server is for local development.

## Verification

```powershell
cd app
.\venv\Scripts\python.exe -m pytest tests -q
```

Tests use an in-memory database with disposable fixture users. They cover original route rendering, authentication, password hashing, CSRF, admin access, private-record ownership, recommendations, quiz validation, resume parsing/deletion, consultation ownership, stream persistence/failure, provider setup states, admin CRUD/reorder/audits and rate limits. Release-lock tests assert that all model-dependent flows stay blocked even with a configured model. Dormant local-model responses are stubbed for future transport regression tests; tests do not require a downloaded model or send email. Transport tests cover native completion/stream parsing, interruption handling, and rejection of external hosts, credentials and cloud model names.

For an isolated browser preview, `python tests/browser_server.py` runs localhost port 5002 using a temporary database and explicitly test-only fixture accounts. It does not open `users.db` and is not a deployment entry point.

Local model integration: [Ollama native chat API](https://docs.ollama.com/api/chat).
