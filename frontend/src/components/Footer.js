// frontend/src/components/Footer.js
// import React from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Link,
  IconButton,
} from "@mui/material";

// Import Social Media Icons
import InstagramIcon from "@mui/icons-material/Instagram";
import FacebookIcon from "@mui/icons-material/Facebook";
// import YouTubeIcon from '@mui/icons-material/YouTube';
// import XIcon from '@mui/icons-material/X';
import WhatsAppIcon from "@mui/icons-material/WhatsApp";

function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: "#424242",
        color: "white",
        py: 4,
        mt: "auto",
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ textAlign: "left" }}>
          {/* Row 1: Contact Us Title */}
          <Typography variant="h6" gutterBottom sx={{ fontWeight: "bold" }}>
            Contact Us
          </Typography>
          
          {/* Row 2: University Name */}
          <Typography variant="body2" sx={{ color: "#bdbdbd", mb: 1 }}>
            SSF Pondicherry University, Kalapet
          </Typography>
          
          {/* Row 3: Email Links */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ color: "#bdbdbd", fontSize: "0.65rem" }}>
              Email: <Link href="mailto:ssfpondicherryuniversity@gmail.com" sx={{ color: "#bdbdbd", textDecoration: "none" }}>ssfpondicherryuniversity@gmail.com</Link>
            </Typography>
            <Typography variant="body2" sx={{ color: "#bdbdbd", fontSize: "0.65rem" }}>
              DevId: <Link href="mailto:muhammedfarhant6@gmail.com" sx={{ color: "#bdbdbd", textDecoration: "none" }}>muhammedfarhant6@gmail.com</Link>
            </Typography>
          </Box>
          
          {/* Row 4: Social Media Icons */}
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
            <IconButton
              href="https://www.instagram.com/ssfpondicherryuniversity?utm_source=ig_web_button_share_sheet&igsh=MXZ3dHBpZjI3NHZnZQ=="
              target="_blank"
              sx={{ color: "white" }}
            >
              <InstagramIcon />
            </IconButton>
            <IconButton
              href="https://www.facebook.com/SSFPondicherryUniversity"
              target="_blank"
              sx={{ color: "white" }}
            >
              <FacebookIcon />
            </IconButton>
            <IconButton
              href="https://chat.whatsapp.com/CLtEVLigf2fJwZJM0Z5B9v?mode=ems_copy_c"
              target="_blank"
              sx={{ color: "white" }}
            >
              <WhatsAppIcon />
            </IconButton>
          </Box>
          
          {/* Row 5: Copyright */}
          <Typography variant="body2" sx={{ color: "#bdbdbd" }}>
            © 2025 SSF PU
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export default Footer;
