// frontend/src/index.js
import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// --- Add these imports ---
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import theme from "./theme"; // Import our custom theme

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    {/* Wrap the App in the ThemeProvider */}
    <ThemeProvider theme={theme}>
      {/* CssBaseline resets browser default styles for consistency */}
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>,
);
