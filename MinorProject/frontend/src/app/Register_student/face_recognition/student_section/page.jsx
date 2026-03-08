"use client";
import React, { useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";
import { HandleChange } from "@/component/Common";
import { useRouter } from "next/navigation";

export default function Html5QrScanner() {
  const [user, setUser] = useState({ rollno: "", name: "" });
  const [attendenceMarked, setAttendenceMarked] = useState(false);
  const [result, setResult] = useState("");
  const [data, setData] = useState({});
  const [qrVerified, setQrVerified] = useState(false);
  const [message, setMessage] = useState("");
  const qrRef = useRef(null);
  const scannerId = "html5qr-scanner";
  const [teacherEmail, setTeacherEmail] = useState("");
  const router = useRouter();

  const fetchCodeForTeacher = async (email) => {
    if (!email) return;

    try {
      const res = await fetch("http://localhost:5000/getCode");
      if (!res.ok) return;
      const json = await res.json();
      const code = json.find((c) => c.teacherEmail === email);
      if (code) setData(code);
    } catch (err) {
      console.error("Fetching error:", err);
    }
  };

  useEffect(() => {
    const interval = setInterval(async () => {
      if (teacherEmail) {
        await fetchCodeForTeacher(teacherEmail);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [teacherEmail]);

  useEffect(() => {
    const roll = localStorage.getItem("studentRoll");
    const name = localStorage.getItem("studentName");
    if (roll) setUser((prev) => ({ ...prev, rollno: roll }));
    if (name) setUser((prev) => ({ ...prev, name: name }));

    const startScanner = async () => {
      const element = document.getElementById(scannerId);
      if (!element) return;

      const html5QrCode = new Html5Qrcode(scannerId);
      const config = { fps: 10, qrbox: { width: 300, height: 300 }, aspectRatio : 3/4 };

      try {
        const devices = await Html5Qrcode.getCameras();
        if (!devices || devices.length === 0) throw new Error("No cameras found");

        const backCam = devices.find((d) => /back|rear|environment/i.test(d.label));
        const cameraId = backCam ? backCam.id : devices[0].id;

        await html5QrCode.start(
          cameraId,
          config,
          (decodedText) => {
            if (!decodedText) return;
            const txt = decodedText.toString().trim();
            setResult(txt);

            const parts = txt.split("----");
            if (parts.length >= 2) {
              const maybeTeacher = parts[1].trim();
              setTeacherEmail(maybeTeacher);
              fetchCodeForTeacher(maybeTeacher);
            }
          },
          (err) => {}
        );

        qrRef.current = html5QrCode;
      } catch (err) {
        console.error("Scanner init error:", err);
      }
    };

    const timeout = setTimeout(startScanner, 100);

    return () => {
      clearTimeout(timeout);
      if (qrRef.current) {
        qrRef.current
          .stop()
          .catch(() => {})
          .finally(() => {
            qrRef.current && qrRef.current.clear();
          });
      }
    };
  }, []);

  useEffect(() => {
    if (result && data?.code) {
      const r = result.trim();
      const c = (data.code || "").trim();
      setQrVerified(r === c);
    } else {
      setQrVerified(false);
    }
  }, [result, data]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch("http://localhost:5000/markAttendence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userData: {
            rollno: localStorage.getItem("studentRoll"),
            name: localStorage.getItem("studentName"),
          },
          subject: data.subject,
          className: data.className,
          code_id: data.id,
          teacherEmail: data.teacherEmail,
        }),
      });

      if (res.ok) {
        setAttendenceMarked(true);
        setMessage("🎉 Thank You! Attendance Marked Successfully.");
        if (qrRef.current) qrRef.current.stop().catch(() => {});
        setTimeout(() => router.push("/Register_student/face_recognition/student_section"), 2000);
      } else {
        setMessage("⚠️ Failed to mark attendance.");
      }
    } catch (err) {
      console.error(err);
      setMessage("⚠️ Server error. Try again.");
    }
  };

  return (
    <div
      style={{
        background: "#000",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        color: "#fff",
      }}
    >
      {!qrVerified ? (
        <>
          <h1 style={{ marginBottom: 20 }}>📸 Scan Your QR Code</h1>
          <div
            style={{
              position: "relative",
              width: "100vw",
              maxWidth: 400,
              height: "70vh",
              border: "2px solid rgba(255,255,255,0.7)",
              borderRadius: 12,
              overflow: "hidden",
              boxShadow: "0 0 20px rgba(255,255,255,0.3)",
            }}
          >
            <div id={scannerId} style={{ width: "100%", height: "100%" }} />
          </div>
          <div style={{ marginTop: 20, fontSize: 18 }}>
            {result && data?.code && result.trim() !== (data.code || "").trim() && (
              <p style={{ color: "red" }}>❌ Invalid QR Code</p>
            )}
            {result && data?.code && result.trim() === (data.code || "").trim() && (
              <p style={{ color: "lime" }}>✅ QR Verified!</p>
            )}
            {result && !data?.code && <p style={{ color: "orange" }}>⌛ Checking code...</p>}
          </div>
        </>
      ) : attendenceMarked ? (
        <h2 style={{ color: "lime", fontSize: 24 }}>{message}</h2>
      ) : (
        <div className="flex flex-col items-center mt-5 space-y-3">
          <h2 style={{ marginBottom: 10 }}>Fill Your Details</h2>
          <form
            onSubmit={handleSubmit}
            className="flex flex-col items-center w-full max-w-xs space-y-3"
          >
            <input
              className="w-full p-2 text-black bg-gray-200 rounded"
              name="name"
              value={user.name}
              onChange={(e) => HandleChange(e, user, setUser)}
              required
              type="text"
              placeholder="Enter your name"
            />
            <input
              className="w-full p-2 text-black bg-gray-200 rounded"
              name="rollno"
              value={user.rollno}
              onChange={(e) => HandleChange(e, user, setUser)}
              required
              type="text"
              placeholder="Enter your Roll no."
            />
            <input
              className="w-full p-2 text-black bg-gray-200 rounded"
              name="subject"
              value={data.subject || ""}
              onChange={(e) => HandleChange(e, data, setData)}
              required
              type="text"
              placeholder="Enter your Subject"
            />
            <input
              className="w-full p-2 text-black bg-gray-200 rounded"
              name="className"
              value={data.className || ""}
              onChange={(e) => HandleChange(e, data, setData)}
              required
              type="text"
              placeholder="Enter your Class"
            />
            <button
              className="w-full p-2 mt-3 text-white bg-green-500 rounded hover:bg-green-600"
              type="submit"
            >
              Mark Attendance
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
