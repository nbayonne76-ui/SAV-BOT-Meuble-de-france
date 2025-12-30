import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Setup MSW server with default handlers
export const server = setupServer(...handlers);

// Helper function to reset handlers
export const resetHandlers = () => server.resetHandlers();

// Helper function to use custom handlers for specific tests
export const useHandlers = (...newHandlers) => {
  server.use(...newHandlers);
};
