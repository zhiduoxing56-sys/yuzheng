import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { App } from "./App";
import { loadRuntimeConfig } from "./config";
import { SessionProvider } from "./stores/sessionStore";
import "./styles/global.css";

async function bootstrap() {
  await loadRuntimeConfig();
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <BrowserRouter>
        <SessionProvider>
          <App />
        </SessionProvider>
      </BrowserRouter>
    </StrictMode>,
  );
}

void bootstrap();
