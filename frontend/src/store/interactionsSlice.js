import { createSlice } from '@reduxjs/toolkit';

/**
 * Interactions slice for managing CRM interaction records
 */
const interactionsSlice = createSlice({
    name: 'interactions',
    initialState: {
        interactions: [], // Array of interaction records
        currentInteraction: null,
        loading: false,
        error: null,
        filter: {
            doctorName: '',
            sentiment: 'all',
            dateRange: 'all'
        }
    },
    reducers: {
        // Set interactions list
        setInteractions: (state, action) => {
            state.interactions = action.payload;
        },

        // Add new interaction
        addInteraction: (state, action) => {
            state.interactions.unshift(action.payload);
        },

        // Update interaction
        updateInteraction: (state, action) => {
            const index = state.interactions.findIndex(i => i.id === action.payload.id);
            if (index !== -1) {
                state.interactions[index] = action.payload;
            }
        },

        // Delete interaction
        deleteInteraction: (state, action) => {
            state.interactions = state.interactions.filter(i => i.id !== action.payload);
        },

        // Set current interaction for editing
        setCurrentInteraction: (state, action) => {
            state.currentInteraction = action.payload;
        },

        // Set loading state
        setLoading: (state, action) => {
            state.loading = action.payload;
        },

        // Set error
        setError: (state, action) => {
            state.error = action.payload;
        },

        // Update filter
        setFilter: (state, action) => {
            state.filter = { ...state.filter, ...action.payload };
        },

        // Clear filters
        clearFilter: (state) => {
            state.filter = {
                doctorName: '',
                sentiment: 'all',
                dateRange: 'all'
            };
        }
    }
});

export const {
    setInteractions,
    addInteraction,
    updateInteraction,
    deleteInteraction,
    setCurrentInteraction,
    setLoading,
    setError,
    setFilter,
    clearFilter
} = interactionsSlice.actions;

export default interactionsSlice.reducer;
