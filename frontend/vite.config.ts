import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "/AC-Virtual-Engineer/",
  server: {
    allowedHosts: [".ngrok-free.app", "tugamer89.github.io"],
  },
});
