// frontend/src/components/HomePage.js
// import React from 'react';
import { Link } from "react-router-dom";
import { Box, Button, Typography, Container } from "@mui/material";
import PanToolIcon from "@mui/icons-material/PanTool";

// --- Import the new component ---
import Dashboard from "./Dashboard";
import ThemeNote from "./ThemeNote";
import Scoreboard from "./Scoreboard";
import ResultBanner from "./ResultBanner";
import AboutPage from "./AboutPage";

function HomePage() {
  // We're wrapping the page in a React Fragment <>...</> to hold multiple sections
  return (
    <>
      <Box
        sx={{
          minHeight: "calc(100vh - 65px)",
          backgroundColor: "#1a1a1a",
          color: "white",
          display: "flex",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <Container
          sx={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            textAlign: { xs: "center", md: "left" },
            alignItems: { xs: "center", md: "flex-start" },
            zIndex: 2,
          }}
        >
          <Typography
            variant="h5"
            sx={{
              color: "#ffffffff",
              fontFamily: "chinese rocks rg", // Apply your custom font
            }}
          >
            PONDICHERRY UNIVERSITY
          </Typography>
          <Box
            component="img"
            src="/images/sahityotsav-logo.png" // Path to your Sahityotsav image
            alt="Sahityotsav"
            sx={{
              width: { xs: "100%", sm: "100%", md: "650px" }, // Responsive width
              my: 2,
              ml: { md: -2 },
            }}
          />

          <Box sx={{ display: "flex", alignItems: "center", my: 2 }}>
            <Typography variant="h5" sx={{ fontFamily: "chinese rocks rg" }}>
              2025 SEPTEMBER&nbsp;
            </Typography>
            <Typography
              variant="h5"
              sx={{
                fontFamily: "chinese rocks rg",
                color: "#ffff00ff", // Your accent color
              }}
            >
              22-27
            </Typography>
          </Box>

          <Box sx={{ mt: 9 }}>
            <Button
              variant="contained"
              component={Link}
              to="/register"
              startIcon={<PanToolIcon />}
              sx={{
                background: "linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)",
                border: 0,
                borderRadius: 3,
                boxShadow: "0 3px 5px 2px rgba(255, 105, 135, .3)",
                color: "white",
                height: 48,
                padding: "0 30px",
                fontSize: "1rem",
              }}
            >
              Register
            </Button>
          </Box>
        </Container>

        <Box
          component="img"
          src="/images/img.png"
          alt="Building facade"
          sx={{
            position: "absolute",
            right: 0,
            bottom: 0,
            height: "90%",
            width: "auto",
            opacity: 0.8,
            display: { xs: "none", md: "block" },
          }}
        />
      </Box>

      {/* --- Add the new ThemeNote section here --- */}
      <Dashboard />
      <ThemeNote />
      <Scoreboard />
      <ResultBanner />
      <AboutPage />
    </>
  );
}

export default HomePage;
