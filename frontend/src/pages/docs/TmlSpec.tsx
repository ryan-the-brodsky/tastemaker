/**
 * TML (Taste Markup Language) specification documentation.
 */
export default function TmlSpec() {
  return (
    <article className="prose prose-slate max-w-none">
      <h1>Taste Markup Language (TML) Specification</h1>

      <p className="lead">
        TML is TasteMaker's machine-readable format for encoding UI/UX taste preferences.
        It enables AI agents to apply design rules deterministically.
      </p>

      <h2>Overview</h2>
      <p>
        TML captures the output of a TasteMaker extraction session as a structured JSON file
        that AI coding tools can parse, validate against, and generate from.
      </p>

      <h2>File Structure</h2>
      <p>The canonical TML format is <code>rules.json</code>:</p>

      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`{
  "version": "1.0",
  "generated": "2026-01-07T12:00:00Z",
  "rules": [
    {
      "id": "btn-001",
      "component": "button",
      "property": "border_radius",
      "operator": ">=",
      "value": 8,
      "severity": "error",
      "confidence": 0.92,
      "source": "extracted",
      "message": "Buttons must have border-radius of at least 8px"
    }
  ]
}`}
      </pre>

      <h2>Rule Properties</h2>
      <table className="w-full">
        <thead>
          <tr>
            <th>Property</th>
            <th>Type</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>id</code></td>
            <td>string</td>
            <td>Unique identifier for the rule</td>
          </tr>
          <tr>
            <td><code>component</code></td>
            <td>string | null</td>
            <td>Component type (button, input, card, etc.) or null for global rules</td>
          </tr>
          <tr>
            <td><code>property</code></td>
            <td>string</td>
            <td>CSS property or design token being constrained</td>
          </tr>
          <tr>
            <td><code>operator</code></td>
            <td>string</td>
            <td>Comparison operator: =, !=, &gt;, &lt;, &gt;=, &lt;=, contains, not_contains</td>
          </tr>
          <tr>
            <td><code>value</code></td>
            <td>any</td>
            <td>Expected value or threshold</td>
          </tr>
          <tr>
            <td><code>severity</code></td>
            <td>string</td>
            <td>error, warning, or info</td>
          </tr>
          <tr>
            <td><code>confidence</code></td>
            <td>number</td>
            <td>0-1 confidence score from extraction</td>
          </tr>
          <tr>
            <td><code>source</code></td>
            <td>string</td>
            <td>extracted (from A/B), stated (user-defined), or baseline (WCAG/Nielsen)</td>
          </tr>
          <tr>
            <td><code>message</code></td>
            <td>string</td>
            <td>Human-readable description of the rule</td>
          </tr>
        </tbody>
      </table>

      <h2>Component Types</h2>
      <p>TasteMaker v1 supports 8 component types:</p>
      <ul>
        <li><strong>button</strong> - Buttons and CTAs</li>
        <li><strong>input</strong> - Form inputs and text fields</li>
        <li><strong>card</strong> - Card containers</li>
        <li><strong>typography</strong> - Text and headings</li>
        <li><strong>navigation</strong> - Nav bars and menus</li>
        <li><strong>form</strong> - Form layouts</li>
        <li><strong>feedback</strong> - Toasts, alerts, notifications</li>
        <li><strong>modal</strong> - Dialogs and overlays</li>
      </ul>

      <h2>Rule Sources</h2>
      <h3>Extracted Rules</h3>
      <p>
        Derived from user's A/B comparison choices. These have confidence scores
        based on consistency of choices.
      </p>

      <h3>Stated Rules</h3>
      <p>
        Explicitly added by the user, e.g., "never use gradients". These always
        have 100% confidence.
      </p>

      <h3>Baseline Rules</h3>
      <p>
        WCAG accessibility and Nielsen usability heuristics. Applied as defaults
        unless overridden.
      </p>

      <h2>Using TML with AI Tools</h2>
      <p>
        Include the TML file in your project and reference it in prompts:
      </p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`"When generating UI components, follow the rules in rules.json.
For buttons, ensure border-radius >= 8px (rule btn-001).
Use the specified color palette for all components."`}
      </pre>

      <h2>Validation</h2>
      <p>
        Use the included <code>audit.py</code> script to validate components:
      </p>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
{`python scripts/audit.py --screenshot ./my-app.png`}
      </pre>
    </article>
  );
}
