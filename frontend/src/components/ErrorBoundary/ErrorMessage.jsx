/**
 * 错误提示组件
 *
 * 用于显示内联错误消息，支持不同的错误类型和操作按钮
 * 可用于表单验证、API 请求失败等场景
 */
import React from 'react';
import PropTypes from 'prop-types';
import './ErrorBoundary.css';

const ErrorMessage = ({
  message,
  type = 'error',
  showIcon = true,
  closable = true,
  onClose,
  onRetry,
  retryText = '重试',
  className = '',
  style = {}
}) => {
  if (!message) {
    return null;
  }

  // 根据错误类型选择图标
  const getIcon = () => {
    switch (type) {
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      case 'success':
        return '✅';
      default:
        return '❌';
    }
  };

  // 根据错误类型选择CSS类名
  const getTypeClass = () => {
    return `error-message--${type}`;
  };

  return (
    <div
      className={`error-message ${getTypeClass()} ${className}`}
      style={style}
      role="alert"
    >
      {showIcon && (
        <span className="error-message__icon" aria-hidden="true">
          {getIcon()}
        </span>
      )}

      <div className="error-message__content">
        <p className="error-message__text">{message}</p>
      </div>

      <div className="error-message__actions">
        {onRetry && (
          <button
            className="error-message__action-button error-message__retry-button"
            onClick={onRetry}
            type="button"
            aria-label={retryText}
          >
            {retryText}
          </button>
        )}

        {closable && onClose && (
          <button
            className="error-message__action-button error-message__close-button"
            onClick={onClose}
            type="button"
            aria-label="关闭"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
};

ErrorMessage.propTypes = {
  // 错误消息内容
  message: PropTypes.string,

  // 错误类型：error | warning | info | success
  type: PropTypes.oneOf(['error', 'warning', 'info', 'success']),

  // 是否显示图标
  showIcon: PropTypes.bool,

  // 是否可关闭
  closable: PropTypes.bool,

  // 关闭回调
  onClose: PropTypes.func,

  // 重试回调
  onRetry: PropTypes.func,

  // 重试按钮文本
  retryText: PropTypes.string,

  // 自定义类名
  className: PropTypes.string,

  // 自定义样式
  style: PropTypes.object
};

ErrorMessage.defaultProps = {
  type: 'error',
  showIcon: true,
  closable: true,
  retryText: '重试',
  className: '',
  style: {}
};

export default ErrorMessage;
