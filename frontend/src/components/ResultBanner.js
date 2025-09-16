// frontend/src/components/ResultBanner.js
// import React from 'react';
import { Box, Typography, Button } from "@mui/material";
import { Link } from "react-router-dom";
import PanToolIcon from "@mui/icons-material/PanTool";

function ResultBanner() {
  return (
    <Box
      sx={{
        backgroundColor: "#fff200",
        color: "black",
        width: "100%", // Use 100% instead of 100vw
        minHeight: { xs: "80vh", md: "55vh" },
        display: "flex",
        flexDirection: { xs: "column", md: "row" },
      }}
    >
      {/* Left Half */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
          p: 2,
        }}
      >
        <Typography sx={{ fontSize: "1.2rem" }}>Get Your Result of</Typography>
        <Typography variant="h5" sx={{ fontWeight: "bold", my: 1 }}>
          PONDICHERRY UNIVERSITY
        </Typography>
        <Typography sx={{ fontSize: "1.5rem" }}>Sahityotsav 2025</Typography>
        <Button
          component={Link}
          to="/results"
          variant="contained"
          startIcon={<PanToolIcon />}
          sx={{
            mt: 4,
            background: "linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)",
            boxShadow: "0 3px 5px 2px rgba(255, 105, 135, .3)",
            color: "white",
            fontWeight: "bold",
            py: 1.5,
            px: 4,
            borderRadius: 2,
          }}
        >
          Check Result
        </Button>
      </Box>

      {/* Right Half */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          p: 2,
        }}
      >
        <Box
          component="img"
          src="/images/theme logo1.jpg"
          alt="Chronicling The Coromandel"
          sx={{
            maxWidth: "300px",
            width: "80%",
            height: "auto",
          }}
        />
      </Box>
    </Box>
  );
}

export default ResultBanner;
