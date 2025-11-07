/**
 * useErrorHandler Hook
 *
 * 提供统一的错误处理功能，包括错误提示、日志记录等
 */

import { useCallback, useState } from 'react';
import {
  ApiError,
  ErrorHandler,
  getUserFriendlyMessage,
  isRetryable,
  requiresReauthentication,
} from '../services/errors';

export interface UseErrorHandlerOptions {
  showToast?: boolean;
  onError?: (error: ApiError) => void;
}

export interface UseErrorHandlerReturn {
  error: ApiError | null;
  handleError: (error: Error | ApiError) => ApiError;
  clearError: () => void;
  retry: (() => Promise<void>) | null;
}

/**
 * 错误处理 Hook
 *
 * @param options - 配置选项
 * @returns 错误处理相关的状态和方法
 */
export function useErrorHandler(
  options: UseErrorHandlerOptions = {}
): UseErrorHandlerReturn {
  const [error, setError] = useState<ApiError | null>(null);
  const [retryCallback, setRetryCallback] = useState<(() => Promise<void>) | null>(null);

  /**
   * 处理错误
   */
  const handleError = useCallback(
    (err: Error | ApiError): ApiError => {
      // 转换为 ApiError
      const apiError = err instanceof ApiError
        ? err
        : ErrorHandler.handle(err, {
            logToConsole: true,
            reportToService: process.env.NODE_ENV === 'production',
          });

      // 更新错误状态
      setError(apiError);

      // 调用自定义错误处理回调
      if (options.onError) {
        options.onError(apiError);
      }

      // 如果需要显示 Toast（需要集成 Toast 组件）
      if (options.showToast !== false) {
        showErrorToast(apiError);
      }

      // 检查是否需要重新认证
      if (requiresReauthentication(apiError)) {
        handleReauthentication();
      }

      return apiError;
    },
    [options]
  );

  /**
   * 清除错误
   */
  const clearError = useCallback(() => {
    setError(null);
    setRetryCallback(null);
  }, []);

  /**
   * 设置重试回调
   */
  const setRetry = useCallback((callback: () => Promise<void>) => {
    setRetryCallback(() => callback);
  }, []);

  /**
   * 执行重试
   */
  const retry = retryCallback
    ? async () => {
        clearError();
        if (retryCallback) {
          try {
            await retryCallback();
          } catch (err) {
            handleError(err as Error);
          }
        }
      }
    : null;

  return {
    error,
    handleError,
    clearError,
    retry,
  };
}

/**
 * 显示错误 Toast（需要集成 Toast 组件）
 */
function showErrorToast(error: ApiError): void {
  const message = getUserFriendlyMessage(error);

  // 发送自定义事件，由 Toast 组件监听
  window.dispatchEvent(new CustomEvent('toast:show', {
    detail: {
      type: 'error',
      message,
      duration: 5000,
    },
  }));
}

/**
 * 处理重新认证
 */
function handleReauthentication(): void {
  // 发送自定义事件
  window.dispatchEvent(new CustomEvent('auth:required', {
    detail: { redirectTo: window.location.pathname },
  }));

  // TODO: 根据实际需求跳转到登录页
  // window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
}

/**
 * useAsyncError Hook
 *
 * 用于在异步操作中处理错误
 *
 * @example
 * const { execute, loading, error } = useAsyncError(fetchData);
 * await execute();
 */
export function useAsyncError<T extends (...args: any[]) => Promise<any>>(
  asyncFunction: T,
  options: UseErrorHandlerOptions = {}
) {
  const { handleError, error, clearError } = useErrorHandler(options);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);

  const execute = useCallback(
    async (...args: Parameters<T>): Promise<ReturnType<T> | null> => {
      setLoading(true);
      clearError();

      try {
        const result = await asyncFunction(...args);
        setData(result);
        return result;
      } catch (err) {
        handleError(err as Error);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [asyncFunction, handleError, clearError]
  );

  return {
    execute,
    loading,
    error,
    data,
    clearError,
  };
}

export default useErrorHandler;
