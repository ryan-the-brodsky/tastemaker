import type { CSSProperties, ReactNode } from 'react';

interface ComponentRendererProps {
  componentType: string;
  styles: Record<string, unknown>;
  context: string;
}

// Helper to get font family CSS value
const getFontFamily = (family: unknown): string => {
  const families: Record<string, string> = {
    'system': 'system-ui, -apple-system, sans-serif',
    'sans-serif': 'Inter, Helvetica, Arial, sans-serif',
    'serif': 'Georgia, Cambria, serif',
    'mono': 'Menlo, Monaco, Consolas, monospace',
  };
  if (typeof family === 'string') {
    // If it's already a CSS font-family string (from Claude API), use it directly
    if (family.includes(',') || family.includes('system-ui')) {
      return family;
    }
    return families[family] || families['system'];
  }
  return families['system'];
};

// Helper to get border radius - handles both number and string values
const getBorderRadius = (value: unknown): string => {
  if (typeof value === 'number') {
    return value === 9999 ? '9999px' : `${value}px`;
  }
  if (typeof value === 'string') {
    // Already has units (from Claude API)
    return value;
  }
  return '8px';
};

// Helper to get padding - handles both number and string values
const getPadding = (value: unknown, defaultVal: number = 16): string => {
  if (typeof value === 'number') {
    return `${value}px`;
  }
  if (typeof value === 'string') {
    return value; // Already has units
  }
  return `${defaultVal}px`;
};

export default function ComponentRenderer({
  componentType,
  styles,
  // context is available for future use with mock page templates
}: ComponentRendererProps) {
  const renderButton = () => {
    // Support both Claude API format (camelCase CSS) and deterministic format (snake_case)
    const buttonStyles: CSSProperties = {
      cursor: 'pointer',
    };

    // Border radius - support both formats
    buttonStyles.borderRadius = getBorderRadius(styles.borderRadius || styles.border_radius);

    // Padding - support both formats
    if (styles.padding) {
      // Claude API format: "12px 24px"
      buttonStyles.padding = styles.padding as string;
    } else {
      buttonStyles.paddingLeft = getPadding(styles.padding_x, 16);
      buttonStyles.paddingRight = getPadding(styles.padding_x, 16);
      buttonStyles.paddingTop = getPadding(styles.padding_y, 10);
      buttonStyles.paddingBottom = getPadding(styles.padding_y, 10);
    }

    // Font weight - support both formats
    buttonStyles.fontWeight = (styles.fontWeight || styles.font_weight || 500) as number;

    // Font size - support both formats
    const fontSize = styles.fontSize || styles.font_size;
    buttonStyles.fontSize = typeof fontSize === 'string' ? fontSize : `${fontSize || 14}px`;

    // Font family - support both formats
    buttonStyles.fontFamily = getFontFamily(styles.fontFamily || styles.font_family);

    // Text transform
    buttonStyles.textTransform = (styles.textTransform || styles.text_transform || 'none') as CSSProperties['textTransform'];

    // Transition
    const transition = styles.transition;
    buttonStyles.transition = transition === 'fast' ? 'all 0.1s' : transition === 'smooth' ? 'all 0.3s' : 'none';

    // Colors - prioritize Claude API format (direct CSS values)
    if (styles.backgroundColor) {
      // Claude API format - direct CSS color
      buttonStyles.background = styles.backgroundColor as string;
      buttonStyles.color = (styles.color as string) || 'white';
      buttonStyles.border = styles.borderWidth
        ? `${styles.borderWidth} solid ${styles.borderColor || 'transparent'}`
        : 'none';
    } else if (styles.background_style === 'gradient') {
      // Deterministic format - gradient
      buttonStyles.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
      buttonStyles.color = 'white';
      buttonStyles.border = 'none';
    } else if (styles.background_style === 'outline') {
      // Deterministic format - outline
      buttonStyles.background = 'transparent';
      buttonStyles.color = '#333';
      buttonStyles.border = '2px solid #333';
    } else {
      // Deterministic format - solid (default)
      buttonStyles.background = '#1a1a2e';
      buttonStyles.color = 'white';
      buttonStyles.border = 'none';
    }

    // Shadow - support both formats
    const shadow = styles.boxShadow || styles.shadow;
    if (typeof shadow === 'string') {
      if (shadow.includes('rgba') || shadow.includes('rgb') || shadow === 'none') {
        // Claude API format - direct CSS shadow
        buttonStyles.boxShadow = shadow;
      } else {
        // Deterministic format - named shadows
        const shadows: Record<string, string> = {
          none: 'none',
          sm: '0 1px 2px rgba(0,0,0,0.05)',
          md: '0 4px 6px rgba(0,0,0,0.1)',
          lg: '0 10px 15px rgba(0,0,0,0.1)',
        };
        buttonStyles.boxShadow = shadows[shadow] || 'none';
      }
    }

    return (
      <button style={buttonStyles}>
        Get Started
      </button>
    );
  };

  const renderInput = () => {
    // Check if using Claude API format
    const isClaudeFormat = styles.backgroundColor || styles.borderRadius || styles.borderColor;

    if (isClaudeFormat) {
      // Claude API format - apply styles directly
      const inputStyles: CSSProperties = {
        borderRadius: getBorderRadius(styles.borderRadius),
        borderWidth: (styles.borderWidth as string) || '1px',
        borderStyle: 'solid',
        borderColor: (styles.borderColor as string) || '#d1d5db',
        padding: (styles.padding as string) || '10px 12px',
        fontSize: (styles.fontSize as string) || '14px',
        fontFamily: getFontFamily(styles.fontFamily),
        fontWeight: (styles.fontWeight as number) || 400,
        background: (styles.backgroundColor as string) || 'white',
        color: (styles.color as string) || '#1f2937',
        outline: 'none',
        width: '200px',
        boxShadow: (styles.boxShadow as string) || 'none',
      };

      const labelStyles: CSSProperties = {
        fontSize: '14px',
        fontWeight: 500,
        color: (styles.color as string) || '#374151',
        fontFamily: getFontFamily(styles.fontFamily),
      };

      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <label style={labelStyles}>Email address</label>
          <input style={inputStyles} placeholder="you@example.com" />
        </div>
      );
    }

    // Fallback: Deterministic format
    const inputStyles: CSSProperties = {
      borderRadius: `${styles.border_radius || 4}px`,
      borderWidth: `${styles.border_width || 1}px`,
      borderStyle: 'solid',
      borderColor: styles.border_color === 'gray-500' ? '#6b7280' : styles.border_color === 'gray-400' ? '#9ca3af' : '#d1d5db',
      paddingLeft: `${styles.padding_x || 12}px`,
      paddingRight: `${styles.padding_x || 12}px`,
      paddingTop: `${styles.padding_y || 10}px`,
      paddingBottom: `${styles.padding_y || 10}px`,
      fontSize: `${styles.font_size || 14}px`,
      background: styles.background === 'gray-50' ? '#f9fafb' : styles.background === 'transparent' ? 'transparent' : 'white',
      outline: 'none',
      width: '200px',
    };

    const containerStyles: CSSProperties = {
      display: 'flex',
      flexDirection: 'column',
      gap: '4px',
    };

    const labelStyles: CSSProperties = {
      fontSize: '14px',
      fontWeight: 500,
      color: '#374151',
    };

    if (styles.label_position === 'floating') {
      return (
        <div style={{ position: 'relative', ...containerStyles }}>
          <input
            style={{
              ...inputStyles,
              paddingTop: '20px',
            }}
            placeholder=" "
          />
          <label
            style={{
              position: 'absolute',
              left: `${styles.padding_x || 12}px`,
              top: '8px',
              fontSize: '12px',
              color: '#6b7280',
            }}
          >
            Email address
          </label>
        </div>
      );
    }

    if (styles.label_position === 'inline') {
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={labelStyles}>Email:</label>
          <input style={inputStyles} placeholder="you@example.com" />
        </div>
      );
    }

    return (
      <div style={containerStyles}>
        <label style={labelStyles}>Email address</label>
        <input style={inputStyles} placeholder="you@example.com" />
      </div>
    );
  };

  const renderCard = () => {
    // Check if using Claude API format
    const isClaudeFormat = styles.backgroundColor || styles.borderRadius || styles.boxShadow;

    if (isClaudeFormat) {
      // Claude API format - apply styles directly
      const cardStyles: CSSProperties = {
        borderRadius: getBorderRadius(styles.borderRadius),
        padding: (styles.padding as string) || '24px',
        background: (styles.backgroundColor as string) || 'white',
        color: (styles.color as string) || '#1f2937',
        width: '280px',
        boxShadow: (styles.boxShadow as string) || 'none',
        fontFamily: getFontFamily(styles.fontFamily),
      };

      if (styles.borderWidth && styles.borderColor) {
        cardStyles.border = `${styles.borderWidth} solid ${styles.borderColor}`;
      }

      return (
        <div style={cardStyles}>
          <h3 style={{
            margin: 0,
            marginBottom: '8px',
            fontWeight: (styles.fontWeight as number) || 600,
            color: (styles.color as string) || '#1f2937',
          }}>
            Card Title
          </h3>
          <p style={{
            margin: 0,
            fontSize: (styles.fontSize as string) || '14px',
            opacity: 0.7,
          }}>
            This is a sample card with some content.
          </p>
        </div>
      );
    }

    // Fallback: Deterministic format
    const cardStyles: CSSProperties = {
      borderRadius: `${styles.border_radius || 8}px`,
      padding: `${styles.padding || 24}px`,
      background: styles.background === 'gray-100' ? '#f3f4f6' : styles.background === 'gray-50' ? '#f9fafb' : 'white',
      width: '280px',
    };

    // Border
    if (styles.border === 'subtle') {
      cardStyles.border = '1px solid #e5e7eb';
    } else if (styles.border === 'prominent') {
      cardStyles.border = '2px solid #d1d5db';
    }

    // Shadow
    const shadows: Record<string, string> = {
      none: 'none',
      sm: '0 1px 2px rgba(0,0,0,0.05)',
      md: '0 4px 6px rgba(0,0,0,0.1)',
      lg: '0 10px 15px rgba(0,0,0,0.1)',
      xl: '0 20px 25px rgba(0,0,0,0.1)',
    };
    cardStyles.boxShadow = shadows[styles.shadow as string] || 'none';

    return (
      <div style={cardStyles}>
        <h3 style={{ margin: 0, marginBottom: '8px', fontWeight: 600 }}>Card Title</h3>
        <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>
          This is a sample card with some content.
        </p>
      </div>
    );
  };

  const renderTypography = () => {
    // Check if using Claude API format
    const isClaudeFormat = styles.backgroundColor || styles.fontWeight || styles.fontSize;

    if (isClaudeFormat) {
      // Claude API format - apply styles directly
      const containerStyles: CSSProperties = {
        maxWidth: '300px',
        padding: (styles.padding as string) || '16px',
        background: (styles.backgroundColor as string) || 'transparent',
        borderRadius: getBorderRadius(styles.borderRadius),
        boxShadow: (styles.boxShadow as string) || 'none',
      };

      const headingStyles: CSSProperties = {
        fontWeight: (styles.fontWeight as number) || 700,
        fontFamily: getFontFamily(styles.fontFamily),
        fontSize: (styles.fontSize as string) || '24px',
        color: (styles.color as string) || '#1f2937',
        margin: 0,
        marginBottom: '12px',
      };

      const bodyStyles: CSSProperties = {
        fontFamily: getFontFamily(styles.fontFamily),
        fontSize: '14px',
        color: (styles.color as string) || '#374151',
        margin: 0,
        lineHeight: 1.6,
        opacity: 0.8,
      };

      return (
        <div style={containerStyles}>
          <h1 style={headingStyles}>Heading</h1>
          <p style={bodyStyles}>
            This is a paragraph of text demonstrating the typography settings for body content.
          </p>
        </div>
      );
    }

    // Fallback: Deterministic format
    const headingStyles: CSSProperties = {
      fontWeight: (styles.heading_weight as number) || 700,
      letterSpacing: `${styles.letter_spacing || 0}em`,
      fontFamily: styles.font_family === 'serif' ? 'Georgia, serif' : styles.font_family === 'mono' ? 'monospace' : 'system-ui, sans-serif',
      margin: 0,
      marginBottom: '16px',
    };

    const bodyStyles: CSSProperties = {
      lineHeight: (styles.body_line_height as number) || 1.5,
      fontFamily: styles.font_family === 'serif' ? 'Georgia, serif' : styles.font_family === 'mono' ? 'monospace' : 'system-ui, sans-serif',
      margin: 0,
      color: '#374151',
    };

    const scale = (styles.heading_size_scale as number) || 1.25;

    return (
      <div style={{ maxWidth: '300px' }}>
        <h1 style={{ ...headingStyles, fontSize: `${24 * scale}px` }}>Heading</h1>
        <p style={bodyStyles}>
          This is a paragraph of text demonstrating the typography settings for body content.
        </p>
      </div>
    );
  };

  const renderNavigation = () => {
    const items = ['Home', 'Products', 'About', 'Contact'];

    // Check if using Claude API format (has camelCase properties)
    const isClaudeFormat = styles.backgroundColor || styles.borderRadius || styles.fontWeight;

    if (isClaudeFormat) {
      // Claude API format - apply styles directly
      const navStyles: CSSProperties = {
        display: 'flex',
        flexDirection: 'row',
        gap: '4px',
        background: (styles.backgroundColor as string) || 'transparent',
        padding: (styles.padding as string) || '8px',
        borderRadius: getBorderRadius(styles.borderRadius),
        boxShadow: (styles.boxShadow as string) || 'none',
      };

      const itemStyles: CSSProperties = {
        padding: '8px 16px',
        cursor: 'pointer',
        color: (styles.color as string) || '#374151',
        textDecoration: 'none',
        fontSize: (styles.fontSize as string) || '14px',
        fontWeight: (styles.fontWeight as number | string) || 500,
        fontFamily: getFontFamily(styles.fontFamily),
        borderRadius: getBorderRadius(styles.borderRadius),
        transition: 'all 0.2s',
      };

      return (
        <nav style={navStyles}>
          {items.map((item, i) => (
            <a
              key={item}
              style={{
                ...itemStyles,
                fontWeight: i === 0 ? 700 : itemStyles.fontWeight, // Active item bold
              }}
            >
              {item}
            </a>
          ))}
        </nav>
      );
    }

    // Fallback: Deterministic format
    const isVertical = styles.style === 'vertical' || styles.style === 'sidebar';

    const navStyles: CSSProperties = {
      display: 'flex',
      flexDirection: isVertical ? 'column' : 'row',
      gap: styles.separator === 'space' ? '16px' : '0',
      background: isVertical ? '#f9fafb' : 'transparent',
      padding: isVertical ? '8px' : '0',
      borderRadius: isVertical ? '8px' : '0',
    };

    const itemStyles: CSSProperties = {
      padding: `${styles.item_padding_y || 8}px ${styles.item_padding_x || 16}px`,
      cursor: 'pointer',
      color: '#374151',
      textDecoration: 'none',
      fontSize: '14px',
    };

    const activeStyles: CSSProperties = {
      ...itemStyles,
    };

    if (styles.active_indicator === 'underline') {
      activeStyles.borderBottom = '2px solid #1a1a2e';
    } else if (styles.active_indicator === 'background') {
      activeStyles.background = '#e5e7eb';
      activeStyles.borderRadius = '4px';
    } else if (styles.active_indicator === 'border-left') {
      activeStyles.borderLeft = '3px solid #1a1a2e';
    } else if (styles.active_indicator === 'bold') {
      activeStyles.fontWeight = 700;
    }

    return (
      <nav style={navStyles}>
        {items.map((item, i) => (
          <a
            key={item}
            style={i === 0 ? activeStyles : itemStyles}
          >
            {item}
          </a>
        ))}
      </nav>
    );
  };

  const renderForm = () => {
    // Check if using Claude API format
    const isClaudeFormat = styles.backgroundColor || styles.borderRadius || styles.borderColor;

    if (isClaudeFormat) {
      // Claude API format - apply styles directly
      const formStyles: CSSProperties = {
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        padding: (styles.padding as string) || '16px',
        background: (styles.backgroundColor as string) || 'transparent',
        borderRadius: getBorderRadius(styles.borderRadius),
        boxShadow: (styles.boxShadow as string) || 'none',
      };

      const inputStyles: CSSProperties = {
        padding: '8px 12px',
        border: `${styles.borderWidth || '1px'} solid ${styles.borderColor || '#d1d5db'}`,
        borderRadius: getBorderRadius(styles.borderRadius),
        width: '150px',
        fontFamily: getFontFamily(styles.fontFamily),
        background: 'white',
      };

      const labelStyles: CSSProperties = {
        fontSize: '14px',
        fontWeight: (styles.fontWeight as number) || 500,
        color: (styles.color as string) || '#374151',
        fontFamily: getFontFamily(styles.fontFamily),
      };

      return (
        <form style={formStyles}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={labelStyles}>Name</label>
            <input style={inputStyles} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={labelStyles}>Email</label>
            <input style={inputStyles} />
          </div>
        </form>
      );
    }

    // Fallback: Deterministic format
    const isInline = styles.layout === 'inline';
    const isGrid = styles.layout === 'grid';

    const formStyles: CSSProperties = {
      display: isGrid ? 'grid' : 'flex',
      flexDirection: isInline ? 'row' : 'column',
      gap: `${styles.spacing || 16}px`,
      gridTemplateColumns: isGrid ? 'repeat(2, 1fr)' : undefined,
    };

    const fieldStyles: CSSProperties = {
      display: 'flex',
      flexDirection: styles.label_style === 'inline' ? 'row' : 'column',
      gap: '4px',
      alignItems: styles.label_style === 'inline' ? 'center' : 'stretch',
    };

    return (
      <form style={formStyles}>
        <div style={fieldStyles}>
          <label style={{ fontSize: '14px', fontWeight: 500 }}>
            Name{styles.required_indicator === 'asterisk' && <span style={{ color: 'red' }}>*</span>}
          </label>
          <input
            style={{
              padding: '8px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              width: '150px',
            }}
          />
        </div>
        <div style={fieldStyles}>
          <label style={{ fontSize: '14px', fontWeight: 500 }}>
            Email{styles.required_indicator === 'asterisk' && <span style={{ color: 'red' }}>*</span>}
          </label>
          <input
            style={{
              padding: '8px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              width: '150px',
            }}
          />
        </div>
      </form>
    );
  };

  const renderFeedback = () => {
    // Check if using Claude API format
    const isClaudeFormat = styles.backgroundColor || styles.borderRadius || styles.boxShadow;

    if (isClaudeFormat) {
      // Claude API format - apply styles directly
      const containerStyles: CSSProperties = {
        padding: (styles.padding as string) || '12px 16px',
        borderRadius: getBorderRadius(styles.borderRadius),
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        width: '250px',
        background: (styles.backgroundColor as string) || '#f0fdf4',
        color: (styles.color as string) || '#166534',
        boxShadow: (styles.boxShadow as string) || 'none',
        fontFamily: getFontFamily(styles.fontFamily),
      };

      if (styles.borderWidth && styles.borderColor) {
        containerStyles.border = `${styles.borderWidth} solid ${styles.borderColor}`;
      }

      return (
        <div style={containerStyles}>
          <span>✓</span>
          <span style={{ fontSize: (styles.fontSize as string) || '14px', fontWeight: (styles.fontWeight as number) || 400 }}>
            Changes saved successfully
          </span>
        </div>
      );
    }

    // Fallback: Deterministic format
    const isBanner = styles.type === 'banner';

    const containerStyles: CSSProperties = {
      padding: '12px 16px',
      borderRadius: isBanner ? '0' : '8px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      width: isBanner ? '300px' : '250px',
    };

    if (styles.style === 'filled') {
      containerStyles.background = '#dcfce7';
      containerStyles.color = '#166534';
    } else if (styles.style === 'bordered') {
      containerStyles.background = 'white';
      containerStyles.border = '1px solid #22c55e';
      containerStyles.color = '#166534';
    } else {
      containerStyles.background = '#f0fdf4';
      containerStyles.color = '#166534';
    }

    return (
      <div style={containerStyles}>
        {styles.icon !== 'none' && <span>✓</span>}
        <span style={{ fontSize: '14px' }}>Changes saved successfully</span>
      </div>
    );
  };

  const renderModal = () => {
    // Check if using Claude API format
    const isClaudeFormat = styles.backgroundColor || styles.borderRadius || styles.boxShadow;

    if (isClaudeFormat) {
      // Claude API format - apply styles directly
      const modalStyles: CSSProperties = {
        width: '400px',
        maxWidth: '100%',
        borderRadius: getBorderRadius(styles.borderRadius),
        background: (styles.backgroundColor as string) || 'white',
        color: (styles.color as string) || '#1f2937',
        overflow: 'hidden',
        boxShadow: (styles.boxShadow as string) || '0 20px 25px rgba(0,0,0,0.15)',
        fontFamily: getFontFamily(styles.fontFamily),
      };

      const headerStyles: CSSProperties = {
        padding: (styles.padding as string) || '16px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: `1px solid ${styles.borderColor || '#e5e7eb'}`,
      };

      return (
        <div
          style={{
            background: 'rgba(0,0,0,0.5)',
            padding: '20px',
            borderRadius: '8px',
          }}
        >
          <div style={modalStyles}>
            <div style={headerStyles}>
              <h3 style={{ margin: 0, fontWeight: (styles.fontWeight as number) || 600 }}>Modal Title</h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '18px', color: styles.color as string || '#6b7280' }}>
                ×
              </button>
            </div>
            <div style={{ padding: (styles.padding as string) || '16px' }}>
              <p style={{ margin: 0, opacity: 0.7, fontSize: (styles.fontSize as string) || '14px' }}>
                This is the modal content area.
              </p>
            </div>
          </div>
        </div>
      );
    }

    // Fallback: Deterministic format
    const sizeWidths: Record<string, string> = {
      sm: '300px',
      md: '400px',
      lg: '500px',
      xl: '600px',
      full: '90%',
    };

    const modalStyles: CSSProperties = {
      width: sizeWidths[styles.size as string] || '400px',
      maxWidth: '100%',
      borderRadius: `${styles.border_radius || 8}px`,
      background: 'white',
      overflow: 'hidden',
    };

    const overlayColors: Record<string, string> = {
      light: 'rgba(0,0,0,0.2)',
      medium: 'rgba(0,0,0,0.5)',
      dark: 'rgba(0,0,0,0.8)',
    };

    const headerStyles: CSSProperties = {
      padding: `${styles.padding || 16}px`,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
    };

    if (styles.header_style === 'border') {
      headerStyles.borderBottom = '1px solid #e5e7eb';
    } else if (styles.header_style === 'background') {
      headerStyles.background = '#f9fafb';
    }

    return (
      <div
        style={{
          background: overlayColors[styles.overlay as string] || overlayColors.medium,
          padding: '20px',
          borderRadius: '8px',
        }}
      >
        <div style={modalStyles}>
          <div style={headerStyles}>
            <h3 style={{ margin: 0, fontWeight: 600 }}>Modal Title</h3>
            {styles.close_button !== 'none' && (
              <button style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '18px' }}>
                ×
              </button>
            )}
          </div>
          <div style={{ padding: `${styles.padding || 16}px` }}>
            <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>
              This is the modal content area.
            </p>
          </div>
        </div>
      </div>
    );
  };

  // Color Palette Renderer for color_exploration phase
  const renderColorPalette = () => {
    const colors = [
      { key: 'primary', label: 'Primary', desc: 'Headers & Navigation' },
      { key: 'secondary', label: 'Secondary', desc: 'Accents & Containers' },
      { key: 'accent', label: 'Accent', desc: 'CTAs & Highlights' },
      { key: 'accentSoft', label: 'Soft Accent', desc: 'Borders & Decorations' },
      { key: 'background', label: 'Background', desc: 'Page Background' },
    ];

    const containerStyles: CSSProperties = {
      display: 'flex',
      flexDirection: 'column',
      gap: '12px',
      padding: '16px',
      background: '#f9fafb',
      borderRadius: '12px',
      width: '240px',
    };

    return (
      <div style={containerStyles}>
        {colors.map(({ key, label, desc }) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                border: '2px solid white',
                backgroundColor: (styles[key] as string) || '#cccccc',
              }}
            />
            <div>
              <div style={{ fontWeight: 600, fontSize: '14px', color: '#1f2937' }}>{label}</div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>{desc}</div>
            </div>
          </div>
        ))}
        {typeof styles.category === 'string' && styles.category && (
          <div style={{
            marginTop: '8px',
            padding: '6px 12px',
            background: '#e5e7eb',
            borderRadius: '6px',
            fontSize: '12px',
            color: '#374151',
            textAlign: 'center',
          }}>
            Style: {styles.category}
          </div>
        )}
      </div>
    );
  };

  // Font Pair Renderer for typography_exploration phase
  const renderFontPair = () => {
    const headingFont = (styles.heading as string) || 'Inter';
    const bodyFont = (styles.body as string) || 'Inter';
    const styleName = (styles.style as string) || 'modern';
    const description = (styles.description as string) || '';

    const containerStyles: CSSProperties = {
      padding: '20px',
      background: 'white',
      borderRadius: '12px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      width: '260px',
    };

    return (
      <div style={containerStyles}>
        <h2
          style={{
            fontFamily: `'${headingFont}', sans-serif`,
            fontSize: '28px',
            fontWeight: 700,
            margin: 0,
            marginBottom: '12px',
            color: '#1f2937',
            lineHeight: 1.2,
          }}
        >
          Heading Text
        </h2>
        <p
          style={{
            fontFamily: `'${bodyFont}', sans-serif`,
            fontSize: '15px',
            color: '#4b5563',
            margin: 0,
            marginBottom: '16px',
            lineHeight: 1.6,
          }}
        >
          This is body text demonstrating how your content will look with this font pairing.
        </p>
        <div
          style={{
            borderTop: '1px solid #e5e7eb',
            paddingTop: '12px',
            fontSize: '12px',
            color: '#6b7280',
          }}
        >
          <div style={{ marginBottom: '4px' }}>
            <span style={{ fontWeight: 600 }}>Heading:</span> {headingFont}
          </div>
          <div style={{ marginBottom: '4px' }}>
            <span style={{ fontWeight: 600 }}>Body:</span> {bodyFont}
          </div>
          {description && (
            <div style={{ marginTop: '8px', fontStyle: 'italic', color: '#9ca3af' }}>
              {description}
            </div>
          )}
        </div>
        {typeof styles.category === 'string' && styles.category && (
          <div
            style={{
              marginTop: '12px',
              padding: '6px 12px',
              background: '#f3f4f6',
              borderRadius: '6px',
              fontSize: '12px',
              color: '#374151',
              textAlign: 'center',
            }}
          >
            Style: {styleName}
          </div>
        )}
      </div>
    );
  };

  const renderers: Record<string, () => ReactNode> = {
    button: renderButton,
    input: renderInput,
    card: renderCard,
    typography: renderTypography,
    navigation: renderNavigation,
    form: renderForm,
    feedback: renderFeedback,
    modal: renderModal,
    color_palette: renderColorPalette,
    font_pair: renderFontPair,
  };

  const renderer = renderers[componentType];
  if (!renderer) {
    return <div>Unknown component type: {componentType}</div>;
  }

  return <>{renderer()}</>;
}
