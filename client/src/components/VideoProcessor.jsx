import React, { useState } from "react";
import axios from "axios";
import "./styles.css";

const uploadLocalVideo = async (
  file,
  language,
  setProcessingStep,
  setOutputMessage,
  setFinalVideoPath
) => {
  try {
    setProcessingStep("Uploading and processing local video...");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("target_language", language);

    const response = await axios.post(
      "http://localhost:8000/process-video-file",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );

    setProcessingStep("Processing completed successfully.");
    setOutputMessage(response.data.message);
    setFinalVideoPath(response.data.output_video);
  } catch (error) {
    setProcessingStep("Error processing local video.");
    console.error(
      "Error during upload:",
      error.response ? error.response.data : error.message
    );
  }
};

const processVideoFromUrl = async (
  videoUrl,
  language,
  setProcessingStep,
  setOutputMessage,
  setFinalVideoPath
) => {
  try {
    setProcessingStep("Processing video from URL...");
    const response = await axios.post("http://localhost:8000/process-video", {
      input_video: videoUrl,
      target_language: language,
    });

    console.log(response.data);
    setProcessingStep("Processing completed successfully.");
    setOutputMessage(response.data.message);
    setFinalVideoPath(response.data.output_video);
  } catch (error) {
    setProcessingStep("Error processing video from URL.");
    console.error(
      "Error during URL processing:",
      error.response ? error.response.data : error.message
    );
  }
};

const VideoProcessor = () => {
  const [videoUrl, setVideoUrl] = useState("");
  const [videoFile, setVideoFile] = useState(null);
  const [language, setLanguage] = useState("hi");
  const [processingStep, setProcessingStep] = useState("");
  const [outputMessage, setOutputMessage] = useState("");
  const [finalVideoPath, setFinalVideoPath] = useState("");

  const handleProcess = () => {
    if (videoFile) {
      uploadLocalVideo(
        videoFile,
        language,
        setProcessingStep,
        setOutputMessage,
        setFinalVideoPath
      );
    } else if (videoUrl.trim() !== "") {
      processVideoFromUrl(
        videoUrl,
        language,
        setProcessingStep,
        setOutputMessage,
        setFinalVideoPath
      );
    } else {
      setProcessingStep("Please provide a video URL or upload a file.");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Video Processor</h1>
      <div>
        <label>Enter Video URL:</label>
        <input
          type="text"
          value={videoUrl}
          onChange={(e) => setVideoUrl(e.target.value)}
          placeholder="Enter URL here"
          style={{ width: "100%", marginBottom: "10px" }}
        />
      </div>
      <div>
        <label>Or Upload a Local File:</label>
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setVideoFile(e.target.files[0])}
          style={{ width: "100%", marginBottom: "10px" }}
        />
      </div>
      <div>
        <label>Select Language:</label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          style={{ width: "100%", marginBottom: "10px" }}
        >
          <option value="hi">Hindi</option>
          <option value="bn">Bengali</option>
          <option value="te">Telugu</option>
          <option value="mr">Marathi</option>
          <option value="ta">Tamil</option>
          <option value="ur">Urdu</option>
          <option value="gu">Gujarati</option>
          <option value="ml">Malayalam</option>
          <option value="kn">Kannada</option>
          <option value="or">Odia</option>
          <option value="pa">Punjabi</option>
          <option value="as">Assamese</option>
        </select>
      </div>
      <button
        onClick={handleProcess}
        style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
      >
        Start Processing
      </button>
      <div>
        <h3>Progress: {processingStep}</h3>
        <p>{outputMessage}</p>
        {finalVideoPath && (
          <p>
            <b>Final Video Path:</b> {finalVideoPath}
          </p>
        )}
      </div>
    </div>
  );
};

export default VideoProcessor;
