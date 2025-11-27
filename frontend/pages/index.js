import React, { useEffect, useState } from "react";
import ChatWindow from "../components/ChatWindow";
import { checkHealth } from "../services/api";

export default function Home() {
  const [backendStatus, setBackendStatus] = useState("checking");

  useEffect(() => {
    const checkBackend = async () => {
      try {
        await checkHealth();
        setBackendStatus("healthy");
      } catch (error) {
        console.error("Backend unreachable:", error);
        setBackendStatus("offline");
      }
    };

    checkBackend();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Status Badge */}
        {backendStatus === "offline" && (
          <div className="mb-4 p-4 bg-yellow-100 border border-yellow-400 rounded-lg text-yellow-800">
            ⚠️ Backend API is offline. Running in demo mode.
          </div>
        )}

        {/* Main Chat Container */}
        <div className="h-screen max-h-[90vh]">
          <ChatWindow />
        </div>

        {/* Footer */}
        <div className="mt-4 text-center text-gray-600 text-sm">
          <p>
            NTRIA v1.0 • Tax Reform Challenge 2025 • Built with ❤️ for Nigeria 🇳🇬
          </p>
        </div>
      </div>
    </div>
  );
}
