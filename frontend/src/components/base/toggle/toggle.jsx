import React from 'react';
import './toggle.css';

export const Toggle = ({
  checked = false,
  onChange,
  size = 'sm',
  disabled = false,
  ariaLabel = 'Toggle theme',
  className = '',
  leftIcon,
  rightIcon,
}) => {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={ariaLabel}
      disabled={disabled}
      className={`ui-toggle ui-toggle--${size} ${checked ? 'ui-toggle--checked' : ''} ${className}`}
      onClick={() => onChange && onChange(!checked)}
    >
      {leftIcon && <span className="ui-toggle-icon ui-toggle-icon--left">{leftIcon}</span>}
      <span className="ui-toggle-thumb" />
      {rightIcon && <span className="ui-toggle-icon ui-toggle-icon--right">{rightIcon}</span>}
    </button>
  );
};

export default Toggle;
