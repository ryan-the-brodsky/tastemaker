import type { ExplorationOption } from '@/services/api';

export type ColorKey = 'primary' | 'secondary' | 'accent' | 'background' | 'accentSoft';

interface PaletteCardProps {
  option: ExplorationOption;
  selected: boolean;
  onClick: () => void;
  disabled?: boolean;
  // Mix & match mode
  mixMatchMode?: boolean;
  selectedColors?: Partial<Record<ColorKey, boolean>>;
  onColorClick?: (colorKey: ColorKey) => void;
}

const colorLabels: Record<ColorKey, string> = {
  primary: 'Primary',
  secondary: 'Secondary',
  accent: 'Accent',
  background: 'Background',
  accentSoft: 'Soft Accent',
};

const colorRingColors: Record<ColorKey, string> = {
  primary: 'ring-blue-500',
  secondary: 'ring-cyan-500',
  accent: 'ring-amber-500',
  background: 'ring-slate-500',
  accentSoft: 'ring-yellow-500',
};

export default function PaletteCard({
  option,
  selected,
  onClick,
  disabled,
  mixMatchMode = false,
  selectedColors = {},
  onColorClick,
}: PaletteCardProps) {
  const handleColorClick = (e: React.MouseEvent, colorKey: ColorKey) => {
    if (mixMatchMode && onColorClick) {
      e.stopPropagation();
      onColorClick(colorKey);
    }
  };

  const showFullSelection = !mixMatchMode && selected;

  const renderColorSwatch = (
    colorKey: ColorKey,
    color: string,
    className: string = 'flex-1'
  ) => {
    const isSelected = mixMatchMode && selectedColors[colorKey];

    return (
      <div
        className={`
          ${className} relative transition-all
          ${mixMatchMode ? 'cursor-pointer hover:opacity-80' : ''}
          ${isSelected ? `ring-4 ${colorRingColors[colorKey]} ring-inset z-10` : ''}
        `}
        style={{ backgroundColor: color }}
        title={`${colorLabels[colorKey]}: ${color}`}
        onClick={(e) => handleColorClick(e, colorKey)}
      >
        {isSelected && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-white/90 rounded-full p-1">
              <svg className="w-4 h-4 text-gray-800" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        )}
      </div>
    );
  };

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

      {/* Color swatches - main display */}
      <div className="flex h-24">
        {renderColorSwatch('primary', option.primary || '#1e3a8a')}
        {renderColorSwatch('secondary', option.secondary || '#0891b2')}
        {renderColorSwatch('accent', option.accent || '#f59e0b')}
      </div>

      {/* Smaller background/soft accent strip */}
      <div className="flex h-6">
        {renderColorSwatch('background', option.background || '#f8fafc')}
        {renderColorSwatch('accentSoft', option.accentSoft || '#fbbf24')}
      </div>

      {/* Info section */}
      <div className="p-3">
        <h3 className="font-semibold text-sm">{option.name}</h3>
        <p className="text-xs text-gray-500 mt-0.5">{option.category}</p>
        {option.description && (
          <p className="text-xs text-gray-400 mt-1 line-clamp-2">{option.description}</p>
        )}
      </div>
    </div>
  );
}
