import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/shadcn/Button';

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

export interface DerivedColors {
  primaryLight: string;
  primaryDark: string;
  secondaryLight: string;
  secondaryDark: string;
  accentLight: string;
  border: string;
  textOnPrimary: string;
  textOnSecondary: string;
  textOnAccent: string;
  textPrimary: string;
  textSecondary: string;
}

interface ColorEditorProps {
  initialPalette: ColorPalette;
  onSave: (palette: ColorPalette, derived: DerivedColors) => void;
  onCancel: () => void;
}

// Color utility functions
function hexToHsl(hex: string): { h: number; s: number; l: number } {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return { h: 0, s: 0, l: 0 };

  let r = parseInt(result[1], 16) / 255;
  let g = parseInt(result[2], 16) / 255;
  let b = parseInt(result[3], 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0;
  let s = 0;
  const l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }

  return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
}

function hslToHex(h: number, s: number, l: number): string {
  s /= 100;
  l /= 100;

  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs((h / 60) % 2 - 1));
  const m = l - c / 2;

  let r = 0, g = 0, b = 0;

  if (0 <= h && h < 60) { r = c; g = x; b = 0; }
  else if (60 <= h && h < 120) { r = x; g = c; b = 0; }
  else if (120 <= h && h < 180) { r = 0; g = c; b = x; }
  else if (180 <= h && h < 240) { r = 0; g = x; b = c; }
  else if (240 <= h && h < 300) { r = x; g = 0; b = c; }
  else if (300 <= h && h < 360) { r = c; g = 0; b = x; }

  const toHex = (n: number) => {
    const hex = Math.round((n + m) * 255).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };

  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

function adjustLightness(hex: string, amount: number): string {
  const hsl = hexToHsl(hex);
  const newL = Math.max(0, Math.min(100, hsl.l + amount));
  return hslToHex(hsl.h, hsl.s, newL);
}

function getContrastColor(hex: string): string {
  const hsl = hexToHsl(hex);
  return hsl.l > 50 ? '#111827' : '#ffffff';
}

// getLuminance can be used for contrast calculations in the future
// function getLuminance(hex: string): number {
//   const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
//   if (!result) return 0;
//   const r = parseInt(result[1], 16) / 255;
//   const g = parseInt(result[2], 16) / 255;
//   const b = parseInt(result[3], 16) / 255;
//   const [rs, gs, bs] = [r, g, b].map(c =>
//     c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
//   );
//   return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
// }

// Calculate all derived colors from a palette
function calculateDerivedColors(palette: ColorPalette): DerivedColors {
  return {
    primaryLight: adjustLightness(palette.primary, 15),
    primaryDark: adjustLightness(palette.primary, -15),
    secondaryLight: adjustLightness(palette.secondary, 15),
    secondaryDark: adjustLightness(palette.secondary, -15),
    accentLight: adjustLightness(palette.accent, 20),
    border: adjustLightness(palette.background, -10),
    textOnPrimary: getContrastColor(palette.primary),
    textOnSecondary: getContrastColor(palette.secondary),
    textOnAccent: getContrastColor(palette.accent),
    textPrimary: '#111827',
    textSecondary: '#6b7280',
  };
}

// Color slider component
function ColorSlider({
  label,
  colorKey,
  value,
  originalValue,
  onChange,
  onRestore,
}: {
  label: string;
  colorKey: string;
  value: string;
  originalValue: string;
  onChange: (key: string, value: string) => void;
  onRestore: (key: string) => void;
}) {
  const hsl = hexToHsl(value);
  const hasChanged = value !== originalValue;

  return (
    <div className="space-y-3 p-4 bg-white rounded-lg border">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm">{label}</span>
          {hasChanged && (
            <button
              onClick={() => onRestore(colorKey)}
              className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-gray-100 transition-colors"
              title={`Restore to ${originalValue}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              Restore
            </button>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-8 h-8 rounded-md border-2 border-gray-200"
            style={{ backgroundColor: value }}
          />
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(colorKey, e.target.value)}
            className="w-20 text-xs font-mono px-2 py-1 border rounded"
          />
        </div>
      </div>

      {/* Hue slider */}
      <div className="space-y-1">
        <label className="text-xs text-gray-500">Hue</label>
        <input
          type="range"
          min="0"
          max="359"
          value={hsl.h}
          onChange={(e) => onChange(colorKey, hslToHex(parseInt(e.target.value), hsl.s, hsl.l))}
          className="w-full h-2 rounded-lg appearance-none cursor-pointer"
          style={{
            background: `linear-gradient(to right,
              hsl(0, ${hsl.s}%, ${hsl.l}%),
              hsl(60, ${hsl.s}%, ${hsl.l}%),
              hsl(120, ${hsl.s}%, ${hsl.l}%),
              hsl(180, ${hsl.s}%, ${hsl.l}%),
              hsl(240, ${hsl.s}%, ${hsl.l}%),
              hsl(300, ${hsl.s}%, ${hsl.l}%),
              hsl(360, ${hsl.s}%, ${hsl.l}%))`
          }}
        />
      </div>

      {/* Saturation slider */}
      <div className="space-y-1">
        <label className="text-xs text-gray-500">Saturation</label>
        <input
          type="range"
          min="0"
          max="100"
          value={hsl.s}
          onChange={(e) => onChange(colorKey, hslToHex(hsl.h, parseInt(e.target.value), hsl.l))}
          className="w-full h-2 rounded-lg appearance-none cursor-pointer"
          style={{
            background: `linear-gradient(to right,
              hsl(${hsl.h}, 0%, ${hsl.l}%),
              hsl(${hsl.h}, 100%, ${hsl.l}%))`
          }}
        />
      </div>

      {/* Lightness slider */}
      <div className="space-y-1">
        <label className="text-xs text-gray-500">Lightness</label>
        <input
          type="range"
          min="0"
          max="100"
          value={hsl.l}
          onChange={(e) => onChange(colorKey, hslToHex(hsl.h, hsl.s, parseInt(e.target.value)))}
          className="w-full h-2 rounded-lg appearance-none cursor-pointer"
          style={{
            background: `linear-gradient(to right,
              hsl(${hsl.h}, ${hsl.s}%, 0%),
              hsl(${hsl.h}, ${hsl.s}%, 50%),
              hsl(${hsl.h}, ${hsl.s}%, 100%))`
          }}
        />
      </div>
    </div>
  );
}

// Preview components
function PreviewButton({ palette, derived }: { palette: ColorPalette; derived: DerivedColors }) {
  return (
    <div className="space-y-2">
      <span className="text-xs text-gray-500">Buttons</span>
      <div className="flex flex-wrap gap-2">
        <button
          className="px-4 py-2 rounded-lg font-medium transition-all hover:opacity-90"
          style={{
            backgroundColor: palette.primary,
            color: derived.textOnPrimary,
          }}
        >
          Primary
        </button>
        <button
          className="px-4 py-2 rounded-lg font-medium transition-all hover:opacity-90"
          style={{
            backgroundColor: palette.secondary,
            color: derived.textOnSecondary,
          }}
        >
          Secondary
        </button>
        <button
          className="px-4 py-2 rounded-lg font-medium transition-all hover:opacity-90"
          style={{
            backgroundColor: palette.accent,
            color: derived.textOnAccent,
          }}
        >
          Action
        </button>
        <button
          className="px-4 py-2 rounded-lg font-medium border-2"
          style={{
            borderColor: palette.primary,
            color: palette.primary,
            backgroundColor: 'transparent',
          }}
        >
          Outline
        </button>
      </div>
    </div>
  );
}

function PreviewCard({ palette, derived }: { palette: ColorPalette; derived: DerivedColors }) {
  return (
    <div className="space-y-2">
      <span className="text-xs text-gray-500">Card</span>
      <div
        className="p-6 rounded-xl"
        style={{
          backgroundColor: palette.background,
          border: `1px solid ${derived.border}`,
        }}
      >
        <h3
          className="text-lg font-semibold mb-2"
          style={{ color: palette.primary }}
        >
          Card Title
        </h3>
        <p
          className="text-sm mb-4"
          style={{ color: derived.textSecondary }}
        >
          This is a sample card component showing how your colors work together in context.
        </p>
        <div className="flex items-center gap-2">
          <span
            className="px-2 py-1 text-xs rounded-full"
            style={{
              backgroundColor: palette.accentSoft,
              color: getContrastColor(palette.accentSoft),
            }}
          >
            Tag
          </span>
          <span
            className="text-sm font-medium"
            style={{ color: palette.accent }}
          >
            Learn more &rarr;
          </span>
        </div>
      </div>
    </div>
  );
}

function PreviewNavigation({ palette, derived }: { palette: ColorPalette; derived: DerivedColors }) {
  return (
    <div className="space-y-2">
      <span className="text-xs text-gray-500">Navigation</span>
      <div
        className="p-4 rounded-xl flex items-center justify-between"
        style={{ backgroundColor: palette.primary }}
      >
        <span
          className="font-bold"
          style={{ color: derived.textOnPrimary }}
        >
          Brand
        </span>
        <div className="flex gap-6">
          {['Home', 'Products', 'About', 'Contact'].map((item, i) => (
            <span
              key={item}
              className={`text-sm ${i === 0 ? 'font-medium' : 'opacity-80'}`}
              style={{ color: derived.textOnPrimary }}
            >
              {item}
            </span>
          ))}
        </div>
        <button
          className="px-3 py-1.5 rounded-md text-sm font-medium"
          style={{
            backgroundColor: palette.accent,
            color: derived.textOnAccent,
          }}
        >
          Sign Up
        </button>
      </div>
    </div>
  );
}

function PreviewInput({ palette, derived }: { palette: ColorPalette; derived: DerivedColors }) {
  return (
    <div className="space-y-2">
      <span className="text-xs text-gray-500">Form Input</span>
      <div
        className="p-4 rounded-xl"
        style={{ backgroundColor: palette.background }}
      >
        <label
          className="block text-sm font-medium mb-1.5"
          style={{ color: derived.textPrimary }}
        >
          Email Address
        </label>
        <input
          type="email"
          placeholder="you@example.com"
          className="w-full px-3 py-2 rounded-lg outline-none transition-all"
          style={{
            backgroundColor: '#ffffff',
            border: `1px solid ${derived.border}`,
            color: derived.textPrimary,
          }}
        />
        <p
          className="text-xs mt-1.5"
          style={{ color: derived.textSecondary }}
        >
          We&apos;ll never share your email.
        </p>
      </div>
    </div>
  );
}

function DerivedColorsPanel({ derived, palette }: { derived: DerivedColors; palette: ColorPalette }) {
  const derivedItems = [
    { label: 'Primary Light', color: derived.primaryLight },
    { label: 'Primary Dark', color: derived.primaryDark },
    { label: 'Secondary Light', color: derived.secondaryLight },
    { label: 'Secondary Dark', color: derived.secondaryDark },
    { label: 'Accent Light', color: derived.accentLight },
    { label: 'Border', color: derived.border },
    { label: 'Text on Primary', color: derived.textOnPrimary, bg: palette.primary },
    { label: 'Text on Secondary', color: derived.textOnSecondary, bg: palette.secondary },
    { label: 'Text on Accent', color: derived.textOnAccent, bg: palette.accent },
  ];

  return (
    <div className="space-y-2">
      <span className="text-xs text-gray-500 font-medium">Auto-Calculated Derived Colors</span>
      <div className="grid grid-cols-3 gap-2">
        {derivedItems.map(({ label, color, bg }) => (
          <div
            key={label}
            className="p-2 rounded-md text-center"
            style={{
              backgroundColor: bg || color,
              border: `1px solid ${derived.border}`,
            }}
          >
            <span
              className="text-xs font-mono"
              style={{ color: bg ? color : getContrastColor(color) }}
            >
              {color}
            </span>
            <p
              className="text-[10px] mt-0.5"
              style={{ color: bg ? color : getContrastColor(color), opacity: 0.7 }}
            >
              {label}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ColorEditor({ initialPalette, onSave, onCancel }: ColorEditorProps) {
  const [palette, setPalette] = useState<ColorPalette>(initialPalette);
  const [derived, setDerived] = useState<DerivedColors>(calculateDerivedColors(initialPalette));

  // Recalculate derived colors whenever palette changes
  useEffect(() => {
    setDerived(calculateDerivedColors(palette));
  }, [palette]);

  const handleColorChange = useCallback((key: string, value: string) => {
    // Validate hex color format
    if (/^#[0-9A-Fa-f]{6}$/.test(value)) {
      setPalette(prev => ({
        ...prev,
        [key]: value,
      }));
    } else if (value.length <= 7) {
      // Allow partial input while typing
      setPalette(prev => ({
        ...prev,
        [key]: value,
      }));
    }
  }, []);

  const handleSave = useCallback(() => {
    onSave(palette, derived);
  }, [palette, derived, onSave]);

  const handleRestoreColor = useCallback((key: string) => {
    setPalette(prev => ({
      ...prev,
      [key]: initialPalette[key as keyof ColorPalette],
    }));
  }, [initialPalette]);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Fine-tune Your Colors</h1>
            <p className="text-gray-500">
              Adjust each color using the sliders. Preview updates in real-time.
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button onClick={handleSave}>
              Save & Continue
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Color Controls */}
          <div className="col-span-4 space-y-4">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Core Palette</h2>
            <ColorSlider
              label="Primary"
              colorKey="primary"
              value={palette.primary}
              originalValue={initialPalette.primary}
              onChange={handleColorChange}
              onRestore={handleRestoreColor}
            />
            <ColorSlider
              label="Secondary"
              colorKey="secondary"
              value={palette.secondary}
              originalValue={initialPalette.secondary}
              onChange={handleColorChange}
              onRestore={handleRestoreColor}
            />
            <ColorSlider
              label="Accent"
              colorKey="accent"
              value={palette.accent}
              originalValue={initialPalette.accent}
              onChange={handleColorChange}
              onRestore={handleRestoreColor}
            />
            <ColorSlider
              label="Accent Soft"
              colorKey="accentSoft"
              value={palette.accentSoft}
              originalValue={initialPalette.accentSoft}
              onChange={handleColorChange}
              onRestore={handleRestoreColor}
            />
            <ColorSlider
              label="Background"
              colorKey="background"
              value={palette.background}
              originalValue={initialPalette.background}
              onChange={handleColorChange}
              onRestore={handleRestoreColor}
            />
          </div>

          {/* Live Preview */}
          <div className="col-span-8 space-y-4">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Live Preview</h2>

            <div className="bg-white rounded-xl p-6 shadow-sm space-y-6">
              <PreviewNavigation palette={palette} derived={derived} />
              <PreviewCard palette={palette} derived={derived} />
              <div className="grid grid-cols-2 gap-6">
                <PreviewButton palette={palette} derived={derived} />
                <PreviewInput palette={palette} derived={derived} />
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm">
              <DerivedColorsPanel derived={derived} palette={palette} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
