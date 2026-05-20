import { useState } from "react";
import axios from "axios";

function App() {

  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState("");


  const askChatbot = async () => {

    const response = await axios.get(

      `http://127.0.0.1:8000/chat/${question}`

    );

    setAnswer(
      JSON.stringify(response.data, null, 2)
    );
  };


  return (

    <div style={{ padding: "40px" }}>

      <h1>AI Database Chatbot</h1>


      <input

        type="text"

        value={question}

        onChange={(e) =>
          setQuestion(e.target.value)
        }

        placeholder="Ask something..."

        style={{
          width: "300px",
          padding: "10px"
        }}
      />


      <button

        onClick={askChatbot}

        style={{
          marginLeft: "10px",
          padding: "10px"
        }}
      >

        Ask

      </button>


      <pre style={{ marginTop: "20px" }}>

        {answer}

      </pre>

    </div>
  );
}

export default App;