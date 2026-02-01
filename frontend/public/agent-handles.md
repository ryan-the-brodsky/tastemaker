# TasteMaker Agent Handles Documentation

This document describes all available `agent-handle` attributes in the TasteMaker application. These handles provide stable selectors for automated testing and AI-driven interactions.

## Overview

Agent handles follow the naming convention: `{context}-{component}-{element}-{identifier}`

Use CSS selector `[agent-handle="handle-name"]` to target elements.

---

## Landing Page (`/`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `landing-hero-button-getstarted` | Button | Primary CTA to navigate to registration |
| `landing-hero-button-login` | Button | Secondary CTA to navigate to login |

### Example Usage
```javascript
// Click Get Started button
await page.click('[agent-handle="landing-hero-button-getstarted"]');
```

---

## Authentication Pages

### Login Page (`/login`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `auth-login-input-email` | Input | Email address input field |
| `auth-login-input-password` | Input | Password input field |
| `auth-login-button-submit` | Button | Submit login form |

### Example Usage
```javascript
// Complete login flow
await page.fill('[agent-handle="auth-login-input-email"]', 'user@example.com');
await page.fill('[agent-handle="auth-login-input-password"]', 'password123');
await page.click('[agent-handle="auth-login-button-submit"]');
```

### Registration Page (`/register`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `auth-register-input-email` | Input | Email address input |
| `auth-register-input-password` | Input | Password input (min 8 chars) |
| `auth-register-input-confirmpassword` | Input | Password confirmation input |
| `auth-register-input-firstname` | Input | User's first name |
| `auth-register-input-lastname` | Input | User's last name |
| `auth-register-button-submit` | Button | Submit registration form |

### Example Usage
```javascript
// Complete registration flow
await page.fill('[agent-handle="auth-register-input-firstname"]', 'John');
await page.fill('[agent-handle="auth-register-input-lastname"]', 'Doe');
await page.fill('[agent-handle="auth-register-input-email"]', 'john@example.com');
await page.fill('[agent-handle="auth-register-input-password"]', 'securepass123');
await page.fill('[agent-handle="auth-register-input-confirmpassword"]', 'securepass123');
await page.click('[agent-handle="auth-register-button-submit"]');
```

---

## Dashboard Page (`/dashboard`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `dashboard-sessions-button-create` | Button | Open new session creation form |
| `dashboard-sessions-card-{sessionId}` | Div | Session card container (dynamic ID) |
| `dashboard-sessions-button-continue-{sessionId}` | Button | Continue specific session (dynamic ID) |

### Example Usage
```javascript
// Create a new session
await page.click('[agent-handle="dashboard-sessions-button-create"]');

// Continue an existing session (e.g., session ID 1)
await page.click('[agent-handle="dashboard-sessions-button-continue-1"]');
```

---

## Extraction Session Page (`/session/{id}`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `extraction-comparison-option-a` | Div | Left comparison option (clickable) |
| `extraction-comparison-option-b` | Div | Right comparison option (clickable) |
| `extraction-comparison-button-nopreference` | Button | Indicate no preference between options |
| `extraction-progress-indicator` | Div | Shows current phase and progress |

### Example Usage
```javascript
// Make comparison choices
await page.click('[agent-handle="extraction-comparison-option-a"]'); // Choose A
// or
await page.click('[agent-handle="extraction-comparison-option-b"]'); // Choose B
// or
await page.click('[agent-handle="extraction-comparison-button-nopreference"]'); // Skip

// Check progress
const progress = await page.textContent('[agent-handle="extraction-progress-indicator"]');
```

### Keyboard Shortcuts
- `1` - Select Option A
- `2` - Select Option B
- `0` - No Preference

---

## Rule Review Page (`/session/{id}/review`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `review-rules-input-newrule` | Input | Text input for adding stated preferences |
| `review-rules-button-addrule` | Button | Submit new stated preference |
| `review-rules-button-generate` | Button | Generate skill package from rules |
| `review-rules-section-{componentType}` | Div | Section containing rules for component type |

### Example Usage
```javascript
// Add a stated preference
await page.fill('[agent-handle="review-rules-input-newrule"]', 'never use gradients');
await page.click('[agent-handle="review-rules-button-addrule"]');

// Generate skill package
await page.click('[agent-handle="review-rules-button-generate"]');
```

### Supported Stated Preferences
Natural language inputs are parsed. Examples:
- "never use gradients"
- "prefer rounded corners"
- "always use shadows"
- "avoid uppercase text"
- "use pill buttons"

---

## Skill Download Page (`/session/{id}/download`)

| Handle | Element Type | Purpose |
|--------|--------------|---------|
| `skill-download-button-zip` | Button | Download generated skill package as ZIP |
| `skill-preview-content` | Div | Preview of package contents |

### Example Usage
```javascript
// Download the skill package
await page.click('[agent-handle="skill-download-button-zip"]');
```

---

## Complete User Flow Example

```javascript
// Full extraction flow using Puppeteer
const puppeteer = require('puppeteer');

async function completeExtractionFlow() {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  // 1. Navigate to app
  await page.goto('http://localhost:5173');

  // 2. Go to registration
  await page.click('[agent-handle="landing-hero-button-getstarted"]');
  await page.waitForSelector('[agent-handle="auth-register-input-email"]');

  // 3. Register
  await page.fill('[agent-handle="auth-register-input-firstname"]', 'Test');
  await page.fill('[agent-handle="auth-register-input-lastname"]', 'User');
  await page.fill('[agent-handle="auth-register-input-email"]', 'test@example.com');
  await page.fill('[agent-handle="auth-register-input-password"]', 'testpass123');
  await page.fill('[agent-handle="auth-register-input-confirmpassword"]', 'testpass123');
  await page.click('[agent-handle="auth-register-button-submit"]');

  // 4. Wait for dashboard
  await page.waitForSelector('[agent-handle="dashboard-sessions-button-create"]');

  // 5. Create session
  await page.click('[agent-handle="dashboard-sessions-button-create"]');
  // Fill session name in the form that appears
  await page.fill('input[placeholder*="Brand"]', 'My Style Profile');
  await page.click('button[type="submit"]');

  // 6. Complete comparisons (10+ for territory mapping)
  for (let i = 0; i < 12; i++) {
    await page.waitForSelector('[agent-handle="extraction-comparison-option-a"]');
    // Randomly choose A or B
    const choice = Math.random() > 0.5 ? 'a' : 'b';
    await page.click(`[agent-handle="extraction-comparison-option-${choice}"]`);
    await page.waitForTimeout(500); // Wait for next comparison
  }

  // 7. Navigate to review (may happen automatically after enough comparisons)
  // Or click skip button if available

  // 8. Add stated preference
  await page.waitForSelector('[agent-handle="review-rules-input-newrule"]');
  await page.fill('[agent-handle="review-rules-input-newrule"]', 'never use drop shadows');
  await page.click('[agent-handle="review-rules-button-addrule"]');

  // 9. Generate skill
  await page.click('[agent-handle="review-rules-button-generate"]');

  // 10. Download
  await page.waitForSelector('[agent-handle="skill-download-button-zip"]');
  await page.click('[agent-handle="skill-download-button-zip"]');

  console.log('Extraction flow completed!');
  await browser.close();
}

completeExtractionFlow();
```

---

## API Endpoint

This documentation is also available via API:

```
GET /agent-handles.md
```

Returns this markdown document for programmatic access.

---

## Notes for AI Agents

1. **Wait for elements**: Always wait for handles to be visible before interacting
2. **Dynamic handles**: Session IDs are dynamic - query the page to find current IDs
3. **Form validation**: Registration requires 8+ character passwords
4. **Phase transitions**: After ~15 comparisons, session moves to dimension isolation
5. **Keyboard shortcuts**: Can use keyboard instead of clicking in extraction flow

## Selector Pattern

All handles use the attribute selector pattern:
```css
[agent-handle="handle-name"]
```

This is more stable than class or ID selectors as handles are explicitly maintained for automation purposes.
