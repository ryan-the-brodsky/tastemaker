/**
 * Cursor IDE integration guide.
 */
export default function CursorGuide() {
  return (
    <article className="prose prose-slate max-w-none">
      <h1>Cursor Integration</h1>

      <p className="lead">
        Use your TasteMaker skill package with Cursor IDE for AI-powered
        code generation that follows your design preferences.
      </p>

      <h2>Quick Start</h2>

      <h3>1. Download Your Skill Package</h3>
      <p>
        Complete your TasteMaker extraction session and download the skill
        package ZIP file.
      </p>

      <h3>2. Add to Your Project</h3>
      <p>
        Extract the skill package into your project. Place it in a location
        Cursor can index:
      </p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`my-project/
├── .cursor/
│   └── rules/
│       └── tastemaker-yourname/
│           ├── SKILL.md
│           └── references/
├── src/
└── package.json`}
      </pre>

      <h3>3. Configure Cursor Rules</h3>
      <p>
        Add a reference to your skill in <code>.cursorrules</code>:
      </p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`# .cursorrules
When generating UI components, follow the style rules defined in:
.cursor/rules/tastemaker-yourname/SKILL.md

Key rules to always apply:
- Use the color palette from references/rules.json
- Follow component-specific rules in references/*.md
- Include agent-handle attributes on interactive elements`}
      </pre>

      <h2>Using with Cursor Chat</h2>

      <h3>Component Generation</h3>
      <p>In Cursor Chat (Cmd+K), reference your style guide:</p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`Create a card component following my TasteMaker style guide.
Use the colors and spacing from my rules.json file.`}
      </pre>

      <h3>Code Review</h3>
      <p>Ask Cursor to review components against your rules:</p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`Review this form component against my TasteMaker rules.
Check for violations in spacing, colors, and border-radius.`}
      </pre>

      <h2>Using with Cursor Composer</h2>
      <p>
        When using Composer for larger changes, include your skill package
        in the context:
      </p>
      <ol>
        <li>Select the files you're working with</li>
        <li>Add <code>SKILL.md</code> and relevant <code>references/*.md</code> files</li>
        <li>Describe your task, referencing the style guide</li>
      </ol>

      <h2>Inline Assistance</h2>
      <p>
        Use Cursor's inline assist (Cmd+L) to apply rules to specific code:
      </p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`// Select your button code, then ask:
"Update this button to match my TasteMaker primary button style"`}
      </pre>

      <h2>Best Practices</h2>

      <h3>Index Your Skill Package</h3>
      <p>
        Ensure Cursor indexes your skill package by placing it in a non-ignored
        directory. Check that <code>.gitignore</code> doesn't exclude it.
      </p>

      <h3>Use @-mentions</h3>
      <p>
        In Cursor Chat, use @-mentions to explicitly reference files:
      </p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`@SKILL.md @references/buttons.md Create a secondary button`}
      </pre>

      <h3>Keep Rules Updated</h3>
      <p>
        When you update your TasteMaker profile, download a fresh skill package
        and replace the existing one in your project.
      </p>

      <h2>Troubleshooting</h2>

      <h3>Rules Not Being Applied</h3>
      <ul>
        <li>Verify the skill package is in an indexed directory</li>
        <li>Explicitly reference SKILL.md in your prompts</li>
        <li>Check that .cursorrules is properly configured</li>
      </ul>

      <h3>Conflicting Styles</h3>
      <p>
        If Cursor generates styles that conflict with your rules, be more
        specific in your prompt and reference the exact rule ID.
      </p>
    </article>
  );
}
