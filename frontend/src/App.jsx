import React from "react";
import { Provider } from "react-redux";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { store } from "./store/store";
import LogInteractionScreen from "./pages/LogInteractionScreen";
import "./App.css";

/**
 * Main App Component
 * Sets up Redux provider and global toast notifications
 */
function App() {
  return (
    <Provider store={store}>
      <LogInteractionScreen />
      <ToastContainer
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </Provider>
  );
}

export default App;
