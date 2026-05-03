import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './chatSlice';
import interactionsReducer from './interactionsSlice';

/**
 * Redux store configuration
 * Combines all reducers and configures middleware
 */
export const store = configureStore({
    reducer: {
        chat: chatReducer,
        interactions: interactionsReducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                // Ignore these action types when checking for non-serializable values
                ignoredActions: ['chat/addMessage', 'interactions/setInteractions'],
            },
        }),
});
