"use client";
import { HandleChange } from "@/component/Common";
import Footer from "@/component/Footer";
import Header from "@/component/Header";
import { useRouter } from "next/navigation";
import React, { useEffect, useRef, useState } from "react";
import { FaRegEye, FaRegEyeSlash } from "react-icons/fa6";

export default function Page() {
  const [show, setShow] = useState(false);
  const [userData, setUserData] = useState({
    name: "",
    rollno: "",
    email: "",
    password: "",
  });
  const [step, setStep] = useState("form");
  const [capturedImage, setCapturedImage] = useState(null);
  const [isCaptured, setIsCaptured] = useState(false);

  const router = useRouter();
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    if (step === "camera") {
      const enableWebcam = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ video: true });
          if (videoRef.current) videoRef.current.srcObject = stream;
          streamRef.current = stream;
        } catch (err) {
          console.error("Error accessing webcam:", err);
          alert("Please allow webcam access!");
        }
      };
      enableWebcam();
    }

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, [step]);

  const captureFace = () => {
    const video = videoRef.current;
    if (!video || video.readyState !== 4) {
      alert("Webcam not ready yet! Wait a second...");
      return null;
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    return canvas.toDataURL("image/jpeg", 0.7);
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    if (!userData.name || !userData.rollno || !userData.email || !userData.password) {
      alert("Please fill all fields!");
      return;
    }

    localStorage.setItem("studentName", userData.name);
    localStorage.setItem("studentRoll", userData.rollno);
    localStorage.setItem("studentEmail", userData.email);

    setStep("camera");
  };

  const handleCaptureAndSave = async () => {
    const imageData = captureFace();
    if (!imageData) return;

    setCapturedImage(imageData);
    setIsCaptured(true);

    try {
      const res = await fetch("http://localhost:5000/registerStudent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userData, image: imageData }),
      });

      if (res.ok) {
        alert("✅ Student Registered Successfully with Face Data!");
        setUserData({ name: "", rollno: "", email: "", password: "" });

        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
        }

        setTimeout(() => {
          router.replace("/Register_student/face_recognition");
        }, 1000);
      } else {
        alert("❌ Error saving student data!");
      }
    } catch (err) {
      console.error("Error saving student:", err);
      alert("Server Error. Please try again.");
    }
  };

  return (
    <div className="w-full min-h-screen overflow-hidden bg-gradient-to-tr from-gray-200 to-white">
      <Header />

      {step === "form" && (
        <main className="h-[450px] mx-auto flex flex-col items-center justify-center">
          <span className="font-semibold text-white bg-gray-900 w-[30vw] text-center py-[1vh] my-[2vh] rounded-4xl text-lg hover:bg-gray-700">
            STUDENT SECTION
          </span>
          <form className="space-y-2" onSubmit={handleRegister}>
            <input
              onChange={(e) => HandleChange(e, userData, setUserData)}
              name="name"
              value={userData.name}
              className="outline-none w-[30vw] border-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
              type="text"
              placeholder="Name"
              required
            />
            <br />
            <input
              onChange={(e) => HandleChange(e, userData, setUserData)}
              name="rollno"
              value={userData.rollno}
              className="outline-none w-[30vw] border-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
              type="text"
              placeholder="Roll No."
              required
            />
            <br />
            <input
              onChange={(e) => HandleChange(e, userData, setUserData)}
              name="email"
              value={userData.email}
              className="outline-none w-[30vw] border-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
              type="email"
              placeholder="Email"
              required
            />
            <br />
            <div className="relative w-[30vw]">
              <input
                onChange={(e) => HandleChange(e, userData, setUserData)}
                name="password"
                value={userData.password}
                className="outline-none w-full border-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
                type={show ? "text" : "password"}
                placeholder="Password"
                required
              />
              <span
                className="absolute text-sm text-gray-500 cursor-pointer right-4 top-3.5"
                onClick={() => setShow(!show)}
              >
                {show ? <FaRegEyeSlash size={21} /> : <FaRegEye size={19} />}
              </span>
            </div>
            <br />
            <button
              className="w-[30vw] text-center bg-blue-600 hover:bg-blue-500 font-semibold text-lg py-[1vh] text-white rounded-3xl"
              type="submit"
            >
              Next → Capture Face
            </button>
          </form>
        </main>
      )}

      {step === "camera" && (
        <div className="flex flex-col items-center justify-center my-10">
          <h2 className="mb-4 text-2xl font-bold">📸 Capture Your Face</h2>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            style={{ width: "400px", borderRadius: "10px", border: "2px solid black" }}
          />
          <br />
          <button
            onClick={handleCaptureAndSave}
            className="px-6 py-2 font-semibold text-white bg-green-600 rounded-lg hover:bg-green-500"
          >
            Capture & Save
          </button>

          {isCaptured && (
            <p className="mt-4 font-semibold text-green-700">✅ Face Captured Successfully!</p>
          )}
        </div>
      )}

      <Footer />
    </div>
  );
}
