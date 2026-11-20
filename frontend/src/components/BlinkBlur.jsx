import React from 'react';
import './BlinkBlur.css';

/**
 * BlinkBlur Loading Indicator
 * Compatible with `react-loading-indicators` API:
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
  // Size dimensions
  const sizeMap = {
    small: { container: 28, dot: 7, font: 12 },
    medium: { container: 42, dot: 10, font: 13 },
    large: { container: 60, dot: 15, font: 15 },
  };

  const dim = sizeMap[size] || sizeMap.medium;

  // Use theme colors if not explicitly provided
  const activeColor = color || 'var(--brand-accent, #10B981)';
  const activeTextColor = textColor || 'var(--text-muted, #94A3B8)';

  return (
    <div
      className={`blink-blur-wrapper ${className}`}
      style={{
        ...style,
      }}
      role="status"
      aria-live="polite"
    >
      <div
        className="blink-blur-dots"
        style={{
          width: dim.container,
          height: dim.container,
        }}
      >
        <span
          className="blink-blur-dot dot-1"
          style={{
            width: dim.dot,
            height: dim.dot,
            backgroundColor: activeColor,
            boxShadow: `0 0 10px ${activeColor}`,
          }}
        />
        <span
          className="blink-blur-dot dot-2"
          style={{
            width: dim.dot,
            height: dim.dot,
            backgroundColor: activeColor,
            boxShadow: `0 0 10px ${activeColor}`,
          }}
        />
        <span
          className="blink-blur-dot dot-3"
          style={{
            width: dim.dot,
            height: dim.dot,
            backgroundColor: activeColor,
            boxShadow: `0 0 10px ${activeColor}`,
          }}
        />
        <span
          className="blink-blur-dot dot-4"
          style={{
            width: dim.dot,
            height: dim.dot,
            backgroundColor: activeColor,
            boxShadow: `0 0 10px ${activeColor}`,
          }}
        />
      </div>

      {text && (
        <span
          className="blink-blur-text"
          style={{
            color: activeTextColor,
            fontSize: dim.font,
          }}
        >
          {text}
        </span>
      )}
    </div>
  );
};

export default BlinkBlur;
