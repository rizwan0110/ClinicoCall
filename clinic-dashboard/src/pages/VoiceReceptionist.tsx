
import { useEffect, useRef, useState } from "react";
import VapiModule from "@vapi-ai/web";

// Handle the nested default export from the installed Vapi SDK
const VapiConstructor = (
  typeof VapiModule === "function"
    ? VapiModule
    : (VapiModule as unknown as {
        default: typeof VapiModule;
      }).default
);

type VapiClient = InstanceType<typeof VapiConstructor>;
type CallStatus = "idle" | "connecting" | "connected";

export default function VoiceReceptionist() {
  const vapiRef = useRef<VapiClient | null>(null);

  const [status, setStatus] = useState<CallStatus>("idle");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const publicKey = import.meta.env.VITE_VAPI_PUBLIC_KEY;

    if (!publicKey) {
      setError("Vapi public key is missing.");
      return;
    }

    const vapi = new VapiConstructor(publicKey);
    vapiRef.current = vapi;

    const onCallStart = () => {
      setStatus("connected");
      setError("");
    };

    const onCallEnd = () => {
      setStatus("idle");
      setIsSpeaking(false);
    };

    const onSpeechStart = () => {
      setIsSpeaking(true);
    };

    const onSpeechEnd = () => {
      setIsSpeaking(false);
    };

    const onError = (err: unknown) => {
      console.error("Vapi error:", err);
      setError("Something went wrong with the call.");
      setStatus("idle");
      setIsSpeaking(false);
    };

    vapi.on("call-start", onCallStart);
    vapi.on("call-end", onCallEnd);
    vapi.on("speech-start", onSpeechStart);
    vapi.on("speech-end", onSpeechEnd);
    vapi.on("error", onError);

    return () => {
    vapi.removeAllListeners();
    vapi.stop();
    vapiRef.current = null;
    };
  }, []);

  const startCall = async () => {
    const assistantId = import.meta.env.VITE_VAPI_ASSISTANT_ID;

    if (!assistantId || !vapiRef.current) {
      setError("Vapi configuration is missing.");
      return;
    }

    setError("");
    setStatus("connecting");

    try {
      await vapiRef.current.start(assistantId);
    } catch (err) {
      console.error("Failed to start call:", err);
      setError("Unable to start the call. Please try again.");
      setStatus("idle");
    }
  };

  const endCall = () => {
    vapiRef.current?.stop();
    setStatus("idle");
    setIsSpeaking(false);
  };

  return (
    <main className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-lg rounded-3xl bg-white p-8 shadow-lg text-center">

        <div className="mb-4 text-5xl">🎙️</div>

        <h1 className="text-3xl font-bold text-slate-900">
          ClinicoCall
        </h1>

        <p className="mt-2 text-slate-500">
          AI Voice Receptionist for KLIC Physiotherapy Clinic
        </p>

        <div className="my-10">
          <div
            className={`mx-auto flex h-36 w-36 items-center justify-center rounded-full transition-all ${
              status === "connected"
                ? "bg-green-100"
                : "bg-blue-100"
            }`}
          >
            <span className="text-5xl">
              {isSpeaking ? "🔊" : "🎤"}
            </span>
          </div>

          <p className="mt-6 text-lg font-medium text-slate-700">
            {status === "idle" && "Ready to assist you"}
            {status === "connecting" && "Connecting..."}
            {status === "connected" &&
              (isSpeaking
                ? "Assistant speaking..."
                : "Call connected")}
          </p>
        </div>

        {status === "idle" ? (
          <button
            onClick={startCall}
            className="w-full rounded-xl bg-blue-600 px-6 py-4 font-semibold text-white hover:bg-blue-700"
          >
            Start Conversation
          </button>
        ) : (
          <button
            onClick={endCall}
            className="w-full rounded-xl bg-red-600 px-6 py-4 font-semibold text-white hover:bg-red-700"
          >
            End Conversation
          </button>
        )}

        {error && (
          <p
            role="alert"
            className="mt-4 text-sm text-red-600"
          >
            {error}
          </p>
        )}

        <p className="mt-6 text-xs text-slate-400">
          Please allow microphone access when prompted.
        </p>

      </div>
    </main>
  );
}
