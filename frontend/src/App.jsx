import { useState } from "react";

import axios from "axios";


function App() {

  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState(null);


  // ==========================================
  // ASK CHATBOT
  // ==========================================

  const askChatbot = async () => {

    try {

      const response = await axios.get(

        `http://127.0.0.1:8000/chat/${question}`
      );

      console.log(response.data);

      setAnswer(response.data);

    }

    catch (error) {

      console.log(error);
    }
  };


  return (

    <div
      style={{
        padding: "40px",
        fontFamily: "Arial"
      }}
    >

      <h1>AI Database Chatbot</h1>


      {/* ===================================== */}
      {/* INPUT */}
      {/* ===================================== */}

      <input

        type="text"

        value={question}

        onChange={(e) =>
          setQuestion(e.target.value)
        }

        placeholder="Ask something..."

        style={{
          width: "400px",
          padding: "10px",
          fontSize: "16px"
        }}
      />


      <button

        onClick={askChatbot}

        style={{
          marginLeft: "10px",
          padding: "10px 20px",
          cursor: "pointer"
        }}
      >

        Ask

      </button>



      {/* ===================================== */}
      {/* RESULTS */}
      {/* ===================================== */}

      {
        answer &&
        answer.results &&
        answer.results.map((section, index) => (

          <div
            key={index}

            style={{
              marginTop: "40px",
              padding: "20px",
              border: "1px solid #ccc",
              borderRadius: "10px"
            }}
          >

            {/* TITLE */}

            <h2>{section.title}</h2>


            {/* ================================= */}
            {/* TABLE */}
            {/* ================================= */}

            {
              section.type === "table" &&
              section.data &&
              section.data.length > 0 && (

                <table

                  border="1"

                  cellPadding="10"

                  style={{
                    borderCollapse: "collapse",
                    width: "100%",
                    marginTop: "20px"
                  }}
                >

                  <thead>

                    <tr>

                      {

                        Object.keys(section.data[0]).map((key) => (

                          <th key={key}>

                            {key}

                          </th>
                        ))
                      }

                    </tr>

                  </thead>


                  <tbody>

                    {

                      section.data.map((row, rowIndex) => (

                        <tr key={rowIndex}>

                          {

                            Object.values(row).map((value, colIndex) => (

                              <td key={colIndex}>

                                {String(value)}

                              </td>
                            ))
                          }

                        </tr>
                      ))
                    }

                  </tbody>

                </table>
              )
            }



            {/* ================================= */}
            {/* ANALYTICS */}
            {/* ================================= */}

            {
              section.type === "analytics" &&
              section.data &&
              section.data.length > 0 && (

                <div
                  style={{
                    marginTop: "20px",
                    padding: "20px",
                    borderRadius: "10px"
                  }}
                >

                  {

                    Object.entries(section.data[0]).map(

                      ([key, value]) => (

                        <h3 key={key}>

                          {key} : {value}

                        </h3>
                      )
                    )
                  }

                </div>
              )
            }

          </div>
        ))
      }

    </div>
  );
}

export default App;