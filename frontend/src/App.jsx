import { useState, useEffect } from "react";
import Summary from "./components/Summary";
import Chat from "./components/Chat";

function App() {
  useEffect(() => {
    const handlePop = () => {
      setOpenChat(false);
    };

    window.addEventListener("popstate", handlePop);

    return () => {
      window.removeEventListener("popstate", handlePop);
    };
  }, []);

  const [openChat, setOpenChat] = useState(false);
  const [messages, setMessages] = useState([
    {
      type: "system",
      text: "⚠️ This is for informational purposes only. Always consult a doctor for medical advice.",
    },
    {
      type: "bot",
      text: "Hello 👋 I can explain your report results. What would you like to know?",
    },
  ]);

  return (
    <>
      {!openChat && <Summary />}

      {!openChat && (
        <div className="bottom-nav">
          <a href="tel:+911234567890" className="nav-btn btn-secondary">
            📞 Call Lab
          </a>
          <button
            className="nav-btn btn-primary"
            onClick={() => {
              setOpenChat(true);
              window.history.pushState({ chatOpen: true }, "");
            }}
          >
            View Summary
          </button>
        </div>
      )}

      {openChat && <Chat messages={messages} setMessages={setMessages} />}
    </>
  );
}

export default App;
