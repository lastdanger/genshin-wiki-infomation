/**
 * useErrorHandler Hook 测试
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useErrorHandler, useAsyncError } from './useErrorHandler';
import { ApiError, ErrorCode, ErrorSeverity } from '../services/errors/types';
import { ErrorHandler } from '../services/errors/errorHandler';

// Mock ErrorHandler
jest.mock('../services/errors/errorHandler', () => ({
  ErrorHandler: {
    handle: jest.fn(),
    logError: jest.fn(),
    reportError: jest.fn(),
  },
}));

// Mock getUserFriendlyMessage
jest.mock('../services/errors', () => ({
  ...jest.requireActual('../services/errors'),
  getUserFriendlyMessage: jest.fn((error) => error.message),
  isRetryable: jest.fn(() => true),
  requiresReauthentication: jest.fn(() => false),
}));

describe('useErrorHandler', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基本功能', () => {
    it('should initialize with null error', () => {
      const { result } = renderHook(() => useErrorHandler());

      expect(result.current.error).toBeNull();
      expect(result.current.retry).toBeNull();
    });

    it('should provide handleError, clearError, and retry functions', () => {
      const { result } = renderHook(() => useErrorHandler());

      expect(typeof result.current.handleError).toBe('function');
      expect(typeof result.current.clearError).toBe('function');
    });
  });

  describe('handleError', () => {
    it('should set error state when error is handled', () => {
      const { result } = renderHook(() => useErrorHandler());

      const testError = new ApiError({
        message: 'Test error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      act(() => {
        result.current.handleError(testError);
      });

      expect(result.current.error).toEqual(testError);
    });

    it('should convert regular Error to ApiError', () => {
      const mockApiError = new ApiError({
        message: 'Converted error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const { result } = renderHook(() => useErrorHandler());

      act(() => {
        result.current.handleError(new Error('Regular error'));
      });

      expect(ErrorHandler.handle).toHaveBeenCalled();
      expect(result.current.error).toEqual(mockApiError);
    });

    it('should call onError callback when provided', () => {
      const onError = jest.fn();
      const { result } = renderHook(() => useErrorHandler({ onError }));

      const testError = new ApiError({
        message: 'Test error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      act(() => {
        result.current.handleError(testError);
      });

      expect(onError).toHaveBeenCalledWith(testError);
    });

    it('should show toast by default', () => {
      const dispatchEventSpy = jest.spyOn(window, 'dispatchEvent');

      const { result } = renderHook(() => useErrorHandler());

      const testError = new ApiError({
        message: 'Test error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      act(() => {
        result.current.handleError(testError);
      });

      expect(dispatchEventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'toast:show',
        })
      );

      dispatchEventSpy.mockRestore();
    });

    it('should not show toast when showToast is false', () => {
      const dispatchEventSpy = jest.spyOn(window, 'dispatchEvent');

      const { result } = renderHook(() =>
        useErrorHandler({ showToast: false })
      );

      const testError = new ApiError({
        message: 'Test error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      act(() => {
        result.current.handleError(testError);
      });

      expect(dispatchEventSpy).not.toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'toast:show',
        })
      );

      dispatchEventSpy.mockRestore();
    });

    it('should trigger reauthentication when required', () => {
      const { requiresReauthentication } = require('../services/errors');
      requiresReauthentication.mockReturnValue(true);

      const dispatchEventSpy = jest.spyOn(window, 'dispatchEvent');

      const { result } = renderHook(() => useErrorHandler());

      const testError = new ApiError({
        message: 'Unauthorized',
        code: ErrorCode.UNAUTHORIZED,
        severity: ErrorSeverity.ERROR,
      });

      act(() => {
        result.current.handleError(testError);
      });

      expect(dispatchEventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'auth:required',
        })
      );

      dispatchEventSpy.mockRestore();
      requiresReauthentication.mockReturnValue(false);
    });
  });

  describe('clearError', () => {
    it('should clear error state', () => {
      const { result } = renderHook(() => useErrorHandler());

      const testError = new ApiError({
        message: 'Test error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      act(() => {
        result.current.handleError(testError);
      });

      expect(result.current.error).toEqual(testError);

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('环境配置', () => {
    it('should report error in production', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      const { result } = renderHook(() => useErrorHandler());

      act(() => {
        result.current.handleError(new Error('Production error'));
      });

      expect(ErrorHandler.handle).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          reportToService: true,
        })
      );

      process.env.NODE_ENV = originalEnv;
    });

    it('should not report error in development', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const { result } = renderHook(() => useErrorHandler());

      act(() => {
        result.current.handleError(new Error('Development error'));
      });

      expect(ErrorHandler.handle).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          reportToService: false,
        })
      );

      process.env.NODE_ENV = originalEnv;
    });
  });
});

describe('useAsyncError', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基本功能', () => {
    it('should initialize with correct default state', () => {
      const asyncFn = jest.fn().mockResolvedValue('success');
      const { result } = renderHook(() => useAsyncError(asyncFn));

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.data).toBeNull();
      expect(typeof result.current.execute).toBe('function');
      expect(typeof result.current.clearError).toBe('function');
    });
  });

  describe('execute', () => {
    it('should execute async function and set data', async () => {
      const asyncFn = jest.fn().mockResolvedValue({ id: 1, name: 'Test' });
      const { result } = renderHook(() => useAsyncError(asyncFn));

      expect(result.current.loading).toBe(false);

      let executePromise: Promise<any>;
      act(() => {
        executePromise = result.current.execute();
      });

      expect(result.current.loading).toBe(true);

      await act(async () => {
        await executePromise;
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toEqual({ id: 1, name: 'Test' });
      expect(result.current.error).toBeNull();
    });

    it('should handle errors during async execution', async () => {
      const mockApiError = new ApiError({
        message: 'Async error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const asyncFn = jest.fn().mockRejectedValue(new Error('Async error'));
      const { result } = renderHook(() => useAsyncError(asyncFn));

      let executePromise: Promise<any>;
      act(() => {
        executePromise = result.current.execute();
      });

      await act(async () => {
        await executePromise;
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toEqual(mockApiError);
      expect(result.current.data).toBeNull();
    });

    it('should pass arguments to async function', async () => {
      const asyncFn = jest.fn().mockResolvedValue('success');
      const { result } = renderHook(() => useAsyncError(asyncFn));

      await act(async () => {
        await result.current.execute(1, 'test', { key: 'value' });
      });

      expect(asyncFn).toHaveBeenCalledWith(1, 'test', { key: 'value' });
    });

    it('should clear previous error before execution', async () => {
      const mockApiError = new ApiError({
        message: 'First error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const asyncFn = jest
        .fn()
        .mockRejectedValueOnce(new Error('First error'))
        .mockResolvedValueOnce('success');

      const { result } = renderHook(() => useAsyncError(asyncFn));

      // 第一次执行失败
      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.error).toEqual(mockApiError);

      // 第二次执行成功，应该清除之前的错误
      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.error).toBeNull();
      expect(result.current.data).toBe('success');
    });

    it('should return null when error occurs', async () => {
      const mockApiError = new ApiError({
        message: 'Error occurred',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const asyncFn = jest.fn().mockRejectedValue(new Error('Error occurred'));
      const { result } = renderHook(() => useAsyncError(asyncFn));

      let returnValue: any;
      await act(async () => {
        returnValue = await result.current.execute();
      });

      expect(returnValue).toBeNull();
    });
  });

  describe('loading state', () => {
    it('should set loading to true during execution', async () => {
      const asyncFn = jest.fn(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      const { result } = renderHook(() => useAsyncError(asyncFn));

      act(() => {
        result.current.execute();
      });

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });

    it('should set loading to false after success', async () => {
      const asyncFn = jest.fn().mockResolvedValue('success');
      const { result } = renderHook(() => useAsyncError(asyncFn));

      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.loading).toBe(false);
    });

    it('should set loading to false after error', async () => {
      const mockApiError = new ApiError({
        message: 'Error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const asyncFn = jest.fn().mockRejectedValue(new Error('Error'));
      const { result } = renderHook(() => useAsyncError(asyncFn));

      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.loading).toBe(false);
    });
  });

  describe('clearError', () => {
    it('should clear error state', async () => {
      const mockApiError = new ApiError({
        message: 'Error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const asyncFn = jest.fn().mockRejectedValue(new Error('Error'));
      const { result } = renderHook(() => useAsyncError(asyncFn));

      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.error).toEqual(mockApiError);

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('选项配置', () => {
    it('should respect showToast option', async () => {
      const dispatchEventSpy = jest.spyOn(window, 'dispatchEvent');

      const asyncFn = jest.fn().mockResolvedValue('success');
      const { result } = renderHook(() =>
        useAsyncError(asyncFn, { showToast: false })
      );

      await act(async () => {
        await result.current.execute();
      });

      expect(dispatchEventSpy).not.toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'toast:show',
        })
      );

      dispatchEventSpy.mockRestore();
    });

    it('should call onError callback', async () => {
      const onError = jest.fn();

      const mockApiError = new ApiError({
        message: 'Error',
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        severity: ErrorSeverity.ERROR,
      });

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const asyncFn = jest.fn().mockRejectedValue(new Error('Error'));
      const { result } = renderHook(() => useAsyncError(asyncFn, { onError }));

      await act(async () => {
        await result.current.execute();
      });

      expect(onError).toHaveBeenCalledWith(mockApiError);
    });
  });
});
