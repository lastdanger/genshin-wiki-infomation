/**
 * 错误降级UI组件
 *
 * 当组件发生错误时显示的友好错误页面
 */
import React from 'react';
import './ErrorBoundary.css';

const ErrorFallback = ({
  error,
  errorInfo,
  resetError,
  showDetails = false
}) => {
  const handleReload = () => {
    window.location.reload();
  };

  const handleGoHome = () => {
    window.location.href = '/';
  };

  const handleReport = () => {
    // TODO: 实现错误报告功能
    console.log('报告错误:', { error, errorInfo });
    alert('感谢您的反馈！错误已记录');
  };

  return (
    <div className="error-fallback">
      <div className="error-fallback__container">
        <div className="error-fallback__icon">
          ⚠️
        </div>

        <h1 className="error-fallback__title">
          糟糕，出现了一些问题
        </h1>

        <p className="error-fallback__message">
          我们遇到了一个意外错误。您可以尝试刷新页面或返回首页。
        </p>

        {showDetails && error && (
          <details className="error-fallback__details">
            <summary>错误详情</summary>
            <div className="error-fallback__error-info">
              <p><strong>错误消息:</strong></p>
              <pre>{error.toString()}</pre>

              {errorInfo && errorInfo.componentStack && (
                <>
                  <p><strong>组件堆栈:</strong></p>
                  <pre>{errorInfo.componentStack}</pre>
                </>
              )}
            </div>
          </details>
        )}

        <div className="error-fallback__actions">
          {resetError && (
            <button
              className="error-fallback__button error-fallback__button--primary"
              onClick={resetError}
            >
              重试
            </button>
          )}

          <button
            className="error-fallback__button error-fallback__button--secondary"
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

          <button
            className="error-fallback__button error-fallback__button--text"
            onClick={handleReport}
          >
            报告问题
          </button>
        </div>

        <div className="error-fallback__tips">
          <p className="error-fallback__tip-title">您可以尝试:</p>
          <ul className="error-fallback__tip-list">
            <li>检查网络连接是否正常</li>
            <li>清除浏览器缓存后重试</li>
            <li>使用其他浏览器访问</li>
            <li>如果问题持续，请联系技术支持</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ErrorFallback;
