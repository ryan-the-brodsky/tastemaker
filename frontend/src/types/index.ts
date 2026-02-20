export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  subscription_tier: string;
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

// Color palette from color_exploration phase
export interface ColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  accentSoft: string;
  background: string;
  category?: string;
}

// Font pairing from typography_exploration phase
export interface FontPairing {
  heading: string;
  body: string;
  style: string;
  category?: string;
  description?: string;
}

export interface Session {
  id: string;
  name: string;
  phase: string;
  brand_colors: string | null;
  project_description: string | null;  // User's project context for AI generation
  comparison_count: number;
  confidence_score: number;
  // Progressive incorporation: established preferences as key-value pairs
  established_preferences: Record<string, string> | null;
  // Chosen color palette from color_exploration phase
  chosen_colors: ColorPalette | null;
  // Chosen typography from typography_exploration phase
  chosen_typography: FontPairing | null;
  created_at: string;
  updated_at: string | null;
  completed_at: string | null;
}

// Lock-in request for "That's it!" button
export interface LockInRequest {
  chosen_option_id: string;
  chosen_styles: Record<string, unknown>;
}

// Lock-in response
export interface LockInResponse {
  success: boolean;
  new_phase: string;
  message: string;
}

export interface ComparisonOption {
  id: string;
  styles: Record<string, unknown>;
}

// Multi-question support
export interface ComparisonQuestion {
  category: string;  // "typography", "color", "shape", "spacing"
  property: string;  // "backgroundColor", "fontWeight", etc.
  question_text: string;
  option_a_value: string;
  option_b_value: string;
}

export interface QuestionAnswer {
  category: string;
  property: string;
  choice: 'a' | 'b' | 'none';
}

export interface Comparison {
  comparison_id: number;
  component_type: string;
  phase: string;
  option_a: ComparisonOption;
  option_b: ComparisonOption;
  context: string;
  // Multi-question support
  questions?: ComparisonQuestion[];
  generation_method?: string;  // "claude_api" or "deterministic"
}

export interface SessionProgress {
  comparison_count: number;
  phase: string;
  confidence_score: number;
  next_phase: string | null;
  // Established preferences for progressive display
  established_preferences: Record<string, string> | null;
}

export interface StyleRule {
  id: string;
  rule_id: string;
  component_type: string | null;
  property: string;
  operator: string;
  value: string;
  severity: string;
  confidence: number | null;
  source: string;
  message: string | null;
  is_modified: boolean;
  created_at: string;
}

export interface SkillPreview {
  total_rules: number;
  extracted_rules: number;
  stated_rules: number;
  baseline_rules: number;
  components_covered: string[];
  files_included: string[];
}

export interface SkillGenerateResponse {
  skill_id: string;
  download_url: string;
  preview: SkillPreview;
}

// Component Studio types
export interface DimensionOption {
  id: string;
  label: string;
  value: string;
}

export interface FineTuneConfig {
  min: number;
  max: number;
  step: number;
  unit: string;
}

export interface DimensionDefinition {
  key: string;
  label: string;
  css_property: string;
  options: DimensionOption[];
  fine_tune: FineTuneConfig | null;
  order: number;
}

export interface ComponentDimensions {
  component_type: string;
  component_label: string;
  dimensions: DimensionDefinition[];
}

export interface DimensionChoiceSubmit {
  dimension: string;
  selected_option_id: string;
  selected_value: string;
  css_property: string;
  fine_tuned_value?: string;
}

export interface ComponentState {
  component_type: string;
  choices: Record<string, {
    option_id: string;
    value: string;
    original_value: string;
    fine_tuned_value: string | null;
    css_property: string;
  }>;
}

export interface StudioProgress {
  current_component: string | null;
  current_dimension_index: number;
  completed_components: string[];
  total_components: number;
  checkpoint_approvals: string[];
  pending_checkpoint: string | null;
  is_complete: boolean;
}

export interface CheckpointData {
  checkpoint_id: string;
  label: string;
  description: string;
  mockup_type: string;
  components: string[];
  component_styles: Record<string, Record<string, string>>;
  colors: Record<string, string> | null;
  typography: Record<string, string> | null;
}

export interface LockComponentResponse {
  success: boolean;
  next_component: string | null;
  trigger_checkpoint: string | null;
  is_studio_complete: boolean;
}

export type ComponentStyles = Record<string, Record<string, string>>;
