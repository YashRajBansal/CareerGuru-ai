# Career Guru — Complete AI, Feature, and UI/UX Overhaul

Act as a senior full-stack Flask engineer, AI application developer, UI/UX designer, and motion designer. Upgrade my diploma final-year project, **Career Guru**, into a polished, functional, AI-powered career-guidance platform.

Use the existing project as the foundation. This is a complete feature and visual overhaul, not a rewrite from scratch or a minor CSS refresh. Give equal priority to useful AI capabilities, reliable functionality, security, and exceptional design.

## 1. Inspect the project and preserve working features

Before editing, inspect the project structure, dependencies, routes, templates, assets, models, database setup, authentication, APIs, and configuration. Read repository instructions first. Map every existing user and admin screen, identify broken flows and design weaknesses, and distinguish implemented features from marketing claims.

The reported stack is Flask, Flask-SQLAlchemy with SQLite, Flask-Login, Flask-Bcrypt, Flask-Mail, Jinja templates, and a Bootstrap-based, Tabler-style admin kit. A MongoDB keyword-lookup chatbot reportedly exists, and an installed `openai` dependency is unused. Career recommendations, resume tools, and personality quizzes are reportedly advertised but unimplemented. Verify these statements against the actual code before acting.

Preserve and extend existing authentication, profiles, email integrations, database records, and consultation booking, including the human “book a professional” flow. Preserve existing route contracts wherever practical. Reuse suitable libraries and components; remove obsolete code only after its replacement works.

Briefly state the implementation sequence and material architecture decisions, then proceed with authorized work. Do not stop after providing a plan.

## 2. Security cleanup comes first

After the initial inspection, complete security cleanup before feature or visual implementation:

- Remove any hardcoded Gmail app password, Flask secret key, admin credentials, and committed API keys. Never print secret values in reports, logs, screenshots, or examples.
- Load secrets through environment variables, using `python-dotenv` for local development. Ensure `.env` is gitignored and provide `.env.example` with blank placeholders and configuration guidance.
- Explain which exposed credentials require rotation. Removing a secret from a file does not rotate it or remove it from Git history. Perform provider-side rotation only when authorized access is available; otherwise clearly record the required owner action. Do not rewrite Git history without approval.
- Replace hardcoded admin login with an `is_admin` flag on the existing User model, or justify another compatible approach. Use Flask-Login and bcrypt-hashed passwords. Protect every `/admin*` page and API server-side, and provide a secure admin provisioning method without default credentials or public privilege escalation.
- Add Flask-WTF CSRF protection to state-changing forms and browser requests, including asynchronous requests. Add Flask-Limiter limits to login, signup, chat, and other expensive AI endpoints as appropriate.
- Enforce user ownership of conversations, quiz results, resumes, interview sessions, profiles, and bookings. Validate inputs and use appropriate session-cookie settings for local and deployed environments.
- Render AI-generated Markdown safely. Restrict resume upload types and sizes, validate parsed content, and avoid logging sensitive document content.

## 3. Implement real, connected AI features

Build maintainable AI service modules rather than duplicating provider calls throughout route handlers. Configure provider credentials and model names through environment variables. Handle missing credentials, timeouts, rate limits, and provider failures with clear recovery states. Keep keys server-side and control request size, history length, and output length.

### Conversational career counselor

- Replace exact-match chatbot responses with an LLM-backed career counselor.
- Persist per-user conversations and support opening, continuing, and deleting conversation history.
- Ground answers through retrieval over the curated career dataset and managed knowledge base. Use retrieval-augmented generation rather than fine-tuning.
- Stream responses incrementally through a Flask-compatible transport, with typing feedback, safe Markdown rendering, message entrance animations, and interruption/error handling.
- Treat retrieved content as reference material, not instructions. Explain uncertainty and missing information without inventing facts or sources.
- Log unanswered, unsupported, or user-flagged queries into an admin queue with review and resolution states. Do not present uncalibrated model confidence as a reliable probability.

### Career dataset and recommendation engine

- Create roughly 75–150 hand-curated career profiles covering relevant career clusters.
- Include title, cluster, core skills, interests/traits, typical education paths, day-to-day work, and growth outlook. Record source/provenance where appropriate; qualify time-sensitive outlook claims instead of inventing statistics.
- Match a user's interests, skills, preferences, quiz results, and optional resume using embeddings and cosine similarity or a lightweight vector store appropriate to this dataset size.
- Provide ranked recommendations with concise LLM explanations grounded in the user profile and retrieved career data. Include strengths, skill gaps, and practical next steps.
- Label similarity scores accurately; do not imply they predict career success.
- Refresh embeddings when career or knowledge entries change. Keep seeding repeatable without duplicating or overwriting admin edits unexpectedly.
- Do not train a large classifier or add unnecessary infrastructure.

### Interest and personality quiz

Create an interactive, keyboard-accessible quiz with animated progress, clear questions, back/next controls, validation, and saved results. Feed responses directly into career matching. Use a transparent scoring rubric with AI-assisted interpretation, and explain the recommendations. Present it as a career exploration aid rather than a validated psychological assessment.

### Resume tools

Implement supported resume uploads, text extraction, an AI resume analyzer, actionable bullet-point rewrites, and career-fit checks. Explain the rubric behind any ATS-style score and identify parsing limitations. Preserve factual accuracy in suggested rewrites; never invent experience, skills, or achievements. Provide upload, processing, result, failure, and deletion states with clear privacy expectations.

### AI mock interviews

Build role-specific interview sessions grounded in a selected career profile, with question-by-question conversation and structured feedback on relevance, clarity, examples, strengths, and improvement areas. Save interview history and offer practical follow-up exercises. Keep human consultation booking available as a complementary path.

## 4. Turn the admin area into a working management product

- Build an analytics dashboard with signup growth, career demand, unanswered-query volume, and booking trends, using real database-backed metrics and useful date filters.
- Add animated charts, count-up statistics, loading skeletons, and honest empty/error states. Refresh metrics from backend endpoints; do not invent analytics to fill charts.
- Provide full CRUD for career profiles and chatbot knowledge entries, including search, validation, and embedding refresh status.
- Add search, filters, sorting, pagination, exports, and appropriate bulk actions to user and consultation tables. Protect destructive operations and prevent accidental removal of the last administrator.
- Provide a resolvable queue for unanswered or flagged chatbot requests.
- Record admin actions in an audit log with actor, action, target, and timestamp, without leaking secrets or unnecessary personal data.
- Generate AI-assisted consultation summaries and reviewable urgency tags for triage. Show when AI processing is unavailable and allow human correction.
- Use drag-and-drop only where ordering has a real purpose, persist changes, and provide keyboard alternatives.

## 5. Redesign the complete experience

Choose a cohesive visual direction suited to students exploring careers: confident, welcoming, clear, and credible. Take initiative on design decisions without repeatedly asking for preferences.

Transform every existing screen and every newly implemented flow, including the landing page, authentication, user dashboard, profiles/settings, career discovery and detail pages, chat, quiz/results, resume tools, mock interviews, consultation booking, admin dashboards, management tables, and error pages. Audit the actual route inventory so no existing page is left behind.

Build a reusable design system with CSS variables for colors, typography, spacing, radii, shadows, and motion. Apply it consistently through Jinja layouts, macros, and shared components.

Include strong typography, thoughtful hierarchy, balanced spacing, distinctive navigation, elegant cards, restrained gradients or background textures, professional icons, and polished buttons and form controls. Design loading, empty, success, validation, error, and disabled states deliberately. Avoid generic template styling, excessive decoration, unsupported claims, and invented testimonials or business metrics.

Provide a persistent dark/light theme toggle across public, user, and admin pages. Respect system preference initially, maintain readable contrast in both themes, and avoid a flash of the wrong theme during loading.

## 6. Make interactions meaningful and motion intentional

Keep Flask, Jinja, and Bootstrap as the default architecture. Prefer existing Bootstrap behavior, CSS transitions, and focused vanilla JavaScript. Add a lightweight animation or chart library only when it materially improves the result. Do not introduce React or Framer Motion solely to add animations.

Implement purposeful interactions where relevant:

- Functional search, filters, sorting, tabs, dropdowns, mobile navigation, accordions, modals, and tooltips.
- Responsive hover/press feedback on cards, buttons, and navigation.
- Scroll reveals and staggered entrances that never hide essential content if JavaScript fails.
- Smooth quiz transitions, progress feedback, streaming chat, and animated chart updates.
- Toasts and inline feedback tied to actual action outcomes, plus copy-to-clipboard where useful.
- Subtle page transitions that preserve browser navigation, focus, form behavior, and accessibility.

Every visible control must perform a meaningful action. Do not ship fake buttons, decorative filters, fabricated responses, or success messages without completed operations. Avoid excessive motion, respect `prefers-reduced-motion`, and maintain responsive performance.

## 7. Responsiveness, accessibility, and reliability

Optimize desktop, laptop, tablet, and mobile layouts. Prevent unintended horizontal overflow, make tables usable on small screens, keep text readable, and provide touch-friendly targets. Ensure long messages, uploaded filenames, charts, modals, and dropdowns behave well on narrow screens.

Use semantic HTML, visible focus states, explicit form labels, accessible validation, keyboard navigation, sufficient contrast, and appropriate screen-reader announcements. Manage modal focus and announce streaming chat without overwhelming assistive technology. Never make essential actions hover-only.

Keep assets efficient, avoid duplicate dependencies and unnecessary work, and preserve server-rendered functionality where practical. Document local SQLite limitations and any production configuration needs without forcing a stack migration.

## 8. Decision boundaries

Proceed autonomously with visual direction, component styling, layouts, animation choices, and ordinary implementation details within this stack. Briefly flag material architectural choices and explain their tradeoffs before implementation.

Ask before replacing Flask/Jinja with a SPA, changing the primary database, adding substantial external infrastructure or paid services, performing destructive migrations, rewriting Git history, or removing a working feature. While such a decision is pending, continue independent work that is already authorized. Prefer the smallest maintainable approach compatible with the project.

## 9. Verify the complete product

Run the application and appropriate checks. Test authentication and admin authorization, CSRF and rate limits, user data isolation, existing profiles and bookings, migrations and seeding, career retrieval, quiz-to-recommendation flow, resume processing, interview feedback, and admin operations.

Exercise AI success, unavailable-provider, and failure paths. Use isolated test fixtures or explicit test stubs where needed, and never disguise them as production functionality. Do not claim a live provider integration was verified without credentials and a successful request.

Inspect every page in the browser, verify meaningful controls, navigation, responsive layouts, both themes, keyboard interactions, reduced motion, and browser console/network errors. Fix discovered regressions and remove unused code introduced during the overhaul.

If the environment prevents a required check, state exactly what could not be verified and why. Do not describe untested features as complete or claim production readiness without evidence.

## 10. Deliverables

Deliver the implemented codebase, updated `requirements.txt`, safe `.env.example`, repeatable database migrations and seed instructions, curated dataset, reusable UI components, and relevant automated checks.

Update the README with local setup, configuration, migration/seeding commands, secure admin provisioning, feature usage, AI architecture, upload/data-retention behavior, limitations, and test commands. Summarize what changed, what was verified, and any remaining owner actions such as credential rotation.

The final result should be a cohesive, visually impressive, animated, responsive Career Guru application whose AI features and interactions actually work. Complete the implementation rather than delivering only suggestions, mockups, or disconnected screens.
