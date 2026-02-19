/**
 * Visual option picker for a single dimension.
 * Shows 3-4 option cards with miniature component previews,
 * plus an optional fine-tune slider.
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import ComponentPreview from './ComponentPreview';
import type { DimensionDefinition, DimensionOption } from '@/types';

interface DimensionPickerProps {
  dimension: DimensionDefinition;
  componentType: string;
  selectedOptionId: string | null;
  fineTunedValue: string | null;
  allChoices: Record<string, { value: string; css_property: string }>;
  colors?: Record<string, string> | null;
  typography?: Record<string, string> | null;
  onSelect: (option: DimensionOption, fineTunedValue?: string) => void;
}

export default function DimensionPicker({
  dimension,
  componentType,
  selectedOptionId,
  fineTunedValue,
  allChoices,
  colors,
  typography,
  onSelect,
}: DimensionPickerProps) {
  // Slider state
  const selectedOption = dimension.options.find(o => o.id === selectedOptionId);
  const currentValue = fineTunedValue || selectedOption?.value || '';

  const [sliderValue, setSliderValue] = useState<number | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  // Parse numeric value from the current selection for slider init
  useEffect(() => {
    if (dimension.fine_tune && currentValue) {
      const numMatch = currentValue.match(/^([\d.]+)/);
      if (numMatch) {
        setSliderValue(parseFloat(numMatch[1]));
      }
    }
  }, [currentValue, dimension.fine_tune]);

  // Build preview styles: merge all previous choices + current option
  const getPreviewStyles = useCallback((optionValue: string) => {
    const styles: Record<string, string> = {};
    // Apply all previous dimension choices
    for (const [, choice] of Object.entries(allChoices)) {
      styles[choice.css_property] = choice.value;
    }
    // Override with this option's value
    styles[dimension.css_property] = optionValue;
    return styles;
  }, [allChoices, dimension.css_property]);

  const handleOptionClick = (option: DimensionOption) => {
    onSelect(option);
    // Reset slider to match option value
    if (dimension.fine_tune) {
      const numMatch = option.value.match(/^([\d.]+)/);
      if (numMatch) {
        setSliderValue(parseFloat(numMatch[1]));
      }
    }
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setSliderValue(val);

    // Debounce the API call
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      if (selectedOption && dimension.fine_tune) {
        const newValue = `${val}${dimension.fine_tune.unit}`;
        onSelect(selectedOption, newValue);
      }
    }, 200);
  };

  return (
    <div className="space-y-4">
      {/* Dimension label */}
      <h3 className="text-lg font-semibold text-gray-800">{dimension.label}</h3>

      {/* Option cards */}
      <div className="grid gap-3" style={{ gridTemplateColumns: `repeat(${Math.min(dimension.options.length, 4)}, 1fr)` }}>
        {dimension.options.map((option) => {
          const isSelected = option.id === selectedOptionId;
          const previewStyles = getPreviewStyles(option.value);

          return (
            <button
              key={option.id}
              onClick={() => handleOptionClick(option)}
              className={`
                relative rounded-xl border-2 overflow-hidden transition-all cursor-pointer
                ${isSelected
                  ? 'border-blue-500 ring-2 ring-blue-200 shadow-md'
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                }
              `}
            >
              {/* Mini preview */}
              <div className="bg-gray-50 border-b" style={{ minHeight: '80px' }}>
                <ComponentPreview
                  componentType={componentType}
                  styles={previewStyles}
                  colors={colors}
                  typography={typography}
                  compact
                />
              </div>
              {/* Label */}
              <div className={`px-3 py-2 text-sm font-medium ${isSelected ? 'text-blue-700 bg-blue-50' : 'text-gray-700'}`}>
                {option.label}
              </div>
              {/* Selected check */}
              {isSelected && (
                <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Fine-tune slider */}
      {dimension.fine_tune && selectedOptionId && sliderValue !== null && (
        <div className="bg-gray-50 rounded-lg p-4 border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Fine-tune</span>
            <span className="text-sm font-mono text-gray-800">
              {sliderValue}{dimension.fine_tune.unit}
            </span>
          </div>
          <input
            type="range"
            min={dimension.fine_tune.min}
            max={dimension.fine_tune.max}
            step={dimension.fine_tune.step}
            value={sliderValue}
            onChange={handleSliderChange}
            className="w-full accent-blue-500"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>{dimension.fine_tune.min}{dimension.fine_tune.unit}</span>
            <span>{dimension.fine_tune.max}{dimension.fine_tune.unit}</span>
          </div>
        </div>
      )}
    </div>
  );
}
