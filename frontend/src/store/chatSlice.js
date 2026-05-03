import { createSlice } from '@reduxjs/toolkit';

/**
 * Chat slice for managing conversation messages
 */
const chatSlice = createSlice({
    name: 'chat',
    initialState: {
        messages: [], // Array of {id, role, content, timestamp}
        loading: false,
        error: null,
    },
    reducers: {
        // Add message to chat
        addMessage: (state, action) => {
            state.messages.push({
                id: Date.now(),
                role: action.payload.role, // 'user' or 'assistant'
                content: action.payload.content,
                timestamp: new Date().toISOString(),
                ...action.payload
            });
        },

        // Clear all messages
        clearMessages: (state) => {
            state.messages = [];
        },

        // Set loading state
        setLoading: (state, action) => {
            state.loading = action.payload;
        },

        // Set error
        setError: (state, action) => {
            state.error = action.payload;
        },

        // Update message (e.g., tool result)
        updateMessage: (state, action) => {
            const { id, updates } = action.payload;
            const message = state.messages.find(m => m.id === id);
            if (message) {
                Object.assign(message, updates);
            }
        }
    }
});

export const {
    addMessage,
    clearMessages,
    setLoading,
    setError,
    updateMessage
} = chatSlice.actions;

export default chatSlice.reducer;
