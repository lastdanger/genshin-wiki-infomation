/**
 * 重试按钮组件
 *
 * 支持加载状态、倒计时、禁用状态等
 * 可用于错误恢复、网络请求重试等场景
 */
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './ErrorBoundary.css';

const RetryButton = ({
  onClick,
  loading = false,
  disabled = false,
  countdown = 0,
  text = '重试',
  loadingText = '重试中...',
  className = '',
  style = {},
  size = 'medium',
  variant = 'primary'
}) => {
  const [remainingTime, setRemainingTime] = useState(countdown);

  useEffect(() => {
    if (countdown > 0) {
      setRemainingTime(countdown);
    }
  }, [countdown]);

  useEffect(() => {
    if (remainingTime > 0) {
      const timer = setTimeout(() => {
        setRemainingTime(prev => prev - 1);
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [remainingTime]);

  const handleClick = () => {
    if (!loading && !disabled && remainingTime === 0) {
      onClick();
    }
  };

  const isDisabled = disabled || loading || remainingTime > 0;

  const getSizeClass = () => {
    switch (size) {
      case 'small':
        return 'retry-button--small';
      case 'large':
        return 'retry-button--large';
      default:
        return '';
    }
  };

  const getVariantClass = () => {
    switch (variant) {
      case 'secondary':
        return 'retry-button--secondary';
      case 'outline':
        return 'retry-button--outline';
      default:
        return 'retry-button--primary';
    }
  };

  const getButtonText = () => {
    if (loading) {
      return loadingText;
    }
    if (remainingTime > 0) {
      return `${text} (${remainingTime}s)`;
    }
    return text;
  };

  return (
    <button
      className={`retry-button ${getSizeClass()} ${getVariantClass()} ${
        loading ? 'retry-button--loading' : ''
      } ${className}`}
      onClick={handleClick}
      disabled={isDisabled}
      style={style}
      type="button"
      aria-label={getButtonText()}
    >
      {loading && (
        <span className="retry-button__icon" aria-hidden="true">
          ⟳
        </span>
      )}
      <span className="retry-button__text">{getButtonText()}</span>
    </button>
  );
};

RetryButton.propTypes = {
  // 点击回调
  onClick: PropTypes.func.isRequired,

  // 是否加载中
  loading: PropTypes.bool,

  // 是否禁用
  disabled: PropTypes.bool,

  // 倒计时（秒）
  countdown: PropTypes.number,

  // 按钮文本
  text: PropTypes.string,

  // 加载中文本
  loadingText: PropTypes.string,

  // 自定义类名
  className: PropTypes.string,

  // 自定义样式
  style: PropTypes.object,

  // 按钮大小：small | medium | large
  size: PropTypes.oneOf(['small', 'medium', 'large']),

  // 按钮样式变体：primary | secondary | outline
  variant: PropTypes.oneOf(['primary', 'secondary', 'outline'])
};

RetryButton.defaultProps = {
  loading: false,
  disabled: false,
  countdown: 0,
  text: '重试',
  loadingText: '重试中...',
  className: '',
  style: {},
  size: 'medium',
  variant: 'primary'
};

export default RetryButton;
