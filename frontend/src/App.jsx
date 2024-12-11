import { Button, Typography } from "@mui/material";
import axios from "axios";
import { useEffect, useState } from "react";
import "./App.css";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";

function App() {
  const [data, setData] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [responseData, setResponseData] = useState(null);

  // Empty string when running in container
  const BASEURL = "http://192.168.1.122:5000"
  
  useEffect(() => {
    axios
      .get(BASEURL + "/api/data")
      .then((response) => setData(response.data))
      .catch((error) => console.error(error));
  }, []);

  const onFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const onFileUpload = async () => {
    if (selectedFile) {
      const formData = new FormData();
      formData.append("file", selectedFile, selectedFile.name);

      console.log("File Name:", selectedFile.name);
      console.log("File Type:", selectedFile.type);
      console.log("File Size:", selectedFile.size, "bytes");
      try {
        const response = await axios.post(
          BASEURL + "/api/uploadfile",
          formData
        );
        // Parse the response
        setResponseData(response.data);
        console.log("Response Data:", response.data);

        if (response.data.message) {
          console.log("Success Message:", response.data.message);
        } else {
          console.log("Error Message:", response.data.error);
        }
      } catch (error) {
        console.error(
          "Error:",
          error.response ? error.response.error : error.message
        );
      }
    } else {
      console.log("No file selected");
    }
  };

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <div>
        <h1>S3 File Uploader</h1>
        <p>{data ? data.message : "Loading..."}</p>
      </div>
      <div>
        <Button variant="contained" component="label">
          Choose File
          <input type="file" hidden onChange={onFileChange} />
        </Button>
        {selectedFile && (
          <Typography variant="body1" style={{ marginTop: 10 }}>
            Selected File: {selectedFile.name}
            <br></br>
            File Size: {selectedFile.size} bytes
          </Typography>
        )}
        <br></br>
        <Button
          variant="contained"
          color="primary"
          onClick={onFileUpload}
          style={{ marginTop: 20 }}
        >
          Upload
        </Button>
        {/* {responseData && <pre>{JSON.stringify(responseData.message, null, 2)}</pre>} */}
        {responseData && <pre>{responseData.message}</pre>}
      </div>
    </>
  );
}

export default App;
