import { useMemo } from 'react';

interface EstablishedPreferencesProps {
  preferences: Record<string, string> | null;
}

// Format property names from camelCase/snake_case to readable text
const formatPropertyName = (prop: string): string => {
  // Handle camelCase (e.g., backgroundColor -> Background Color)
  const spaced = prop.replace(/([A-Z])/g, ' $1');
  // Handle snake_case (e.g., border_radius -> Border Radius)
  const formatted = spaced.replace(/_/g, ' ');
  // Capitalize first letter of each word
  return formatted
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
    .trim();
};

// Format values for display
const formatValue = (value: string): string => {
  // If it's a hex color, show color swatch reference
  if (value.startsWith('#')) {
    return value.toUpperCase();
  }
  // If it has px/rem/em units, keep as is
  if (/\d+(px|rem|em|%)$/.test(value)) {
    return value;
  }
  // Capitalize simple values
  return value.charAt(0).toUpperCase() + value.slice(1);
};

// Get category icon for preference
const getCategoryIcon = (prop: string): string => {
  const propLower = prop.toLowerCase();
  if (propLower.includes('color') || propLower.includes('background')) {
    return '🎨';
  }
  if (propLower.includes('font') || propLower.includes('weight') || propLower.includes('size')) {
    return '📝';
  }
  if (propLower.includes('radius') || propLower.includes('border') || propLower.includes('shadow')) {
    return '◼️';
  }
  if (propLower.includes('padding') || propLower.includes('margin') || propLower.includes('gap')) {
    return '📐';
  }
  return '✓';
};

// Check if value is a color
const isColor = (value: string): boolean => {
  return value.startsWith('#') || value.startsWith('rgb') || value.startsWith('hsl');
};

export default function EstablishedPreferences({ preferences }: EstablishedPreferencesProps) {
  const preferenceList = useMemo(() => {
    if (!preferences || Object.keys(preferences).length === 0) {
      return [];
    }
    return Object.entries(preferences)
      // Filter out internal exploration state (starts with _) and non-string values
      .filter(([prop, value]) => !prop.startsWith('_') && typeof value === 'string')
      .map(([prop, value]) => ({
        property: prop,
        value: value,
        displayName: formatPropertyName(prop),
        displayValue: formatValue(value),
        icon: getCategoryIcon(prop),
        isColor: isColor(value),
      }));
  }, [preferences]);

  if (preferenceList.length === 0) {
    return null;
  }

  return (
    <div
      className="bg-white border-b py-2 px-4"
      agent-handle="established-preferences-display"
    >
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            Your Preferences
          </span>
          <span className="text-xs text-gray-400">
            ({preferenceList.length} established)
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          {preferenceList.map(({ property, value, displayName, displayValue, icon, isColor: isColorValue }) => (
            <div
              key={property}
              className="inline-flex items-center gap-1.5 px-2 py-1 bg-gray-100 rounded-full text-xs"
              title={`${displayName}: ${displayValue}`}
            >
              <span className="text-gray-400">{icon}</span>
              <span className="font-medium text-gray-700">{displayName}:</span>
              {isColorValue ? (
                <span className="flex items-center gap-1">
                  <span
                    className="w-3 h-3 rounded-full border border-gray-300"
                    style={{ backgroundColor: value }}
                  />
                  <span className="text-gray-600">{displayValue}</span>
                </span>
              ) : (
                <span className="text-gray-600">{displayValue}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
