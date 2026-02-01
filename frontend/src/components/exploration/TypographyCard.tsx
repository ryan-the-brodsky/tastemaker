import { useEffect } from 'react';
import type { ExplorationOption } from '@/services/api';

interface TypographyCardProps {
  option: ExplorationOption;
  selected: boolean;
  onClick: () => void;
  disabled?: boolean;
  // Mix & match mode
  mixMatchMode?: boolean;
  headingSelected?: boolean;
  bodySelected?: boolean;
  onHeadingClick?: () => void;
  onBodyClick?: () => void;
}

// Load Google Font dynamically
const loadGoogleFont = (fontName: string) => {
  const linkId = `google-font-${fontName.replace(/\s+/g, '-')}`;
  if (document.getElementById(linkId)) return;

  const link = document.createElement('link');
  link.id = linkId;
  link.rel = 'stylesheet';
  link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(fontName)}:wght@400;600;700&display=swap`;
  document.head.appendChild(link);
};

export default function TypographyCard({
  option,
  selected,
  onClick,
  disabled,
  mixMatchMode = false,
  headingSelected = false,
  bodySelected = false,
  onHeadingClick,
  onBodyClick,
}: TypographyCardProps) {
  const headingFont = option.heading || 'Inter';
  const bodyFont = option.body || 'Inter';

  // Load fonts on mount
  useEffect(() => {
    loadGoogleFont(headingFont);
    if (bodyFont !== headingFont) {
      loadGoogleFont(bodyFont);
    }
  }, [headingFont, bodyFont]);

  const handleHeadingClick = (e: React.MouseEvent) => {
    if (mixMatchMode && onHeadingClick) {
      e.stopPropagation();
      onHeadingClick();
    }
  };

  const handleBodyClick = (e: React.MouseEvent) => {
    if (mixMatchMode && onBodyClick) {
      e.stopPropagation();
      onBodyClick();
    }
  };

  // In mix-match mode, show selection state per section
  const showFullSelection = !mixMatchMode && selected;
  const showHeadingSelection = mixMatchMode && headingSelected;
  const showBodySelection = mixMatchMode && bodySelected;

  return (
    <div
      className={`
        relative bg-white rounded-xl overflow-hidden transition-all duration-200
        border-2 hover:shadow-lg
        ${showFullSelection ? 'border-primary ring-2 ring-primary/30 shadow-lg' : 'border-gray-200 hover:border-gray-300'}
        ${disabled ? 'opacity-50 pointer-events-none' : ''}
        ${!mixMatchMode ? 'cursor-pointer' : ''}
      `}
      onClick={!mixMatchMode ? onClick : undefined}
    >
      {/* Full selection indicator (non-mix-match mode) */}
      {showFullSelection && (
        <div className="absolute top-2 right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center z-10">
          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      )}

      {/* Typography preview */}
      <div className="p-4 pb-2 min-h-[100px] flex flex-col justify-center">
        {/* Heading sample - clickable in mix-match mode */}
        <div
          className={`
            ${mixMatchMode ? 'cursor-pointer rounded-lg px-2 py-1 -mx-2 transition-all' : ''}
            ${mixMatchMode && !showHeadingSelection ? 'hover:bg-blue-50' : ''}
            ${showHeadingSelection ? 'bg-blue-100 ring-2 ring-blue-500' : ''}
          `}
          onClick={handleHeadingClick}
        >
          {showHeadingSelection && (
            <span className="text-[10px] font-medium text-blue-600 uppercase tracking-wide">Heading Selected</span>
          )}
          <h3
            className="text-xl font-semibold text-gray-900"
            style={{ fontFamily: `"${headingFont}", sans-serif` }}
          >
            The quick brown fox
          </h3>
        </div>

        {/* Body sample - clickable in mix-match mode */}
        <div
          className={`
            mt-2
            ${mixMatchMode ? 'cursor-pointer rounded-lg px-2 py-1 -mx-2 transition-all' : ''}
            ${mixMatchMode && !showBodySelection ? 'hover:bg-green-50' : ''}
            ${showBodySelection ? 'bg-green-100 ring-2 ring-green-500' : ''}
          `}
          onClick={handleBodyClick}
        >
          {showBodySelection && (
            <span className="text-[10px] font-medium text-green-600 uppercase tracking-wide">Body Selected</span>
          )}
          <p
            className="text-sm text-gray-600 leading-relaxed"
            style={{ fontFamily: `"${bodyFont}", sans-serif` }}
          >
            Pack my box with five dozen liquor jugs.
          </p>
        </div>
      </div>

      {/* Info section */}
      <div className="p-3 pt-0 border-t border-gray-100">
        <h4 className="font-semibold text-sm">{option.name}</h4>
        <div className="flex gap-3 mt-1 text-xs text-gray-500">
          <span className={showHeadingSelection ? 'text-blue-600 font-medium' : ''}>
            <span className={showHeadingSelection ? 'text-blue-400' : 'text-gray-400'}>H:</span> {headingFont}
          </span>
          <span className={showBodySelection ? 'text-green-600 font-medium' : ''}>
            <span className={showBodySelection ? 'text-green-400' : 'text-gray-400'}>B:</span> {bodyFont}
          </span>
        </div>
        {option.description && (
          <p className="text-xs text-gray-400 mt-1 line-clamp-1">{option.description}</p>
        )}
      </div>
    </div>
  );
}
