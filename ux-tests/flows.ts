/**
 * UX test flow definitions — real user journeys across Browser Use sites.
 *
 * Each flow describes a natural user scenario that Browser Use executes
 * in a real browser session, then evaluates the experience via structured output.
 */
import { z } from "zod";

// ── Shared schemas ──────────────────────────────────────────────────────────

export const UxResult = z.object({
  passed: z.boolean().describe("Whether the flow completed successfully"),
  score: z
    .number()
    .min(1)
    .max(10)
    .describe("UX quality score from 1 (terrible) to 10 (perfect)"),
  pageLoadFeeling: z
    .enum(["fast", "acceptable", "slow", "broken"])
    .describe("Perceived page load speed"),
  issues: z
    .array(z.string())
    .describe("List of UX issues found (empty if none)"),
  suggestions: z
    .array(z.string())
    .describe("Actionable improvement suggestions (empty if none)"),
  summary: z.string().describe("One-paragraph summary of the experience"),
});

export type UxResult = z.infer<typeof UxResult>;

export interface UxFlow {
  /** Short name for reporting. */
  name: string;
  /** Which site this flow targets. */
  site: "browser-use.com" | "cloud.browser-use.com" | "docs.browser-use.com";
  /** Natural-language task instruction for Browser Use. */
  task: string;
}

// ── Flows ───────────────────────────────────────────────────────────────────

export const flows: UxFlow[] = [
  // ── browser-use.com (marketing site) ──────────────────────────────────
  {
    name: "homepage-first-impression",
    site: "browser-use.com",
    task: `Go to https://browser-use.com. Evaluate the homepage as a first-time visitor:
- Does the page load quickly and render correctly?
- Is the value proposition immediately clear?
- Are the CTAs visible and compelling?
- Is the design modern and professional?
- Check for broken images, layout shifts, or visual glitches.
- Try scrolling through the entire page.
Report any UX issues you find.`,
  },
  {
    name: "homepage-navigation",
    site: "browser-use.com",
    task: `Go to https://browser-use.com. Test the navigation:
- Click through each item in the main navigation menu.
- Verify each link loads a proper page (no 404s, no broken content).
- Check that the navigation is consistent across pages.
- Test the mobile responsiveness by noting if elements overlap or break.
- Go back to the homepage using the logo/brand link.
Report any broken links, confusing navigation, or UX issues.`,
  },
  {
    name: "pricing-page-clarity",
    site: "browser-use.com",
    task: `Go to https://browser-use.com/pricing. Evaluate the pricing page:
- Are the pricing tiers clearly differentiated?
- Is it obvious what each plan includes?
- Are the CTAs clear (sign up, contact sales, etc.)?
- Is the pricing easy to understand at a glance?
- Check for any confusing or missing information.
Report any UX issues with the pricing presentation.`,
  },

  // ── docs.browser-use.com (documentation) ──────────────────────────────
  {
    name: "docs-quickstart",
    site: "docs.browser-use.com",
    task: `Go to https://docs.browser-use.com. As a new developer:
- Find the quickstart or getting started guide.
- Can you find installation instructions within 2 clicks?
- Are code examples visible and properly formatted?
- Is there a clear path from "I just arrived" to "I can run my first task"?
- Check that code blocks have copy buttons and syntax highlighting.
Report any issues that would slow down a new developer.`,
  },
  {
    name: "docs-search",
    site: "docs.browser-use.com",
    task: `Go to https://docs.browser-use.com. Test the search functionality:
- Look for a search bar or search shortcut (Cmd/Ctrl+K).
- Search for "authentication" or "API key".
- Are the results relevant and well-organized?
- Click on a search result — does it navigate correctly?
- Search for "streaming" — are the results helpful?
Report any issues with search discoverability or result quality.`,
  },
  {
    name: "docs-navigation-depth",
    site: "docs.browser-use.com",
    task: `Go to https://docs.browser-use.com. Test the sidebar navigation:
- Is the sidebar well-organized with clear categories?
- Navigate to an API reference page — are endpoints documented with examples?
- Check that links between related pages work (e.g., "see also" links).
- Navigate 3 levels deep into the docs — can you still orient yourself?
- Check breadcrumbs or other wayfinding aids.
Report any navigation confusion or broken links.`,
  },

  // ── cloud.browser-use.com (app / dashboard) ───────────────────────────
  {
    name: "cloud-landing",
    site: "cloud.browser-use.com",
    task: `Go to https://cloud.browser-use.com. Evaluate the landing/login experience:
- Does the page load quickly?
- Is the login/signup flow clear and accessible?
- Are there any visual glitches or layout issues?
- Is the branding consistent with the main site?
- Check for any error messages or broken elements.
Do NOT attempt to log in with credentials — just evaluate the public-facing UX.
Report any issues.`,
  },

  // ── Cross-site journeys ───────────────────────────────────────────────
  {
    name: "marketing-to-docs",
    site: "browser-use.com",
    task: `Start at https://browser-use.com. Simulate a developer's journey:
1. Read the homepage to understand what Browser Use does.
2. Find and click the link to documentation.
3. Verify the docs page loads and is the official documentation site.
4. Find the quickstart or getting started section.
5. Check that the transition between sites feels seamless (consistent branding, no jarring changes).
Report any friction in the marketing-to-docs journey.`,
  },
  {
    name: "marketing-to-signup",
    site: "browser-use.com",
    task: `Start at https://browser-use.com. Simulate a user wanting to sign up:
1. Find the main CTA to get started or sign up.
2. Click it and note where it takes you.
3. Is the signup/onboarding path clear?
4. How many clicks from homepage to starting the signup flow?
5. Is the transition to cloud.browser-use.com smooth?
Do NOT enter any credentials — just evaluate the funnel UX.
Report any friction or confusion in the signup journey.`,
  },
];
