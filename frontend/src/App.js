// frontend/src/App.js
// import React from 'react';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { Box, Toolbar } from "@mui/material";

// --- THIS IS THE KEY CHANGE ---
// We now import the entire AppBar from its own component file
import AppBarComponent from "./components/AppBarComponent";
import Footer from "./components/Footer";

// --- Page Imports ---
import HomePage from "./components/HomePage";
import AboutPage from "./components/AboutPage";
import EventsPage from "./components/EventsPage";
import RegistrationPage from "./components/RegistrationPage";
import ResultsPage from "./components/ResultsPage";
import GalleryPage from "./components/GalleryPage";
import Scoreboard from "./components/Scoreboard";

function App() {
  return (
    <Router>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          minHeight: "100vh",
        }}
      >
        {/* We now use the imported component here */}
        <AppBarComponent />

        {/* Spacer for the fixed AppBar */}
        <Toolbar />

        <Box
          component="main"
          sx={{
            flexGrow: 1,
          }}
        >
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/register" element={<RegistrationPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/gallery" element={<GalleryPage />} />
            <Route path="/Scoreboard" element={<Scoreboard />} />
          </Routes>
        </Box>

        <Footer />
      </Box>
    </Router>
  );
}

export default App;
