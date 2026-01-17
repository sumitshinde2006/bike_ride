import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
// Note: lovable-tagger removed to prevent import issues
// It's an optional development tool and not essential for the app to run
export default defineConfig(({ mode }) => ({
  server: {
    host: "localhost",
    port: 3000,
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
