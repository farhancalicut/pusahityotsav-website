// frontend/src/components/AppBarComponent.js
import React from "react";
import { NavLink, Link } from "react-router-dom";

import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Dialog,
  Slide,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import "./AppBar.css";

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="down" ref={ref} {...props} />;
});

function AppBarComponent() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  const [open, setOpen] = React.useState(false);
  const handleClickOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const navLinks = [
    { title: "Home", path: "/" },
    // { title: "Dashboard", path: "/dashboard" },
    { title: "About", path: "/about" },
    { title: "Gallery", path: "/gallery" },
    { title: "Scoreboard", path: "/Scoreboard" },
  ];

  return (
    // Use a React Fragment to return both the AppBar and the Dialog as siblings
    <>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          backgroundColor: "rgba(255, 255, 255, 0.8)",
          backdropFilter: "blur(90px)",
          color: "black",
          borderBottom: "1px solid #e0e0e0",
        }}
      >
        <Toolbar sx={{ justifyContent: "space-between" }}>
          {/* Logo and University Name */}
          <Box
            component={Link}
            to="/"
            sx={{
              display: "flex",
              alignItems: "center",
              textDecoration: "none",
              color: "inherit",
              overflow: "hidden", // Prevents text from wrapping awkwardly
            }}
          >
            <img
              src="/images/logo.png"
              alt="University Logo"
              style={{ height: 30, marginLeft: 16 }}
            />
          </Box>

          {isMobile ? (
            // --- Mobile View: Show only the Hamburger Icon in the AppBar ---
            <IconButton color="inherit" onClick={handleClickOpen}>
              <MenuIcon />
            </IconButton>
          ) : (
            // --- Desktop View: Show the full links ---
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              {navLinks.map((item) => (
                <Button
                  key={item.title}
                  component={NavLink}
                  to={item.path}
                  className="nav-link"
                >
                  {item.title}
                </Button>
              ))}
              <Button
                variant="contained"
                component={Link}
                to="/results"
                sx={{
                  backgroundColor: "#9d000dff",
                  borderRadius: "10px",
                  boxShadow: "none",
                  "&:hover": { backgroundColor: "#9d000df7" },
                }}
              >
                Result
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* --- Mobile Menu Dialog is now outside the AppBar for a cleaner structure --- */}
      <Dialog
        fullScreen
        open={open}
        onClose={handleClose}
        TransitionComponent={Transition}
      >
        <AppBar
          sx={{
            position: "relative",
            backgroundColor: "white",
            color: "#424242",
          }}
        >
          <Toolbar>
            <Typography
              variant="h6"
              sx={{ ml: 2, flex: 1, fontWeight: "bold" }}
            >
              Menu
            </Typography>
            <IconButton edge="end" color="inherit" onClick={handleClose}>
              <CloseIcon />
            </IconButton>
          </Toolbar>
        </AppBar>
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            px: 3,
            pt: 4,
            gap: 2, // spacing between items
          }}
        >
          {navLinks.map((item) => (
            <Button
              key={item.title}
              component={Link}
              to={item.path}
              onClick={handleClose}
              fullWidth
              sx={{
                justifyContent: "flex-start",
                borderRadius: "12px",
                backgroundColor: "#f5f5f5",
                color: "#424242",
                textTransform: "none",
                fontWeight: "bold",
                fontSize: "1.1rem",
                padding: "12px 16px",
                "&:hover": { backgroundColor: "#e0e0e0" },
              }}
            >
              <span style={{ marginRight: 8 }}>➕</span> {item.title}
            </Button>
          ))}

          {/* Get Results Button */}
          <Button
            variant="contained"
            component={Link}
            to="/results"
            onClick={handleClose}
            fullWidth
            sx={{
              mt: 3,
              borderRadius: "12px",
              background: "linear-gradient(to right, #0072ff, #00c6ff)", // gradient like your screenshot
              fontSize: "1.1rem",
              padding: "14px 0",
              fontWeight: "bold",
              color: "white",
              boxShadow: "none",
              "&:hover": {
                background: "linear-gradient(to right, #0062e6, #00aaff)",
              },
            }}
          >
            Get Results
          </Button>
        </Box>
      </Dialog>
    </>
  );
}

export default AppBarComponent;
