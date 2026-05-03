/**
 * Redux Thunk middleware setup for async actions
 */
export const asyncActionCreator = (asyncFunction) => {
    return asyncFunction;
};

/**
 * Custom middleware to handle API calls
 */
export const apiMiddleware = store => next => action => {
    if (action.type === 'api/request') {
        // Handle async API calls
        return action.payload;
    }
    return next(action);
};
