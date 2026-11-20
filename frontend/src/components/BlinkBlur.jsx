import React from 'react';
import './BlinkBlur.css';

/**
 * BlinkBlur Loading Indicator
 * Matches react-loading-indicators exact specification:
 * 5 skewed rounded vertical bars blinking and blurring in wave sequence
 * <BlinkBlur color="" size="medium" text="" textColor="" />
 */
export const BlinkBlur = ({
  color,
  size = 'medium',
  text,
  textColor,
  className = '',
  style = {},
}) => {
  const sizeMap = {
    small: { height: 22, width: 8, gap: 4, font: 11 },
    medium: { height: 34, width: 11, gap: 5, font: 13 },
    large: { height: 48, width: 16, gap: 7, font: 15 },
  };

  const dim = sizeMap[size] || sizeMap.medium;

  // Theme-aware default colors
  const activeColor = color || 'var(--brand-primary, #10B981)';
  const activeTextColor = textColor || 'var(--text-muted, #94A3B8)';

  return (
    <div
      className={`blink-blur-container ${className}`}
      style={{
        ...style,
      }}
      role="status"
      aria-live="polite"
    >
      <div
        className="blink-blur-bars"
        style={{
          gap: `${dim.gap}px`,
          height: `${dim.height}px`,
        }}
      >
        {[0, 1, 2, 3, 4].map((i) => (
          <span
            key={i}
            className={`blink-blur-bar blink-blur-bar-${i + 1}`}
            style={{
              width: `${dim.width}px`,
              height: `${dim.height}px`,
              backgroundColor: activeColor,
              animationDelay: `${i * 0.16}s`,
            }}
          />
        ))}
      </div>

      {text && (
        <span
          className="blink-blur-label"
          style={{
            color: activeTextColor,
            fontSize: `${dim.font}px`,
          }}
        >
          {text}
        </span>
      )}
    </div>
  );
};

export default BlinkBlur;
