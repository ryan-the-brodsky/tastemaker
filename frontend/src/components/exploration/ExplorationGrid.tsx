import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/shadcn/Button';
import PaletteCard, { type ColorKey } from './PaletteCard';
import TypographyCard from './TypographyCard';
import ColorEditor, { type DerivedColors } from './ColorEditor';
import { api } from '@/services/api';
import type { ExplorationOption, ExplorationResponse } from '@/services/api';

// Type for tracking which option each color was selected from
type SelectedColors = Partial<Record<ColorKey, { option: ExplorationOption; color: string }>>;

interface ColorPalette {
  id: string;
  name: string;
  category: string;
  primary: string;
  secondary: string;
  accent: string;
  accentSoft: string;
  background: string;
  description?: string;
}

interface ExplorationGridProps {
  sessionId: string;
  explorationType: 'palette' | 'typography';
  onPhaseComplete: (newPhase: string) => void;
}

export default function ExplorationGrid({
  sessionId,
  explorationType,
  onPhaseComplete,
}: ExplorationGridProps) {
  const [options, setOptions] = useState<ExplorationOption[]>([]);
  const [selectedOption, setSelectedOption] = useState<ExplorationOption | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [explorationDepth, setExplorationDepth] = useState(0);
  const [context, setContext] = useState<string | undefined>();
  // Color editor state - only for palette exploration
  const [showColorEditor, setShowColorEditor] = useState(false);
  const [paletteForEditing, setPaletteForEditing] = useState<ColorPalette | null>(null);
  // Mix & match state (shared toggle, separate selections)
  const [mixMatchMode, setMixMatchMode] = useState(false);
  // Typography mix & match
  const [selectedHeadingOption, setSelectedHeadingOption] = useState<ExplorationOption | null>(null);
  const [selectedBodyOption, setSelectedBodyOption] = useState<ExplorationOption | null>(null);
  // Palette mix & match
  const [selectedColors, setSelectedColors] = useState<SelectedColors>({});

  // Load initial options with AbortController to handle React StrictMode double-mount
  useEffect(() => {
    const abortController = new AbortController();
    loadOptions(abortController.signal);
    return () => abortController.abort();
  }, [sessionId, explorationType]);

  const loadOptions = async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    setSelectedOption(null);

    try {
      let response: ExplorationResponse;
      if (explorationType === 'palette') {
        response = await api.getPaletteOptions(sessionId, signal);
      } else {
        response = await api.getTypographyOptions(sessionId, signal);
      }

      // Don't update state if request was aborted
      if (signal?.aborted) return;

      setOptions(response.options);
      setExplorationDepth(response.exploration_depth);
      setContext(response.context);
    } catch (err) {
      // Ignore abort errors
      if (err instanceof Error && err.name === 'AbortError') return;
      console.error('Failed to load exploration options:', err);
      setError('Failed to load options. Please try again.');
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  };

  const handleSelect = (option: ExplorationOption) => {
    setSelectedOption(option);
  };

  // Handle selecting a specific color from a palette in mix-match mode
  const handleColorSelect = (option: ExplorationOption, colorKey: ColorKey) => {
    const colorValue = option[colorKey] as string;
    setSelectedColors(prev => ({
      ...prev,
      [colorKey]: { option, color: colorValue },
    }));
  };

  // Check if all required colors are selected for palette mix-match
  const allPaletteColorsSelected =
    selectedColors.primary &&
    selectedColors.secondary &&
    selectedColors.accent &&
    selectedColors.background &&
    selectedColors.accentSoft;

  const handleRefine = async () => {
    if (!selectedOption) return;

    setSubmitting(true);
    setError(null);

    try {
      let response;
      if (explorationType === 'palette') {
        response = await api.selectPalette(
          sessionId,
          selectedOption.id,
          selectedOption as unknown as Record<string, unknown>,
          true // wants refinement
        );
      } else {
        response = await api.selectTypography(
          sessionId,
          selectedOption.id,
          selectedOption as unknown as Record<string, unknown>,
          true // wants refinement
        );
      }

      if (response.locked_in) {
        // Phase completed
        onPhaseComplete(response.new_phase || '');
      } else if (response.next_options && response.next_options.length > 0) {
        // Got refined options
        setOptions(response.next_options);
        setExplorationDepth(response.exploration_depth);
        setSelectedOption(null);
      } else {
        // No more refinements, reload from server
        await loadOptions();
      }
    } catch (err) {
      console.error('Failed to refine selection:', err);
      setError('Failed to submit selection. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLockIn = async () => {
    // For palette exploration, show the color editor first
    if (explorationType === 'palette') {
      let palette: ColorPalette;

      if (mixMatchMode && allPaletteColorsSelected) {
        // Create a mixed palette from selected colors
        palette = {
          id: `mixed-palette-${Date.now()}`,
          name: 'Custom Mixed Palette',
          category: 'mixed',
          primary: selectedColors.primary!.color,
          secondary: selectedColors.secondary!.color,
          accent: selectedColors.accent!.color,
          accentSoft: selectedColors.accentSoft!.color,
          background: selectedColors.background!.color,
          description: 'Custom palette created by mixing colors from different palettes',
        };
      } else if (selectedOption) {
        palette = {
          id: selectedOption.id,
          name: selectedOption.name,
          category: selectedOption.category,
          primary: selectedOption.primary || '#1e3a8a',
          secondary: selectedOption.secondary || '#0891b2',
          accent: selectedOption.accent || '#f59e0b',
          accentSoft: selectedOption.accentSoft || '#fbbf24',
          background: selectedOption.background || '#f8fafc',
          description: selectedOption.description,
        };
      } else {
        return;
      }

      setPaletteForEditing(palette);
      setShowColorEditor(true);
      return;
    }

    // For typography in mix-match mode, create a combined option
    if (mixMatchMode && selectedHeadingOption && selectedBodyOption) {
      const mixedOption: ExplorationOption = {
        id: `mixed-${selectedHeadingOption.id}-${selectedBodyOption.id}`,
        name: `${selectedHeadingOption.heading} + ${selectedBodyOption.body}`,
        category: 'mixed',
        heading: selectedHeadingOption.heading,
        headingCategory: selectedHeadingOption.headingCategory,
        body: selectedBodyOption.body,
        bodyCategory: selectedBodyOption.bodyCategory,
        description: `Mixed: ${selectedHeadingOption.heading} headings with ${selectedBodyOption.body} body text`,
      };
      await submitLockIn(mixedOption);
      return;
    }

    // For typography without mix-match, proceed with lock-in immediately
    if (!selectedOption) return;
    await submitLockIn(selectedOption);
  };

  // Check if we can lock in (either has selection or has mix-match selections)
  const canLockIn = mixMatchMode
    ? (explorationType === 'typography'
        ? (selectedHeadingOption && selectedBodyOption)
        : allPaletteColorsSelected)
    : !!selectedOption;

  const submitLockIn = async (option: ExplorationOption | ColorPalette) => {
    setSubmitting(true);
    setError(null);

    try {
      let response;
      if (explorationType === 'palette') {
        response = await api.selectPalette(
          sessionId,
          option.id,
          option as unknown as Record<string, unknown>,
          false // don't want more refinement
        );
      } else {
        response = await api.selectTypography(
          sessionId,
          option.id,
          option as unknown as Record<string, unknown>,
          false // don't want more refinement
        );
      }

      // Phase should be complete
      onPhaseComplete(response.new_phase || '');
    } catch (err) {
      console.error('Failed to lock in selection:', err);
      setError('Failed to lock in selection. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleColorEditorSave = useCallback(async (palette: ColorPalette, derived: DerivedColors) => {
    // Add derived colors to the palette object for storage
    const enrichedPalette = {
      ...palette,
      derived,
    };
    await submitLockIn(enrichedPalette as unknown as ExplorationOption);
  }, []);

  const handleColorEditorCancel = useCallback(() => {
    setShowColorEditor(false);
    setPaletteForEditing(null);
  }, []);

  // Show color editor if user is fine-tuning a palette
  if (showColorEditor && paletteForEditing) {
    return (
      <ColorEditor
        initialPalette={paletteForEditing}
        onSave={handleColorEditorSave}
        onCancel={handleColorEditorCancel}
      />
    );
  }

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-500">
            {explorationType === 'palette' ? 'Generating color palettes...' : 'Generating typography options...'}
          </p>
        </div>
      </div>
    );
  }

  const maxDepth = 3;

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      {/* Context/Instructions */}
      <div className="p-4 bg-white border-b">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-lg font-semibold text-gray-800">
            {explorationType === 'palette' ? 'Choose Your Color Palette' : 'Choose Your Typography Style'}
          </h2>
          {context && (
            <p className="text-sm text-gray-500 mt-1">{context}</p>
          )}
          <div className="flex items-center justify-center gap-2 mt-2">
            <span className="text-xs text-gray-400">Refinement depth:</span>
            <div className="flex gap-1">
              {[...Array(maxDepth)].map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full ${
                    i < explorationDepth ? 'bg-primary' : 'bg-gray-200'
                  }`}
                />
              ))}
            </div>
          </div>
          {/* Mix & Match Toggle */}
          <div className="mt-3">
            <button
              onClick={() => {
                setMixMatchMode(!mixMatchMode);
                if (!mixMatchMode) {
                  // Entering mix-match mode - clear single selection
                  setSelectedOption(null);
                } else {
                  // Exiting mix-match mode - clear mix selections
                  setSelectedHeadingOption(null);
                  setSelectedBodyOption(null);
                  setSelectedColors({});
                }
              }}
              className={`
                px-4 py-2 text-sm font-medium rounded-full transition-all
                ${mixMatchMode
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }
              `}
            >
              {mixMatchMode
                ? 'Mix & Match: ON'
                : explorationType === 'typography'
                  ? 'Mix & Match Fonts'
                  : 'Mix & Match Colors'}
            </button>
            {mixMatchMode && (
              <p className="text-xs text-purple-600 mt-2">
                {explorationType === 'typography'
                  ? 'Click on heading or body text to select them separately'
                  : 'Click on individual color swatches to mix colors from different palettes'}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="p-4 bg-red-50 text-red-600 text-center">
          {error}
        </div>
      )}

      {/* Mix & Match Preview (Palette) */}
      {explorationType === 'palette' && mixMatchMode && Object.keys(selectedColors).length > 0 && (
        <div className="px-6 pt-4">
          <div className="max-w-5xl mx-auto">
            <div className="bg-white rounded-xl border-2 border-purple-200 p-4 shadow-sm">
              <span className="text-xs font-medium text-purple-600 uppercase tracking-wide">Live Preview</span>
              <div className="mt-3 flex gap-1 rounded-lg overflow-hidden">
                {/* Main colors */}
                <div
                  className={`h-16 flex-1 flex items-center justify-center text-xs font-medium ${selectedColors.primary ? 'text-white' : 'text-gray-400 bg-gray-100'}`}
                  style={selectedColors.primary ? { backgroundColor: selectedColors.primary.color } : undefined}
                >
                  {selectedColors.primary ? 'Primary' : 'Select Primary'}
                </div>
                <div
                  className={`h-16 flex-1 flex items-center justify-center text-xs font-medium ${selectedColors.secondary ? 'text-white' : 'text-gray-400 bg-gray-100'}`}
                  style={selectedColors.secondary ? { backgroundColor: selectedColors.secondary.color } : undefined}
                >
                  {selectedColors.secondary ? 'Secondary' : 'Select Secondary'}
                </div>
                <div
                  className={`h-16 flex-1 flex items-center justify-center text-xs font-medium ${selectedColors.accent ? 'text-white' : 'text-gray-400 bg-gray-100'}`}
                  style={selectedColors.accent ? { backgroundColor: selectedColors.accent.color } : undefined}
                >
                  {selectedColors.accent ? 'Accent' : 'Select Accent'}
                </div>
              </div>
              <div className="mt-1 flex gap-1 rounded-lg overflow-hidden">
                <div
                  className={`h-8 flex-1 flex items-center justify-center text-xs font-medium ${selectedColors.background ? 'text-gray-600' : 'text-gray-400 bg-gray-100'}`}
                  style={selectedColors.background ? { backgroundColor: selectedColors.background.color } : undefined}
                >
                  {selectedColors.background ? 'Background' : 'Select Background'}
                </div>
                <div
                  className={`h-8 flex-1 flex items-center justify-center text-xs font-medium ${selectedColors.accentSoft ? 'text-gray-700' : 'text-gray-400 bg-gray-100'}`}
                  style={selectedColors.accentSoft ? { backgroundColor: selectedColors.accentSoft.color } : undefined}
                >
                  {selectedColors.accentSoft ? 'Soft Accent' : 'Select Soft Accent'}
                </div>
              </div>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                {selectedColors.primary && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">Primary: {selectedColors.primary.color}</span>
                )}
                {selectedColors.secondary && (
                  <span className="px-2 py-1 bg-cyan-100 text-cyan-700 rounded">Secondary: {selectedColors.secondary.color}</span>
                )}
                {selectedColors.accent && (
                  <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded">Accent: {selectedColors.accent.color}</span>
                )}
                {selectedColors.background && (
                  <span className="px-2 py-1 bg-slate-100 text-slate-700 rounded">Background: {selectedColors.background.color}</span>
                )}
                {selectedColors.accentSoft && (
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded">Soft: {selectedColors.accentSoft.color}</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mix & Match Preview (Typography) */}
      {explorationType === 'typography' && mixMatchMode && (selectedHeadingOption || selectedBodyOption) && (
        <div className="px-6 pt-4">
          <div className="max-w-5xl mx-auto">
            <div className="bg-white rounded-xl border-2 border-purple-200 p-6 shadow-sm">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <span className="text-xs font-medium text-purple-600 uppercase tracking-wide">Live Preview</span>
                  <h3
                    className="text-2xl font-semibold text-gray-900 mt-2"
                    style={{ fontFamily: selectedHeadingOption ? `"${selectedHeadingOption.heading}", sans-serif` : 'inherit' }}
                  >
                    {selectedHeadingOption ? 'The quick brown fox jumps over the lazy dog' : 'Select a heading font...'}
                  </h3>
                  <p
                    className="text-base text-gray-600 mt-3 leading-relaxed"
                    style={{ fontFamily: selectedBodyOption ? `"${selectedBodyOption.body}", sans-serif` : 'inherit' }}
                  >
                    {selectedBodyOption
                      ? 'Pack my box with five dozen liquor jugs. The five boxing wizards jump quickly. How vexingly quick daft zebras jump!'
                      : 'Select a body font...'}
                  </p>
                </div>
                <div className="ml-6 text-right text-sm">
                  <div className={`${selectedHeadingOption ? 'text-blue-600' : 'text-gray-400'}`}>
                    <span className="text-xs uppercase tracking-wide">Heading:</span>
                    <div className="font-medium">{selectedHeadingOption?.heading || 'None'}</div>
                  </div>
                  <div className={`mt-2 ${selectedBodyOption ? 'text-green-600' : 'text-gray-400'}`}>
                    <span className="text-xs uppercase tracking-wide">Body:</span>
                    <div className="font-medium">{selectedBodyOption?.body || 'None'}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Options Grid */}
      <div className="flex-1 p-6 overflow-auto">
        <div className="max-w-5xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {explorationType === 'typography' ? (
            // Typography cards with mix-match support
            options.map((option) => (
              <TypographyCard
                key={option.id}
                option={option}
                selected={!mixMatchMode && selectedOption?.id === option.id}
                onClick={() => !mixMatchMode && handleSelect(option)}
                disabled={submitting}
                mixMatchMode={mixMatchMode}
                headingSelected={selectedHeadingOption?.id === option.id}
                bodySelected={selectedBodyOption?.id === option.id}
                onHeadingClick={() => setSelectedHeadingOption(option)}
                onBodyClick={() => setSelectedBodyOption(option)}
              />
            ))
          ) : (
            // Palette cards with mix-match support
            options.map((option) => (
              <PaletteCard
                key={option.id}
                option={option}
                selected={!mixMatchMode && selectedOption?.id === option.id}
                onClick={() => !mixMatchMode && handleSelect(option)}
                disabled={submitting}
                mixMatchMode={mixMatchMode}
                selectedColors={{
                  primary: selectedColors.primary?.option.id === option.id,
                  secondary: selectedColors.secondary?.option.id === option.id,
                  accent: selectedColors.accent?.option.id === option.id,
                  background: selectedColors.background?.option.id === option.id,
                  accentSoft: selectedColors.accentSoft?.option.id === option.id,
                }}
                onColorClick={(colorKey) => handleColorSelect(option, colorKey)}
              />
            ))
          )}
        </div>
      </div>

      {/* Action Bar */}
      <div className="p-4 bg-white border-t">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="text-sm text-gray-500">
            {mixMatchMode ? (
              explorationType === 'typography' ? (
                <span>
                  {selectedHeadingOption && selectedBodyOption ? (
                    <>
                      Mixed: <strong className="text-blue-600">{selectedHeadingOption.heading}</strong>
                      {' + '}
                      <strong className="text-green-600">{selectedBodyOption.body}</strong>
                    </>
                  ) : (
                    <>
                      {selectedHeadingOption && (
                        <span>Heading: <strong className="text-blue-600">{selectedHeadingOption.heading}</strong></span>
                      )}
                      {selectedHeadingOption && !selectedBodyOption && ' — '}
                      {!selectedHeadingOption && !selectedBodyOption && 'Click on heading or body text in the cards above'}
                      {!selectedBodyOption && selectedHeadingOption && <span className="text-gray-400">Select a body font</span>}
                      {selectedBodyOption && !selectedHeadingOption && (
                        <span>Body: <strong className="text-green-600">{selectedBodyOption.body}</strong> — <span className="text-gray-400">Select a heading font</span></span>
                      )}
                    </>
                  )}
                </span>
              ) : (
                <span>
                  {allPaletteColorsSelected ? (
                    <>Mixed palette ready — <strong className="text-purple-600">5/5 colors selected</strong></>
                  ) : (
                    <>
                      <strong className="text-purple-600">{Object.keys(selectedColors).length}/5</strong> colors selected
                      {Object.keys(selectedColors).length > 0 && ' — '}
                      {Object.keys(selectedColors).length === 0 && ' — Click on color swatches above'}
                      {Object.keys(selectedColors).length > 0 && Object.keys(selectedColors).length < 5 && (
                        <span className="text-gray-400">Select remaining colors</span>
                      )}
                    </>
                  )}
                </span>
              )
            ) : selectedOption ? (
              <span>
                Selected: <strong>{selectedOption.name}</strong>
              </span>
            ) : (
              <span>Select an option to continue</span>
            )}
          </div>
          <div className="flex gap-3">
            {explorationDepth < maxDepth - 1 && !mixMatchMode && (
              <Button
                variant="outline"
                onClick={handleRefine}
                disabled={!selectedOption || submitting}
              >
                {submitting ? 'Loading...' : 'Show Similar Options'}
              </Button>
            )}
            <Button
              onClick={handleLockIn}
              disabled={!canLockIn || submitting}
              className="bg-green-600 hover:bg-green-700"
            >
              {submitting ? 'Loading...' : (
                explorationType === 'palette'
                  ? 'Fine-tune This Palette'
                  : 'Lock In This Choice'
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
