/**
 * Axios 拦截器测试
 */

import { AxiosRequestConfig, AxiosResponse } from 'axios';
import interceptors from './interceptors';
import { ErrorHandler } from '../errors/errorHandler';
import { ApiError } from '../errors/ApiError';
import { ErrorCode, ErrorSeverity } from '../errors/types';

// Mock ErrorHandler
jest.mock('../errors/errorHandler', () => ({
  ErrorHandler: {
    handle: jest.fn(),
  },
}));

describe('Axios Interceptors', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Mock localStorage
    Storage.prototype.getItem = jest.fn();
    Storage.prototype.setItem = jest.fn();
    Storage.prototype.removeItem = jest.fn();

    // Mock console
    jest.spyOn(console, 'log').mockImplementation();
    jest.spyOn(console, 'error').mockImplementation();

    // Mock window.dispatchEvent
    jest.spyOn(window, 'dispatchEvent').mockImplementation();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('requestInterceptor', () => {
    it('should add X-Request-ID header to request', () => {
      const config: AxiosRequestConfig = {
        headers: {},
      };

      const result = interceptors.requestInterceptor(config);

      expect(result.headers?.['X-Request-ID']).toMatch(/^req-\d+-[a-z0-9]+$/);
    });

    it('should add X-Request-Time header to request', () => {
      const config: AxiosRequestConfig = {
        headers: {},
      };

      const result = interceptors.requestInterceptor(config);

      expect(result.headers?.['X-Request-Time']).toBeTruthy();
      expect(new Date(result.headers?.['X-Request-Time']).getTime()).toBeLessThanOrEqual(
        Date.now()
      );
    });

    it('should add Authorization header when token exists', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('test-token');

      const config: AxiosRequestConfig = {
        headers: {},
      };

      const result = interceptors.requestInterceptor(config);

      expect(result.headers?.['Authorization']).toBe('Bearer test-token');
    });

    it('should not add Authorization header when token does not exist', () => {
      (localStorage.getItem as jest.Mock).mockReturnValue(null);

      const config: AxiosRequestConfig = {
        headers: {},
      };

      const result = interceptors.requestInterceptor(config);

      expect(result.headers?.['Authorization']).toBeUndefined();
    });

    it('should log request in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const config: AxiosRequestConfig = {
        method: 'GET',
        url: '/test',
        headers: {},
        params: { id: 1 },
        data: { name: 'test' },
      };

      interceptors.requestInterceptor(config);

      expect(console.log).toHaveBeenCalledWith(
        '[API Request]',
        expect.objectContaining({
          method: 'GET',
          url: '/test',
        })
      );

      process.env.NODE_ENV = originalEnv;
    });

    it('should not log request in production mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      const config: AxiosRequestConfig = {
        method: 'GET',
        url: '/test',
        headers: {},
      };

      interceptors.requestInterceptor(config);

      expect(console.log).not.toHaveBeenCalled();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('responseSuccessInterceptor', () => {
    it('should return response for successful requests', () => {
      const response: AxiosResponse = {
        data: { success: true, data: { id: 1 } },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {},
      };

      const result = interceptors.responseSuccessInterceptor(response);

      expect(result).toEqual(response);
    });

    it('should log response in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const response: AxiosResponse = {
        data: { success: true, data: {} },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: { method: 'GET', url: '/test' },
      };

      interceptors.responseSuccessInterceptor(response);

      expect(console.log).toHaveBeenCalledWith(
        '[API Response]',
        expect.objectContaining({
          method: 'GET',
          status: 200,
          success: true,
        })
      );

      process.env.NODE_ENV = originalEnv;
    });

    it('should reject when success is false', async () => {
      const mockApiError = new ApiError(
        'Error from backend',
        ErrorCode.INTERNAL_SERVER_ERROR,
        ErrorSeverity.HIGH
      );

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const response: AxiosResponse = {
        data: {
          success: false,
          error: { message: 'Error from backend' },
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {},
      };

      await expect(
        interceptors.responseSuccessInterceptor(response)
      ).rejects.toEqual(mockApiError);
    });

    it('should not reject when response does not have success field', () => {
      const response: AxiosResponse = {
        data: { items: [1, 2, 3] },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {},
      };

      const result = interceptors.responseSuccessInterceptor(response);

      expect(result).toEqual(response);
    });
  });

  describe('responseErrorInterceptor', () => {
    it('should handle errors and call ErrorHandler', async () => {
      const mockApiError = new ApiError(
        'Network Error',
        ErrorCode.NETWORK_ERROR,
        ErrorSeverity.HIGH
      );

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const error: any = {
        isAxiosError: true,
        message: 'Network Error',
        config: {},
      };

      await expect(
        interceptors.responseErrorInterceptor(error)
      ).rejects.toEqual(mockApiError);

      expect(ErrorHandler.handle).toHaveBeenCalledWith(
        error,
        expect.objectContaining({
          logToConsole: true,
        })
      );
    });

    it('should handle 401 errors and trigger auth logout', async () => {
      const mockApiError = new ApiError(
        'Unauthorized',
        ErrorCode.UNAUTHORIZED,
        ErrorSeverity.MEDIUM
      );

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const error: any = {
        isAxiosError: true,
        message: 'Request failed with status code 401',
        config: {},
        response: {
          status: 401,
          data: 'Unauthorized',
          statusText: 'Unauthorized',
          headers: {},
          config: {},
        },
      };

      await expect(
        interceptors.responseErrorInterceptor(error)
      ).rejects.toBeDefined();

      // 应该清除本地存储的 token
      expect(localStorage.removeItem).toHaveBeenCalledWith('authToken');
      expect(localStorage.removeItem).toHaveBeenCalledWith('userInfo');

      // 应该触发 auth:logout 事件
      expect(window.dispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'auth:logout',
        })
      );
    });

    it('should handle 403 errors and trigger permission error event', async () => {
      const mockApiError = new ApiError(
        'Forbidden',
        ErrorCode.FORBIDDEN,
        ErrorSeverity.MEDIUM
      );

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const error: any = {
        isAxiosError: true,
        message: 'Request failed with status code 403',
        config: {},
        response: {
          status: 403,
          data: 'Forbidden',
          statusText: 'Forbidden',
          headers: {},
          config: {},
        },
      };

      await expect(
        interceptors.responseErrorInterceptor(error)
      ).rejects.toBeDefined();

      // 应该触发 error:permission 事件
      expect(window.dispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'error:permission',
        })
      );
    });

    it('should handle 429 rate limit errors', async () => {
      const mockApiError = new ApiError(
        'Rate Limit Exceeded',
        ErrorCode.RATE_LIMIT_EXCEEDED,
        ErrorSeverity.MEDIUM
      );

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const error: any = {
        isAxiosError: true,
        message: 'Request failed with status code 429',
        config: {},
        response: {
          status: 429,
          data: 'Too Many Requests',
          statusText: 'Too Many Requests',
          headers: {},
          config: {},
        },
      };

      await expect(
        interceptors.responseErrorInterceptor(error)
      ).rejects.toBeDefined();

      // 应该触发 error:rateLimit 事件
      expect(window.dispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'error:rateLimit',
        })
      );
    });

    it('should log errors in development mode', async () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const mockApiError = new ApiError(
        'Test Error',
        ErrorCode.INTERNAL_SERVER_ERROR,
        ErrorSeverity.HIGH
      );

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const error: any = {
        isAxiosError: true,
        message: 'Request failed with status code 500',
        config: { method: 'GET', url: '/test' },
        response: {
          status: 500,
          data: 'Internal Server Error',
          statusText: 'Internal Server Error',
          headers: {},
          config: {},
        },
      };

      await expect(
        interceptors.responseErrorInterceptor(error)
      ).rejects.toBeDefined();

      expect(console.error).toHaveBeenCalledWith(
        '[API Error]',
        expect.objectContaining({
          method: 'GET',
          status: 500,
        })
      );

      process.env.NODE_ENV = originalEnv;
    });

    it('should report errors in production mode', async () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      const mockApiError = new ApiError(
        'Production Error',
        ErrorCode.INTERNAL_SERVER_ERROR,
        ErrorSeverity.HIGH
      );

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const error: any = {
        isAxiosError: true,
        message: 'Request failed with status code 500',
        config: {},
        response: {
          status: 500,
          data: 'Internal Server Error',
          statusText: 'Internal Server Error',
          headers: {},
          config: {},
        },
      };

      await expect(
        interceptors.responseErrorInterceptor(error)
      ).rejects.toBeDefined();

      expect(ErrorHandler.handle).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          reportToService: true,
        })
      );

      process.env.NODE_ENV = originalEnv;
    });

    it('should handle errors without response', async () => {
      const mockApiError = new ApiError(
        'Network Error',
        ErrorCode.NETWORK_ERROR,
        ErrorSeverity.HIGH
      );

      (ErrorHandler.handle as jest.Mock).mockReturnValue(mockApiError);

      const error: any = {
        isAxiosError: true,
        message: 'Network Error',
        config: {},
      };

      await expect(
        interceptors.responseErrorInterceptor(error)
      ).rejects.toEqual(mockApiError);
    });
  });
});
