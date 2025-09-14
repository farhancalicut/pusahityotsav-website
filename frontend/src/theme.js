// frontend/src/theme.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#004d40', // Dark Teal/Green
    },
    secondary: {
      main: '#ffab00', // Vibrant Gold/Yellow
    },
    background: {
      default: '#f5f5f5', // A light grey for the page background
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif', // A clean, modern font
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 700,
    },
  },
});

export default theme;