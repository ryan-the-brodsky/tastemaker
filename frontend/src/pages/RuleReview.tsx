import { useEffect, useState, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useSession } from '@/contexts/SessionContext';
import { Button } from '@/components/ui/shadcn/Button';
import { Input } from '@/components/ui/shadcn/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/shadcn/Card';
import type { StyleRule } from '@/types';

export default function RuleReview() {
  const navigate = useNavigate();
  const { sessionId } = useParams<{ sessionId: string }>();
  const {
    currentSession,
    rules,
    selectSession,
    loadRules,
    addRule,
    deleteRule,
    generateSkill,
    loading,
    error,
  } = useSession();
  const [newRuleText, setNewRuleText] = useState('');
  const [addingRule, setAddingRule] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState<string>('all');
  const [ruleBuilderMode, setRuleBuilderMode] = useState<'simple' | 'advanced'>('simple');
  const [advancedRule, setAdvancedRule] = useState({
    component_type: '',
    property: '',
    operator: '=',
    value: '',
    severity: 'warning',
    message: '',
  });
  const initialized = useRef(false);

  const COMPONENT_TYPES = ['button', 'input', 'card', 'modal', 'navigation', 'form', 'feedback', ''];
  const OPERATORS = ['=', '>=', '<=', '>', '<', 'contains', 'one_of'];
  const SEVERITIES = ['error', 'warning', 'info'];

  useEffect(() => {
    if (sessionId && !initialized.current) {
      initialized.current = true;
      selectSession(parseInt(sessionId)).then(() => {
        loadRules();
      });
    }
  }, [sessionId]);

  // Redirect if session is complete
  useEffect(() => {
    if (currentSession?.phase === 'complete') {
      navigate(`/session/${sessionId}/download`);
    }
  }, [currentSession?.phase, sessionId, navigate]);

  const handleAddRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRuleText.trim()) return;

    setAddingRule(true);
    try {
      await addRule(newRuleText.trim());
      setNewRuleText('');
    } catch {
      // Error handled by context
    } finally {
      setAddingRule(false);
    }
  };

  const handleAddAdvancedRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!advancedRule.property || !advancedRule.value) return;

    setAddingRule(true);
    try {
      // Format as a structured rule string that the backend can parse
      const ruleText = advancedRule.message ||
        `${advancedRule.property} ${advancedRule.operator} ${advancedRule.value}`;
      await addRule(ruleText);
      // Reset form
      setAdvancedRule({
        component_type: '',
        property: '',
        operator: '=',
        value: '',
        severity: 'warning',
        message: '',
      });
    } catch {
      // Error handled by context
    } finally {
      setAddingRule(false);
    }
  };

  const getAdvancedRulePreview = () => {
    return {
      rule_id: `custom-${Date.now()}`,
      component_type: advancedRule.component_type || null,
      property: advancedRule.property,
      operator: advancedRule.operator,
      value: advancedRule.value,
      severity: advancedRule.severity,
      message: advancedRule.message || `${advancedRule.property} must be ${advancedRule.operator} ${advancedRule.value}`,
      source: 'stated',
    };
  };

  const handleDeleteRule = async (ruleId: string) => {
    if (!confirm('Are you sure you want to delete this rule?')) return;
    await deleteRule(ruleId);
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const result = await generateSkill();
      navigate(`/session/${sessionId}/download`, { state: { skill: result } });
    } catch {
      // Error handled by context
    } finally {
      setGenerating(false);
    }
  };

  // Group rules by component type
  const groupedRules = rules.reduce((acc, rule) => {
    const key = rule.component_type || 'global';
    if (!acc[key]) acc[key] = [];
    acc[key].push(rule);
    return acc;
  }, {} as Record<string, StyleRule[]>);

  const componentTypes = ['all', ...Object.keys(groupedRules).filter(k => k !== 'global'), 'global'];
  const filteredRules = activeTab === 'all' ? rules : groupedRules[activeTab] || [];

  const getSourceBadge = (source: string) => {
    const colors: Record<string, string> = {
      extracted: 'bg-blue-100 text-blue-800',
      stated: 'bg-purple-100 text-purple-800',
      baseline: 'bg-gray-100 text-gray-800',
    };
    return colors[source] || 'bg-gray-100 text-gray-800';
  };

  const getSeverityBadge = (severity: string) => {
    const colors: Record<string, string> = {
      error: 'bg-red-100 text-red-800',
      warning: 'bg-yellow-100 text-yellow-800',
      info: 'bg-blue-100 text-blue-800',
    };
    return colors[severity] || 'bg-gray-100 text-gray-800';
  };

  if (!currentSession) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading session...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="font-semibold">{currentSession.name}</h1>
            <p className="text-sm text-gray-500">
              Review and refine your extracted rules
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => navigate(`/session/${sessionId}`)}
            >
              Back to Comparisons
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate(`/session/${sessionId}/mockups`)}
              agent-handle="review-rules-button-mockups"
            >
              Preview Mockups
            </Button>
            <Button
              onClick={handleGenerate}
              disabled={generating || rules.length === 0}
              agent-handle="review-rules-button-generate"
            >
              {generating ? 'Generating...' : 'Generate Skill Package'}
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Error Display */}
        {error && (
          <div className="p-4 mb-6 text-red-500 bg-red-50 rounded-md">
            {error}
          </div>
        )}

        {/* Add Rule Section */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Add Style Rule</CardTitle>
              <div className="flex gap-2">
                <button
                  className={`px-3 py-1 text-sm rounded-md ${
                    ruleBuilderMode === 'simple'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                  onClick={() => setRuleBuilderMode('simple')}
                >
                  Simple
                </button>
                <button
                  className={`px-3 py-1 text-sm rounded-md ${
                    ruleBuilderMode === 'advanced'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                  onClick={() => setRuleBuilderMode('advanced')}
                  agent-handle="rule-builder-advanced-toggle"
                >
                  Rule Builder
                </button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {ruleBuilderMode === 'simple' ? (
              <form onSubmit={handleAddRule} className="flex gap-2">
                <Input
                  placeholder='e.g., "never use gradients" or "prefer rounded corners"'
                  value={newRuleText}
                  onChange={(e) => setNewRuleText(e.target.value)}
                  className="flex-1"
                  agent-handle="review-rules-input-newrule"
                />
                <Button
                  type="submit"
                  disabled={addingRule || !newRuleText.trim()}
                  agent-handle="review-rules-button-addrule"
                >
                  {addingRule ? 'Adding...' : 'Add Rule'}
                </Button>
              </form>
            ) : (
              <form onSubmit={handleAddAdvancedRule} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Component Type</label>
                    <select
                      className="w-full px-3 py-2 border rounded-md"
                      value={advancedRule.component_type}
                      onChange={(e) => setAdvancedRule({ ...advancedRule, component_type: e.target.value })}
                      agent-handle="rule-builder-component-type"
                    >
                      <option value="">Global (all components)</option>
                      {COMPONENT_TYPES.filter(t => t).map((type) => (
                        <option key={type} value={type}>
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Property *</label>
                    <Input
                      placeholder="e.g., border-radius, font-size"
                      value={advancedRule.property}
                      onChange={(e) => setAdvancedRule({ ...advancedRule, property: e.target.value })}
                      required
                      agent-handle="rule-builder-property"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Operator</label>
                    <select
                      className="w-full px-3 py-2 border rounded-md"
                      value={advancedRule.operator}
                      onChange={(e) => setAdvancedRule({ ...advancedRule, operator: e.target.value })}
                      agent-handle="rule-builder-operator"
                    >
                      {OPERATORS.map((op) => (
                        <option key={op} value={op}>{op}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Value *</label>
                    <Input
                      placeholder="e.g., 8px, #1a365d"
                      value={advancedRule.value}
                      onChange={(e) => setAdvancedRule({ ...advancedRule, value: e.target.value })}
                      required
                      agent-handle="rule-builder-value"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Severity</label>
                    <select
                      className="w-full px-3 py-2 border rounded-md"
                      value={advancedRule.severity}
                      onChange={(e) => setAdvancedRule({ ...advancedRule, severity: e.target.value })}
                      agent-handle="rule-builder-severity"
                    >
                      {SEVERITIES.map((sev) => (
                        <option key={sev} value={sev}>
                          {sev.charAt(0).toUpperCase() + sev.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Message (optional)</label>
                    <Input
                      placeholder="Custom error message"
                      value={advancedRule.message}
                      onChange={(e) => setAdvancedRule({ ...advancedRule, message: e.target.value })}
                      agent-handle="rule-builder-message"
                    />
                  </div>
                </div>

                {/* JSON Preview */}
                {(advancedRule.property && advancedRule.value) && (
                  <div className="p-3 bg-gray-50 rounded-md">
                    <label className="block text-xs font-medium text-gray-500 mb-2">Rule Preview (JSON)</label>
                    <pre className="text-xs overflow-x-auto" agent-handle="rule-builder-preview">
                      {JSON.stringify(getAdvancedRulePreview(), null, 2)}
                    </pre>
                  </div>
                )}

                <Button
                  type="submit"
                  disabled={addingRule || !advancedRule.property || !advancedRule.value}
                  agent-handle="rule-builder-submit"
                >
                  {addingRule ? 'Adding...' : 'Add Rule'}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>

        {/* Tabs */}
        <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
          {componentTypes.map((type) => (
            <button
              key={type}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === type
                  ? 'bg-primary text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
              onClick={() => setActiveTab(type)}
            >
              {type === 'all' ? 'All Rules' : type.charAt(0).toUpperCase() + type.slice(1)}
              {type !== 'all' && groupedRules[type] && (
                <span className="ml-1 text-xs opacity-70">
                  ({groupedRules[type].length})
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Rules List */}
        {loading && rules.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            Loading rules...
          </div>
        ) : filteredRules.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <p className="text-gray-500">
                {activeTab === 'all'
                  ? 'No rules extracted yet. Complete more comparisons or add stated preferences.'
                  : `No rules for ${activeTab} components.`}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3" agent-handle={`review-rules-section-${activeTab}`}>
            {filteredRules.map((rule) => (
              <Card key={rule.id} className="hover:shadow-sm transition-shadow">
                <CardContent className="py-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${getSourceBadge(
                            rule.source
                          )}`}
                        >
                          {rule.source}
                        </span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${getSeverityBadge(
                            rule.severity
                          )}`}
                        >
                          {rule.severity}
                        </span>
                        {rule.component_type && (
                          <span className="text-xs text-gray-500">
                            {rule.component_type}
                          </span>
                        )}
                        {rule.confidence && (
                          <span className="text-xs text-gray-400">
                            {(rule.confidence * 100).toFixed(0)}% confidence
                          </span>
                        )}
                      </div>
                      <p className="font-medium text-gray-900">
                        {rule.message || `${rule.property} ${rule.operator} ${rule.value}`}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        {rule.property} {rule.operator} {rule.value}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      onClick={() => handleDeleteRule(rule.rule_id)}
                    >
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Summary */}
        {rules.length > 0 && (
          <Card className="mt-6">
            <CardContent className="py-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium">
                    {rules.length} rules ready
                  </p>
                  <p className="text-sm text-gray-500">
                    {rules.filter(r => r.source === 'extracted').length} extracted,{' '}
                    {rules.filter(r => r.source === 'stated').length} stated
                  </p>
                </div>
                <Button
                  onClick={handleGenerate}
                  disabled={generating}
                  agent-handle="review-rules-button-generate-bottom"
                >
                  {generating ? 'Generating...' : 'Generate Skill Package'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
