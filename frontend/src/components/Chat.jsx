import { useState, useEffect, useRef } from "react";

const DEFAULT_BUTTONS = [
  "Hemoglobin",
  "How many parameters",
  "How many tests",
  "Download Report",
];

function Chat({ messages, setMessages }) {
  const [text, setText] = useState("");
  const [actionButtons, setActionButtons] = useState(DEFAULT_BUTTONS);
  const [isBotTyping, setIsBotTyping] = useState(false); // new state
  const bottomRef = useRef(null);

  // Scroll to bottom whenever messages change OR typing starts
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isBotTyping]);

  const addMsg = (type, messageText) => {
    setMessages((prev) => [...prev, { type, text: messageText }]);
  };

  const sendChat = async (questionOverride) => {
    const questionText = (questionOverride ?? text).trim();
    if (!questionText) return;

    // Prevent sending another request while bot is already typing
    if (isBotTyping) return;

    addMsg("user", questionText);
    setText("");
    setIsBotTyping(true); // show typing indicator

    try {
      const params = new URLSearchParams(window.location.search);
      const pid = params.get("pid");
      const rid = params.get("rid");
      const exp = params.get("exp");
      const sig = params.get("sig");

      const response = await fetch(
        `/chat?pid=${pid}&rid=${rid}&exp=${exp}&sig=${sig}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: questionText }),
        },
      );

      const data = await response.json();
      setIsBotTyping(false); // hide indicator before adding bot message
      addMsg("bot", data.answer || "No response.");

      if (Array.isArray(data.buttons) && data.buttons.length) {
        setActionButtons(data.buttons);
      } else {
        setActionButtons(DEFAULT_BUTTONS);
      }
    } catch (err) {
      setIsBotTyping(false);
      addMsg("bot", "Server connection error.");
      setActionButtons(DEFAULT_BUTTONS);
    }
  };

  const quickAsk = (buttonLabel) => {
    if (buttonLabel.toLowerCase().includes("download report")) {
      downloadReport();
      return;
    }
    sendChat(buttonLabel);
  };

  const downloadReport = () => {
    const params = new URLSearchParams(window.location.search);
    const pid = params.get("pid");
    const rid = params.get("rid");
    const exp = params.get("exp");
    const sig = params.get("sig");

    window.location.href = `/download-report?pid=${pid}&rid=${rid}&exp=${exp}&sig=${sig}`;
  };

  return (
    <div className="chat">
      <div className="chat-header">DiagnoIQ Assistant</div>

      <div className="chat-body">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.type}`}>
            {m.text}
          </div>
        ))}

        {/* Typing indicator shown while waiting for bot response */}
        {isBotTyping && (
          <div className="msg bot typing">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={bottomRef}></div>
      </div>

      <div className="actions">
        {actionButtons.map((label) => (
          <button key={label} onClick={() => quickAsk(label)}>
            {label}
          </button>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type your question..."
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendChat();
            }
          }}
          disabled={isBotTyping} // disable while bot is typing
        />
        <button onClick={() => sendChat()} disabled={isBotTyping}>
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;
