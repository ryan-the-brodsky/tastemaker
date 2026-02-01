/**
 * Claude Code integration guide.
 */
export default function ClaudeCodeGuide() {
  return (
    <article className="prose prose-slate max-w-none">
      <h1>Claude Code Integration</h1>

      <p className="lead">
        Use your TasteMaker skill package with Claude Code for consistent,
        on-brand UI component generation.
      </p>

      <h2>Quick Start</h2>

      <h3>1. Download Your Skill Package</h3>
      <p>
        After completing your TasteMaker extraction session, download the skill
        package ZIP file.
      </p>

      <h3>2. Extract to Your Project</h3>
      <p>
        Extract the ZIP file into your project directory. The recommended location
        is at the project root:
      </p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`my-project/
├── tastemaker-yourname/
│   ├── SKILL.md
│   ├── references/
│   │   ├── rules.json
│   │   ├── baseline.md
│   │   └── ...
│   └── scripts/
│       └── audit.py
├── src/
└── package.json`}
      </pre>

      <h3>3. Reference in Claude Code</h3>
      <p>
        Claude Code automatically detects SKILL.md files in your project.
        When asking Claude to generate components, it will follow your style rules.
      </p>

      <h2>Example Usage</h2>

      <h3>Generating Components</h3>
      <p>Simply ask Claude Code to create components:</p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`"Create a primary button component following my TasteMaker style guide"`}
      </pre>
      <p>Claude will reference your rules.json and generate code that matches your preferences.</p>

      <h3>Auditing Existing Components</h3>
      <p>Ask Claude to check components against your rules:</p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`"Review this button component against my TasteMaker rules and suggest fixes"`}
      </pre>

      <h2>Best Practices</h2>

      <h3>Keep SKILL.md Updated</h3>
      <p>
        If you refine your preferences in TasteMaker, download a new skill package
        and replace the existing one.
      </p>

      <h3>Reference Specific Rules</h3>
      <p>
        For precise control, reference specific rule IDs:
      </p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`"Ensure this component follows rule btn-001 (minimum border-radius)"`}
      </pre>

      <h3>Use with Component Libraries</h3>
      <p>
        TasteMaker rules work well with component libraries like shadcn/ui.
        Ask Claude to apply your style tokens to existing components:
      </p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`"Update the shadcn Button component to match my TasteMaker color palette"`}
      </pre>

      <h2>Troubleshooting</h2>

      <h3>Claude Not Finding SKILL.md</h3>
      <p>
        Ensure the file is named exactly <code>SKILL.md</code> and is in a
        directory that Claude Code can access.
      </p>

      <h3>Rules Not Being Applied</h3>
      <p>
        Be explicit in your prompts: mention "TasteMaker rules" or "my style guide"
        to ensure Claude references the skill package.
      </p>
    </article>
  );
}
