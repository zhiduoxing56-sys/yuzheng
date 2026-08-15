import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { App } from "./App";
import { loadRuntimeConfig } from "./config";
import { SessionProvider } from "./stores/sessionStore";
import { AuthProvider } from "./stores/authStore";
import "./styles/global.css";
import "./styles/visual-pages.css";

async function bootstrap() {
  await loadRuntimeConfig();
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <BrowserRouter>
        <AuthProvider>
          <SessionProvider><App /></SessionProvider>
        </AuthProvider>
      </BrowserRouter>
    </StrictMode>,
  );
}

void bootstrap();
