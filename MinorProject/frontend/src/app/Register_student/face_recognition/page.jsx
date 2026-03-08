"use client";
import React, { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation"; // ✅ Import router

export default function Page() {
  const videoRef = useRef(null);
  const [message, setMessage] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [verified, setVerified] = useState(false);
  const [stream, setStream] = useState(null);
  const router = useRouter(); 

  useEffect(() => {
    const enableWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) videoRef.current.srcObject = stream;
        setStream(stream);
      } catch (err) {
        console.error("Error accessing webcam:", err);
        alert("Please allow webcam access!");
      }
    };
    enableWebcam();

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const captureFace = () => {
    const video = videoRef.current;
    if (!video || video.readyState !== 4) {
      alert("Webcam not ready yet!");
      return null;
    }
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    return canvas.toDataURL("image/jpeg", 0.7);
  };

  const handleVerify = async () => {
    const imageData = captureFace();
    if (!imageData) return;

    setIsProcessing(true);
    setMessage("Verifying face... ⏳");

    try {
      const res = await fetch("http://localhost:5000/verifyFace", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: localStorage.getItem("studentEmail"),
          image: imageData,
        }),
      });

      const data = await res.json();

      if (data.message === "Face Matched ✅") {
        setMessage("✅ Face Verified Successfully!");
        setVerified(true);

        if (stream) {
          stream.getTracks().forEach((track) => track.stop());
        }

        setTimeout(() => {
          router.push("/Register_student/face_recognition/student_section");
        }, 1500);
      } else {
        setMessage("❌ Face Not Matched! Try again.");
      }
    } catch (err) {
      console.error("Verification error:", err);
      setMessage("⚠️ Server error. Try again later.");
    } finally {
      setIsProcessing(false);
    }
  };

  // ✅ UI
  return (
    <div
      style={{
        textAlign: "center",
        marginTop: 40,
        color: "#fff",
        backgroundColor: "#000",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {!verified ? (
        <>
          <h2>🎥 Face Verification System</h2>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            style={{
              width: 400,
              borderRadius: 10,
              border: "3px solid #555",
              marginBottom: 10,
            }}
          />
          <button
            onClick={handleVerify}
            disabled={isProcessing}
            style={{
              backgroundColor: isProcessing ? "#aaa" : "#007bff",
              color: "white",
              padding: "10px 20px",
              border: "none",
              borderRadius: 5,
              cursor: "pointer",
            }}
          >
            {isProcessing ? "Processing..." : "Verify Face"}
          </button>
          <p style={{ marginTop: 20, fontSize: 18 }}>{message}</p>
        </>
      ) : (
        <div>
          <h1 style={{ color: "lime", fontSize: "28px" }}>✅ Face Verified</h1>
          <h2 style={{ marginTop: 10 }}>Redirecting... 🚀</h2>
        </div>
      )}
    </div>
  );
}
