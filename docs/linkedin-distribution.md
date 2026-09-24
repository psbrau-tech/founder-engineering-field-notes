# LinkedIn Distribution Contract

LinkedIn is not a shortened copy of the technical article. It is a founder-facing interpretation of the same verified lesson.

GitHub Pages remains the canonical technical record. DEV receives the technical syndication copy. LinkedIn should communicate why the lesson mattered to a founder or small technical team: what wasted time, why the diagnosis was difficult, what changed in the engineering system, and what another team can reuse.

## Audience

Write for technical founders, engineering leaders, consultants, and practitioners who understand software delivery but may not work daily in the specific platform or service involved.

A reader should understand the post without knowing the article title, private source incident, or platform-specific implementation details.

## Default post shape

Use this sequence when it fits the lesson:

1. **Founder-relevant opening:** Lead with the cost, risk, debugging trap, or engineering misconception.
2. **Concrete failure:** Explain what went wrong in plain language without private details.
3. **Wrong instinct:** Name the tempting diagnosis or fix when it is useful to the lesson.
4. **Root lesson:** Explain the actual failure class with only the technical detail needed to make the lesson credible.
5. **Permanent control:** State what preflight, regression check, process change, or observability improvement now catches the problem earlier.
6. **Reusable rule:** End with a principle another small team can apply.

## Editorial rules

- Prefer plain language over service-specific jargon.
- Use platform or API names only when they materially improve the lesson.
- Do not lead with an AWS action, IAM ARN, configuration key, framework flag, or other implementation detail.
- Do not turn the post into a mini runbook. The canonical article owns the detailed procedure.
- Do not use boilerplate such as “the field note covers...” or “read the article to learn...”. The post must stand on its own.
- Do not invent a dramatic time or cost figure. If the evidence only supports “wasted deployment cycles” or “slow diagnosis,” say that.
- Do not manufacture controversy, engagement bait, or a question solely to generate comments.
- Keep the founder perspective grounded in the actual lesson: wasted effort, hidden assumptions, better controls, automation boundaries, or improved recovery.
- Claims must remain within the evidence already accepted for the canonical article.
- Public/private sanitization rules apply unchanged.

## Length and formatting

Most posts should fit naturally in roughly 150–300 words. This is guidance, not a hard validation rule.

Use short paragraphs and whitespace for scanability. A short numbered sequence is appropriate when the sequence itself is the lesson. Bold may be used sparingly for the reusable rule.

The canonical article link belongs in the package as an optional element. The founder may include it in the post, add it separately, or omit it based on the publishing context. The LinkedIn post must still deliver useful value without requiring the click.

## Package format

Each `linkedin_ready: true` article should have `distribution/linkedin/<slug>.md` containing:

```markdown
# LinkedIn Package: <descriptive title>

## Post

<founder-facing post copy>

## Optional canonical link

https://psbrau-tech.github.io/founder-engineering-field-notes/articles/<slug>/
```

LinkedIn remains manually published. The repository prepares the copy so the recurring founder action is review, optional light personalization, and post.
