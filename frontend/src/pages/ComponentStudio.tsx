/**
 * Component Studio - Main orchestrator page.
 *
 * Walks users through each of the 12 component types systematically,
 * one dimension at a time, with live preview and checkpoint mockup reviews.
 */
import { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useSession } from '@/contexts/SessionContext';
import { api } from '@/services/api';
import { Button } from '@/components/ui/shadcn/Button';
import DimensionPicker from '@/components/studio/DimensionPicker';
import ComponentPreview from '@/components/studio/ComponentPreview';
import MockupCheckpoint from '@/components/studio/MockupCheckpoint';
import type {
  StudioProgress,
  ComponentDimensions,
  ComponentState,
  DimensionOption,
  CheckpointData,
} from '@/types';

const COMPONENT_LABELS: Record<string, string> = {
  button: 'Button', input: 'Input', card: 'Card', typography: 'Typography',
  navigation: 'Navigation', form: 'Form', modal: 'Modal', feedback: 'Feedback',
  table: 'Table', badge: 'Badge', tabs: 'Tabs', toggle: 'Toggle',
};

const ALL_COMPONENTS = [
  'button', 'input', 'card', 'typography',
  'navigation', 'form', 'modal', 'feedback',
  'table', 'badge', 'tabs', 'toggle',
];

// Checkpoint boundaries: after indices 3, 7, 11
const CHECKPOINT_AFTER = [3, 7, 11];

export default function ComponentStudio() {
  const navigate = useNavigate();
  const { sessionId } = useParams<{ sessionId: string }>();
  const { currentSession, selectSession } = useSession();
  const initialized = useRef(false);
  const [progress, setProgress] = useState<StudioProgress | null>(null);
  const [dimensions, setDimensions] = useState<ComponentDimensions | null>(null);
  const [componentState, setComponentState] = useState<ComponentState | null>(null);
  const [checkpointData, setCheckpointData] = useState<CheckpointData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const sid = sessionId || '';

  // Init session
  useEffect(() => {
    if (sessionId && !initialized.current) {
      initialized.current = true;
      selectSession(sid);
    }
  }, [sessionId]);

  // Load studio progress
  const loadProgress = useCallback(async () => {
    try {
      const p = await api.getStudioProgress(sid);
      setProgress(p);
      return p;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load progress');
      return null;
    }
  }, [sid]);

  // Load dimensions and state for a component
  const loadComponent = useCallback(async (componentType: string) => {
    setLoading(true);
    setError(null);
    try {
      const [dims, state] = await Promise.all([
        api.getComponentDimensions(sid, componentType),
        api.getComponentState(sid, componentType),
      ]);
      setDimensions(dims);
      setComponentState(state);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load component');
    } finally {
      setLoading(false);
    }
  }, [sid]);

  // Initial load
  useEffect(() => {
    if (!sid) return;
    (async () => {
      setLoading(true);
      const p = await loadProgress();
      if (p?.pending_checkpoint) {
        // Load checkpoint data
        try {
          const data = await api.getCheckpointData(sid, p.pending_checkpoint);
          setCheckpointData(data);
        } catch {}
        setLoading(false);
      } else if (p?.current_component) {
        await loadComponent(p.current_component);
      } else if (p?.is_complete) {
        navigate(`/session/${sessionId}/review`);
      } else {
        setLoading(false);
      }
    })();
  }, [sid]);

  // Handle dimension selection
  const handleDimensionSelect = useCallback(async (option: DimensionOption, fineTunedValue?: string) => {
    if (!progress?.current_component || !dimensions) return;

    const currentDimIdx = progress.current_dimension_index;
    const dim = dimensions.dimensions[currentDimIdx];
    if (!dim) return;

    try {
      await api.submitDimensionChoice(sid, progress.current_component, {
        dimension: dim.key,
        selected_option_id: option.id,
        selected_value: option.value,
        css_property: dim.css_property,
        fine_tuned_value: fineTunedValue,
      });

      // Update local state
      setComponentState(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          choices: {
            ...prev.choices,
            [dim.key]: {
              option_id: option.id,
              value: fineTunedValue || option.value,
              original_value: option.value,
              fine_tuned_value: fineTunedValue || null,
              css_property: dim.css_property,
            },
          },
        };
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save choice');
    }
  }, [sid, progress, dimensions]);

  // Next dimension or lock component
  const handleNext = useCallback(async () => {
    if (!progress?.current_component || !dimensions) return;

    const nextIdx = progress.current_dimension_index + 1;

    if (nextIdx < dimensions.dimensions.length) {
      // Move to next dimension
      setProgress(prev => prev ? { ...prev, current_dimension_index: nextIdx } : prev);
    } else {
      // All dimensions done - lock component
      setLoading(true);
      try {
        const result = await api.lockComponent(sid);

        if (result.trigger_checkpoint) {
          // Show checkpoint mockup
          const data = await api.getCheckpointData(sid, result.trigger_checkpoint);
          setCheckpointData(data);
          const p = await loadProgress();
          setProgress(p);
          setLoading(false);
        } else if (result.is_studio_complete) {
          navigate(`/session/${sessionId}/review`);
        } else if (result.next_component) {
          const p = await loadProgress();
          setProgress(p);
          await loadComponent(result.next_component);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to advance');
        setLoading(false);
      }
    }
  }, [sid, progress, dimensions, sessionId, navigate, loadProgress, loadComponent]);

  // Go back one dimension
  const handleBack = useCallback(() => {
    if (!progress) return;
    if (progress.current_dimension_index > 0) {
      setProgress(prev => prev ? { ...prev, current_dimension_index: prev.current_dimension_index - 1 } : prev);
    }
  }, [progress]);

  // Navigate to a different component
  const handleComponentNav = useCallback(async (componentType: string) => {
    if (!progress) return;
    // Only allow navigating to completed components
    if (!progress.completed_components.includes(componentType) && componentType !== progress.current_component) return;

    setLoading(true);
    try {
      await api.goBackToComponent(sid, componentType);
      const p = await loadProgress();
      setProgress(p);
      await loadComponent(componentType);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to navigate');
      setLoading(false);
    }
  }, [sid, progress, loadProgress, loadComponent]);

  // Approve checkpoint
  const handleCheckpointApprove = useCallback(async () => {
    if (!checkpointData) return;
    setLoading(true);
    try {
      const result = await api.approveCheckpoint(sid, checkpointData.checkpoint_id);
      setCheckpointData(null);

      if (result.is_studio_complete) {
        navigate(`/session/${sessionId}/review`);
      } else if (result.next_component) {
        const p = await loadProgress();
        setProgress(p);
        await loadComponent(result.next_component);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve checkpoint');
      setLoading(false);
    }
  }, [sid, checkpointData, sessionId, navigate, loadProgress, loadComponent]);

  // Go back from checkpoint to edit a component
  const handleCheckpointGoBack = useCallback(async (componentType: string) => {
    setCheckpointData(null);
    setLoading(true);
    try {
      await api.goBackToComponent(sid, componentType);
      const p = await loadProgress();
      setProgress(p);
      await loadComponent(componentType);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to go back');
      setLoading(false);
    }
  }, [sid, loadProgress, loadComponent]);

  // Compute hasSelection early so it's available for the Enter key effect
  const _currentDim = dimensions?.dimensions[progress?.current_dimension_index ?? 0];
  const hasSelectionEarly = !!(_currentDim && componentState?.choices[_currentDim.key]);

  // Enter key to advance
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && hasSelectionEarly && !loading) {
        e.preventDefault();
        handleNext();
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [handleNext, hasSelectionEarly, loading]);

  // ============================================================================
  // Render
  // ============================================================================

  if (!currentSession) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading session...</p>
      </div>
    );
  }

  // Checkpoint view
  if (checkpointData) {
    return (
      <MockupCheckpoint
        data={checkpointData}
        sessionName={currentSession.name}
        onApprove={handleCheckpointApprove}
        onGoBack={handleCheckpointGoBack}
        loading={loading}
      />
    );
  }

  const currentComponent = progress?.current_component;
  const currentDimIdx = progress?.current_dimension_index ?? 0;
  const currentDim = dimensions?.dimensions[currentDimIdx];
  const totalDims = dimensions?.dimensions.length ?? 0;
  const isLastDimension = currentDimIdx >= totalDims - 1;
  const hasSelection = currentDim && componentState?.choices[currentDim.key];

  // Build accumulated styles for the live preview
  const previewStyles: Record<string, string> = {};
  if (componentState) {
    for (const [, choice] of Object.entries(componentState.choices)) {
      previewStyles[choice.css_property] = choice.value;
    }
  }

  // Parse colors and typography from session
  const sessionColors = currentSession.chosen_colors as Record<string, string> | null;
  const sessionTypography = currentSession.chosen_typography as Record<string, string> | null;

  // Build allChoices map for DimensionPicker
  const allChoices: Record<string, { value: string; css_property: string }> = {};
  if (componentState) {
    for (const [key, choice] of Object.entries(componentState.choices)) {
      allChoices[key] = { value: choice.value, css_property: choice.css_property };
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b py-3 px-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="font-semibold">{currentSession.name}</h1>
            <p className="text-sm text-gray-500">Component Studio</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" onClick={() => navigate(`/session/${sessionId}/review`)}>
              Skip to Review
            </Button>
            <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')}>
              Exit
            </Button>
          </div>
        </div>
      </header>

      {/* Component Navigation Bar */}
      <div className="bg-white border-b py-2 px-4 overflow-x-auto">
        <div className="max-w-7xl mx-auto flex items-center gap-1">
          {ALL_COMPONENTS.map((comp, idx) => {
            const isCompleted = progress?.completed_components.includes(comp);
            const isCurrent = comp === currentComponent;
            const isClickable = isCompleted || isCurrent;

            return (
              <div key={comp} className="flex items-center">
                <button
                  onClick={() => isClickable && handleComponentNav(comp)}
                  disabled={!isClickable}
                  className={`
                    px-3 py-1.5 rounded-md text-xs font-medium transition-all whitespace-nowrap
                    ${isCurrent ? 'bg-blue-100 text-blue-700 ring-1 ring-blue-300' : ''}
                    ${isCompleted && !isCurrent ? 'bg-green-50 text-green-700 hover:bg-green-100 cursor-pointer' : ''}
                    ${!isCompleted && !isCurrent ? 'text-gray-400 cursor-default' : ''}
                  `}
                >
                  {isCompleted && !isCurrent && <span className="mr-1">&#10003;</span>}
                  {isCurrent && <span className="mr-1">&#8594;</span>}
                  {COMPONENT_LABELS[comp] || comp}
                </button>
                {CHECKPOINT_AFTER.includes(idx) && idx < ALL_COMPONENTS.length - 1 && (
                  <div className="w-px h-6 bg-gray-300 mx-1" />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-3 text-red-600 bg-red-50 text-center text-sm">
          {error}
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-4">
        {loading && !currentDim ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4" />
              <p className="text-gray-500">Loading component...</p>
            </div>
          </div>
        ) : currentComponent && currentDim ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Dimension Picker */}
            <div className="space-y-6">
              {/* Component title */}
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  {COMPONENT_LABELS[currentComponent] || currentComponent}
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  Customize each dimension to match your taste
                </p>
              </div>

              {/* Dimension Picker */}
              <DimensionPicker
                dimension={currentDim}
                componentType={currentComponent}
                selectedOptionId={componentState?.choices[currentDim.key]?.option_id || null}
                fineTunedValue={componentState?.choices[currentDim.key]?.fine_tuned_value || null}
                allChoices={allChoices}
                colors={sessionColors}
                typography={sessionTypography}
                onSelect={handleDimensionSelect}
              />

              {/* Dimension Progress Dots */}
              <div className="flex items-center gap-2">
                {dimensions?.dimensions.map((d, i) => (
                  <div
                    key={d.key}
                    className={`
                      w-2.5 h-2.5 rounded-full transition-all
                      ${i < currentDimIdx ? 'bg-green-400' : ''}
                      ${i === currentDimIdx ? 'bg-blue-500 ring-2 ring-blue-200 scale-125' : ''}
                      ${i > currentDimIdx ? 'bg-gray-300' : ''}
                    `}
                  />
                ))}
                <span className="text-xs text-gray-400 ml-2">
                  Dimension {currentDimIdx + 1} of {totalDims}
                </span>
              </div>
            </div>

            {/* Right: Live Preview */}
            <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
              <div className="px-4 py-3 border-b bg-gray-50">
                <h3 className="text-sm font-medium text-gray-600">Live Preview</h3>
              </div>
              <div className="p-6">
                <ComponentPreview
                  componentType={currentComponent}
                  styles={previewStyles}
                  colors={sessionColors}
                  typography={sessionTypography}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center py-20">
            <p className="text-gray-500">No component selected</p>
          </div>
        )}
      </main>

      {/* Footer Navigation */}
      <footer className="bg-white border-t py-4 px-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Button
            variant="outline"
            size="sm"
            onClick={handleBack}
            disabled={!progress || progress.current_dimension_index === 0}
          >
            &larr; Back
          </Button>

          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              {currentComponent && (
                <>
                  {progress?.completed_components.length || 0} of {ALL_COMPONENTS.length} components
                </>
              )}
            </span>

            <Button
              onClick={handleNext}
              disabled={!hasSelection || loading}
              className="px-8 py-2.5 text-base font-semibold"
            >
              {isLastDimension ? 'Lock & Continue \u2192' : 'Next \u2192'}
              {hasSelection && (
                <span className="ml-2 text-xs opacity-70 font-normal">Enter &#x23CE;</span>
              )}
            </Button>
          </div>
        </div>
      </footer>
    </div>
  );
}
