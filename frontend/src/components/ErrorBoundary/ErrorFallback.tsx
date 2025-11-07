/**
 * ErrorFallback 组件
 *
 * 错误边界的备用 UI，显示友好的错误信息和恢复选项
 */

import React, { ErrorInfo } from 'react';
import './ErrorFallback.css';

interface Props {
  error: Error;
  errorInfo: ErrorInfo | null;
  onReset: () => void;
}

const ErrorFallback: React.FC<Props> = ({ error, errorInfo, onReset }) => {
  const isDevelopment = process.env.NODE_ENV === 'development';

  const handleGoHome = () => {
    window.location.href = '/';
  };

  const handleReload = () => {
    window.location.reload();
  };

  return (
    <div className="error-fallback">
      <div className="error-fallback__container">
        {/* 错误图标 */}
        <div className="error-fallback__icon">
          <svg
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>

        {/* 错误标题 */}
        <h1 className="error-fallback__title">哎呀，出了点问题</h1>

        {/* 错误描述 */}
        <p className="error-fallback__description">
          {isDevelopment
            ? error.message
            : '页面遇到了一些问题，我们正在努力修复。您可以尝试刷新页面或返回首页。'}
        </p>

        {/* 操作按钮 */}
        <div className="error-fallback__actions">
          <button
            className="error-fallback__button error-fallback__button--primary"
            onClick={handleReload}
          >
            刷新页面
          </button>
          <button
            className="error-fallback__button error-fallback__button--secondary"
            onClick={handleGoHome}
          >
            返回首页
          </button>
          {isDevelopment && (
            <button
              className="error-fallback__button error-fallback__button--secondary"
              onClick={onReset}
            >
              重试
            </button>
          )}
        </div>

        {/* 开发环境显示详细错误信息 */}
        {isDevelopment && errorInfo && (
          <details className="error-fallback__details">
            <summary className="error-fallback__details-summary">
              查看技术详情
            </summary>
            <div className="error-fallback__details-content">
              <div className="error-fallback__stack">
                <h3>错误堆栈:</h3>
                <pre>{error.stack}</pre>
              </div>
              <div className="error-fallback__component-stack">
                <h3>组件堆栈:</h3>
                <pre>{errorInfo.componentStack}</pre>
              </div>
            </div>
          </details>
        )}

        {/* 帮助信息 */}
        <div className="error-fallback__help">
          <p>如果问题持续存在，请联系技术支持：</p>
          <p>
            <a href="mailto:support@genshin-wiki.com">support@genshin-wiki.com</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ErrorFallback;
