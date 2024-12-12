import { Button, Typography } from "@mui/material";
import axios from "axios";
import { useEffect, useState } from "react";
import "./App.css";
import scientistLogo from "./assets/Mad_scientist_transparent_background.svg";
import Select from "react-select";

function App() {
  const [data, setData] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [responseData, setResponseData] = useState(null);
  const [selectedBucket, setSelectedBucket] = useState(null);
  const [bucketsData, setBucketsData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Empty string when running in container
  const BASEURL = "http://192.168.1.122:5000";
  // const BASEURL = ""

  const onFileChange = (event) => {
    console.log("Selected File:", event.target.files[0]);
    setSelectedFile(event.target.files[0]);
  };

  const onBucketChange = (event) => {
    console.log("Selected Bucket:", event.value);
    setSelectedBucket(event.value);
  };

  const onFileUpload = async () => {
    if (selectedFile) {
      const formData = new FormData();
      setResponseData({ message: "Uploading..." });

      formData.append("file", selectedFile, selectedFile.name);
      formData.append("bucket", selectedBucket);

      const formValues = Object.fromEntries(formData);
      console.log("Form Data:", formValues);

      try {
        const response = await axios.post(
          BASEURL + "/api/uploadfile",
          formData
        );

        setResponseData(response.data);

        if (response.data.message) {
          console.log("Success Message:", response.data.message);
        }
        if (response.data.error) {
          console.log("Error Message:", response.data.error);
        }
      } catch (error) {
        console.error(
          "Error:",
          error.response ? error.response.error : error.message
        );
      }
    } else {
      setResponseData({ error: "Choose a file to upload first!" });
      console.log("No file selected");
    }
  };

  const onFileScanSandbox = async () => {
    if (selectedFile) {
      const formData = new FormData();
      setResponseData({ message: "Uploading and waiting for scan result..." });

      formData.append("file", selectedFile, selectedFile.name);

      try {
        const response = await axios.post(
          BASEURL + "/api/scansandbox",
          formData
        );
        setResponseData(response.data);

        if (response.data.message) {
          console.log("Success Message:", response.data.message);
        }
        if (response.data.error) {
          console.log("Error Message:", response.data.error);
        }
      } catch (error) {
        console.error(
          "Error:",
          error.response ? error.response.error : error.message
        );
      }
    } else {
      setResponseData({ error: "Choose a file to upload first!" });
      console.log("No file selected");
    }
  };

  const onFileScanFS = async () => {
    if (selectedFile) {
      const formData = new FormData();
      setResponseData({ message: "Uploading and waiting for scan result..." });

      formData.append("file", selectedFile, selectedFile.name);

      try {
        const response = await axios.post(BASEURL + "/api/scanfs", formData);
        // Parse the response
        setResponseData(response.data);

        if (response.data.message) {
          console.log("Success Message:", response.data.message);
        }
        if (response.data.error) {
          console.log("Error Message:", response.data.error);
        }
      } catch (error) {
        console.error(
          "Error:",
          error.response ? error.response.error : error.message
        );
      }
    } else {
      setResponseData({ error: "Choose a file to scan first!" });
      console.log("No file selected");
    }
  };

  const onFileScanCS = async () => {
    if (selectedFile) {
      const formData = new FormData();
      setResponseData({ message: "Uploading..." });

      formData.append("file", selectedFile, selectedFile.name);

      try {
        const response = await axios.post(BASEURL + "/api/scancs", formData);

        setResponseData(response.data);

        if (response.data.message) {
          console.log("Success Message:", response.data.message);
        }
        if (response.data.error) {
          console.log("Error Message:", response.data.error);
        }
      } catch (error) {
        console.error(
          "Error:",
          error.response ? error.response.error : error.message
        );
      }
    } else {
      setResponseData({ error: "Choose a file to save first!" });
      console.log("No file selected");
    }
  };

  const listBuckets = async () => {
    try {
      const formData = new FormData();
      const response = await axios.get(BASEURL + "/api/listbuckets", formData);

      setResponseData(response.data);
      setBucketsData(response.data.buckets);
      setIsLoading(false);

      if (response.data.message) {
        console.log("Success Message:", response.data.message);
      }
      if (response.data.error) {
        console.log("Error Message:", response.data.error);
      }
    } catch (error) {
      console.error(
        "Error:",
        error.response ? error.response.error : error.message
      );
    }
  };

  useEffect(() => {
    axios
      .get(BASEURL + "/api/data")
      .then((response) => setData(response.data))
      .catch((error) => console.error(error));
  }, []);

  useEffect(() => {
    if (bucketsData === null) {
      listBuckets();
    }
  }, [bucketsData]);

  if (isLoading) {
    return <div>Loading S3 Buckets...</div>;
  }

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
        <h1>File Cruncher</h1>
        <p>{data ? data.message : "Loading..."}</p>
      </div>
      <div>
        <Button variant="contained" component="label">
          Choose File
          <input type="file" hidden onChange={onFileChange} />
        </Button>
        {/* <Button
          variant="contained"
          color="primary"
          onClick={listBuckets}
          style={{ marginTop: 20 }}
        >
          Retrieve S3 Buckets
        </Button>
        <br></br> */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <Select
            placeholder="Choose Upload Bucket..."
            options={bucketsData}
            onChange={onBucketChange}
            styles={{
              container: (provided) => ({
                ...provided,
                width: "500px", // Set width here
              }),
              control: (provided) => ({
                ...provided,
                minWidth: "500px", // Optional: to ensure the control also respects the width
              }),
            }}
            theme={(theme) => ({
              ...theme,
              borderRadius: 0,
              colors: {
                ...theme.colors,
                //after select dropdown option
                primary50: "gray",
                //Border and Background dropdown color
                primary: "#FFFFFF",
                //Background hover dropdown color
                primary25: "gray",
                //Background color
                neutral0: "#242424",
                //Border before select
                neutral20: "#484848",
                //Hover border
                neutral30: "#1976d2",
                //No options color
                neutral40: "#242424",
                //Select color
                neutral50: "#F4FFFD",
                //arrow icon when click select
                neutral60: "#42FFDD",
                //Text color
                neutral80: "#F4FFFD",
              },
            })}
          />
        </div>
        <br></br>
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

        {responseData && responseData.message && <p>{responseData.message}</p>}
        {responseData && responseData.error && (
          <p>Error: {responseData.error}</p>
        )}
        {responseData && responseData.tags && (
          <pre>Tags: {JSON.stringify(responseData.tags, null, 2)}</pre>
        )}
      </div>
    </>
  );
}

export default App;
