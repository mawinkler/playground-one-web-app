import { Button, Typography } from "@mui/material";
import axios from "axios";
import { useEffect, useState } from "react";
import "./App.css";
// import reactLogo from "./assets/react.svg";
// import viteLogo from "/vite.svg";
import scientistLogo from "./assets/Mad_scientist_transparent_background.svg";

function App() {
  const [data, setData] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [responseData, setResponseData] = useState(null);

  // Empty string when running in container
  const BASEURL = "http://192.168.1.122:5000";
  // const BASEURL = ""

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
      setResponseData({ message: "Uploading..." });

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

  const onFileScanSandbox = async () => {
    if (selectedFile) {
      const formData = new FormData();
      setResponseData({ message: "Uploading..." });

      formData.append("file", selectedFile, selectedFile.name);

      console.log("File Name:", selectedFile.name);
      console.log("File Type:", selectedFile.type);
      console.log("File Size:", selectedFile.size, "bytes");
      try {
        const response = await axios.post(
          BASEURL + "/api/scansandbox",
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

  const onFileScanFS = async () => {
    if (selectedFile) {
      const formData = new FormData();
      setResponseData({ message: "Uploading..." });

      formData.append("file", selectedFile, selectedFile.name);

      console.log("File Name:", selectedFile.name);
      console.log("File Type:", selectedFile.type);
      console.log("File Size:", selectedFile.size, "bytes");
      try {
        const response = await axios.post(BASEURL + "/api/scanfs", formData);
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

  const onFileScanCS = async () => {
    if (selectedFile) {
      const formData = new FormData();
      setResponseData({ message: "Uploading..." });

      formData.append("file", selectedFile, selectedFile.name);

      console.log("File Name:", selectedFile.name);
      console.log("File Type:", selectedFile.type);
      console.log("File Size:", selectedFile.size, "bytes");
      try {
        const response = await axios.post(BASEURL + "/api/scancs", formData);
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
        <a
          href="https://mawinkler.github.io/playground-one-pages/"
          target="_blank"
        >
          <img src={scientistLogo} className="logo" alt="Scientific Scanner" />
        </a>
      </div>
      <div>
        <h1>File Uploader and Scanner</h1>
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
          Upload to S3
        </Button>

        <Button
          variant="contained"
          color="primary"
          onClick={onFileScanSandbox}
          style={{ marginTop: 20 }}
        >
          Sandbox
        </Button>

        <Button
          variant="contained"
          color="primary"
          onClick={onFileScanFS}
          style={{ marginTop: 20 }}
        >
          File Security
        </Button>

        <Button
          variant="contained"
          color="primary"
          onClick={onFileScanCS}
          style={{ marginTop: 20 }}
        >
          Container Security
        </Button>

        {/* {responseData && <pre>{JSON.stringify(responseData.tags, null, 2)}</pre>} */}
        {responseData && <pre>Message: {responseData.message}</pre>}
        {responseData && responseData.tags && (
          <pre>Tags: {JSON.stringify(responseData.tags, null, 2)}</pre>
        )}
      </div>
    </>
  );
}

export default App;
