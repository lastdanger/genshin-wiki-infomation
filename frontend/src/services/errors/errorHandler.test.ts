/**
 * ErrorHandler 工具测试
 */

import { AxiosError } from 'axios';
import { ErrorHandler } from './errorHandler';
import { ApiError } from './ApiError';
import { ErrorCode, ErrorSeverity } from './types';

describe('ErrorHandler', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'error').mockImplementation();
    jest.spyOn(console, 'warn').mockImplementation();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('handleAxiosError', () => {
    it('should handle network error', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Network Error',
        name: 'Error',
        config: {},
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result).toBeInstanceOf(ApiError);
      expect(result.code).toBe(ErrorCode.NETWORK_ERROR);
    });

    it('should handle timeout error', () => {
      const axiosError = {
        isAxiosError: true,
        code: 'ECONNABORTED',
        message: 'timeout of 5000ms exceeded',
        name: 'Error',
        config: {},
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result).toBeInstanceOf(ApiError);
      expect(result.code).toBe(ErrorCode.TIMEOUT_ERROR);
    });

    it('should handle 400 Bad Request', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Request failed with status code 400',
        name: 'Error',
        config: {},
        response: {
          status: 400,
          data: 'Invalid request',
          statusText: 'Bad Request',
          headers: {},
          config: {},
        },
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result.code).toBe(ErrorCode.BAD_REQUEST);
    });

    it('should handle 401 Unauthorized', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Request failed with status code 401',
        name: 'Error',
        config: {},
        response: {
          status: 401,
          data: 'Unauthorized',
          statusText: 'Unauthorized',
          headers: {},
          config: {},
        },
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result.code).toBe(ErrorCode.UNAUTHORIZED);
    });

    it('should handle 403 Forbidden', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Request failed with status code 403',
        name: 'Error',
        config: {},
        response: {
          status: 403,
          data: 'Forbidden',
          statusText: 'Forbidden',
          headers: {},
          config: {},
        },
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result.code).toBe(ErrorCode.FORBIDDEN);
    });

    it('should handle 404 Not Found', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Request failed with status code 404',
        name: 'Error',
        config: {},
        response: {
          status: 404,
          data: 'Not Found',
          statusText: 'Not Found',
          headers: {},
          config: {},
        },
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result.code).toBe(ErrorCode.NOT_FOUND);
    });

    it('should handle 422 Validation Error', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Request failed with status code 422',
        name: 'Error',
        config: {},
        response: {
          status: 422,
          data: 'Validation Failed',
          statusText: 'Unprocessable Entity',
          headers: {},
          config: {},
        },
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result.code).toBe(ErrorCode.VALIDATION_ERROR);
    });

    it('should handle 429 Rate Limit', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Request failed with status code 429',
        name: 'Error',
        config: {},
        response: {
          status: 429,
          data: 'Too Many Requests',
          statusText: 'Too Many Requests',
          headers: {},
          config: {},
        },
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result.code).toBe(ErrorCode.RATE_LIMIT_EXCEEDED);
    });

    it('should handle 500 Internal Server Error', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Request failed with status code 500',
        name: 'Error',
        config: {},
        response: {
          status: 500,
          data: 'Internal Server Error',
          statusText: 'Internal Server Error',
          headers: {},
          config: {},
        },
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result.code).toBe(ErrorCode.INTERNAL_SERVER_ERROR);
    });

    it('should handle 503 Service Unavailable', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Request failed with status code 503',
        name: 'Error',
        config: {},
        response: {
          status: 503,
          data: 'Service Unavailable',
          statusText: 'Service Unavailable',
          headers: {},
          config: {},
        },
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result.code).toBe(ErrorCode.SERVICE_UNAVAILABLE);
    });

    it('should handle API error response format', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Request failed',
        name: 'Error',
        config: {},
        response: {
          status: 400,
          data: {
            success: false,
            error: {
              code: 'VALIDATION_ERROR',
              message: 'Invalid email format',
              details: [
                { field: 'email', message: 'Email is required' },
              ],
            },
          },
          statusText: 'Bad Request',
          headers: {},
          config: {},
        },
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handleAxiosError(axiosError);

      expect(result.code).toBe('VALIDATION_ERROR');
      expect(result.message).toBe('Invalid email format');
      expect(result.details).toHaveLength(1);
    });
  });

  describe('handleGeneralError', () => {
    it('should handle regular JavaScript Error', () => {
      const error = new Error('Something went wrong');

      const result = ErrorHandler.handleGeneralError(error);

      expect(result).toBeInstanceOf(ApiError);
      expect(result.message).toBe('Something went wrong');
      expect(result.code).toBe(ErrorCode.UNKNOWN_ERROR);
    });

    it('should handle error without message', () => {
      const error = new Error();

      const result = ErrorHandler.handleGeneralError(error);

      expect(result.message).toBe('发生未知错误');
    });
  });

  describe('getUserFriendlyMessage', () => {
    it('should return predefined user-friendly message for known error codes', () => {
      const error = new ApiError(
        'Error: Technical error message',
        ErrorCode.NETWORK_ERROR,
        ErrorSeverity.HIGH
      );

      const message = ErrorHandler.getUserFriendlyMessage(error);

      expect(message).toBe('网络连接失败，请检查您的网络设置');
    });

    it('should return error message if it is already user-friendly', () => {
      const error = new ApiError(
        '请稍后重试',
        ErrorCode.INTERNAL_SERVER_ERROR,
        ErrorSeverity.HIGH
      );

      const message = ErrorHandler.getUserFriendlyMessage(error);

      expect(message).toBe('请稍后重试');
    });

    it('should return default message for unknown error codes', () => {
      const error = new ApiError(
        'Error: Unknown error',
        'CUSTOM_ERROR' as ErrorCode,
        ErrorSeverity.MEDIUM
      );

      const message = ErrorHandler.getUserFriendlyMessage(error);

      expect(message).toBe('未知错误，请刷新页面重试');
    });
  });

  describe('logError', () => {
    it('should log ApiError to console', () => {
      const error = new ApiError(
        'Test error',
        ErrorCode.INTERNAL_SERVER_ERROR,
        ErrorSeverity.HIGH
      );

      ErrorHandler.logError(error, 'TestContext');

      expect(console.error).toHaveBeenCalledWith(
        expect.stringContaining('[TestContext]'),
        expect.objectContaining({
          code: ErrorCode.INTERNAL_SERVER_ERROR,
          message: 'Test error',
        })
      );
    });

    it('should log regular Error to console', () => {
      const error = new Error('Regular error');

      ErrorHandler.logError(error);

      expect(console.error).toHaveBeenCalledWith(
        expect.stringContaining('[Error]'),
        error
      );
    });
  });

  describe('reportError', () => {
    it('should report error in production', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      const error = new ApiError(
        'Production error',
        ErrorCode.INTERNAL_SERVER_ERROR,
        ErrorSeverity.HIGH
      );

      ErrorHandler.reportError(error);

      expect(console.warn).toHaveBeenCalledWith(
        'Error reporting not implemented yet'
      );

      process.env.NODE_ENV = originalEnv;
    });

    it('should not report error in development', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const error = new ApiError(
        'Dev error',
        ErrorCode.INTERNAL_SERVER_ERROR,
        ErrorSeverity.HIGH
      );

      ErrorHandler.reportError(error);

      expect(console.warn).not.toHaveBeenCalled();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('handle', () => {
    it('should handle ApiError directly', () => {
      const error = new ApiError(
        'Direct error',
        ErrorCode.VALIDATION_ERROR,
        ErrorSeverity.LOW
      );

      const result = ErrorHandler.handle(error, { logToConsole: false });

      expect(result).toBe(error);
    });

    it('should handle AxiosError', () => {
      const axiosError = {
        isAxiosError: true,
        message: 'Network Error',
        name: 'Error',
        config: {},
        toJSON: () => ({}),
      } as AxiosError;

      const result = ErrorHandler.handle(axiosError, { logToConsole: false });

      expect(result).toBeInstanceOf(ApiError);
      expect(result.code).toBe(ErrorCode.NETWORK_ERROR);
    });

    it('should handle regular Error', () => {
      const error = new Error('Regular error');

      const result = ErrorHandler.handle(error, { logToConsole: false });

      expect(result).toBeInstanceOf(ApiError);
      expect(result.code).toBe(ErrorCode.UNKNOWN_ERROR);
    });

    it('should override severity when provided in options', () => {
      const error = new ApiError(
        'Test error',
        ErrorCode.VALIDATION_ERROR,
        ErrorSeverity.LOW
      );

      const result = ErrorHandler.handle(error, {
        severity: ErrorSeverity.HIGH,
        logToConsole: false,
      });

      expect(result.severity).toBe(ErrorSeverity.HIGH);
    });

    it('should log to console by default', () => {
      const error = new Error('Test error');

      ErrorHandler.handle(error);

      expect(console.error).toHaveBeenCalled();
    });

    it('should not log to console when logToConsole is false', () => {
      const error = new Error('Test error');

      ErrorHandler.handle(error, { logToConsole: false });

      expect(console.error).not.toHaveBeenCalled();
    });

    it('should report to service when reportToService is true', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      const error = new Error('Test error');

      ErrorHandler.handle(error, {
        logToConsole: false,
        reportToService: true,
      });

      expect(console.warn).toHaveBeenCalledWith(
        'Error reporting not implemented yet'
      );

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('isRetryable', () => {
    it('should return true for network errors', () => {
      const error = new ApiError(
        'Network error',
        ErrorCode.NETWORK_ERROR,
        ErrorSeverity.HIGH
      );

      expect(ErrorHandler.isRetryable(error)).toBe(true);
    });

    it('should return true for timeout errors', () => {
      const error = new ApiError(
        'Timeout error',
        ErrorCode.TIMEOUT_ERROR,
        ErrorSeverity.MEDIUM
      );

      expect(ErrorHandler.isRetryable(error)).toBe(true);
    });

    it('should return true for service unavailable', () => {
      const error = new ApiError(
        'Service unavailable',
        ErrorCode.SERVICE_UNAVAILABLE,
        ErrorSeverity.HIGH
      );

      expect(ErrorHandler.isRetryable(error)).toBe(true);
    });

    it('should return true for internal server error', () => {
      const error = new ApiError(
        'Internal server error',
        ErrorCode.INTERNAL_SERVER_ERROR,
        ErrorSeverity.HIGH
      );

      expect(ErrorHandler.isRetryable(error)).toBe(true);
    });

    it('should return false for validation errors', () => {
      const error = new ApiError(
        'Validation error',
        ErrorCode.VALIDATION_ERROR,
        ErrorSeverity.LOW
      );

      expect(ErrorHandler.isRetryable(error)).toBe(false);
    });

    it('should return false for not found errors', () => {
      const error = new ApiError(
        'Not found',
        ErrorCode.NOT_FOUND,
        ErrorSeverity.LOW
      );

      expect(ErrorHandler.isRetryable(error)).toBe(false);
    });
  });

  describe('requiresReauthentication', () => {
    it('should return true for unauthorized errors', () => {
      const error = new ApiError(
        'Unauthorized',
        ErrorCode.UNAUTHORIZED,
        ErrorSeverity.MEDIUM
      );

      expect(ErrorHandler.requiresReauthentication(error)).toBe(true);
    });

    it('should return false for other errors', () => {
      const error = new ApiError(
        'Forbidden',
        ErrorCode.FORBIDDEN,
        ErrorSeverity.MEDIUM
      );

      expect(ErrorHandler.requiresReauthentication(error)).toBe(false);
    });
  });
});
