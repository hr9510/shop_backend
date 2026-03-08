"use client"
import React, { useEffect, useRef, useState } from "react";

export default function QR({ QRCodeCanvas, usersData }) {
  const length = 11;
  const specialChars = "!@#$%^&*()_+[]{}|;:',.<>?/~`=";
  const qrRef = useRef(null);
  const [url, setUrl] = useState("");
  const email = localStorage.getItem("teacherEmail")

  const userRef = useRef(usersData);
  useEffect(() => {
    userRef.current = usersData;
  }, [usersData]);

  useEffect(() => {
    const interval = setInterval(async () => {
      const { className, subject } = userRef.current;
      if (!className || !subject) return;

      // let result = "!@#$%^&*()_+[]{}|;:',.<>?/~`=";
      let result = "";
      for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * specialChars.length);
        result += specialChars[randomIndex];
      }
      result += `----${email}`
      try {
        const res = await fetch("http://localhost:5000/updateCode", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ result, className, subject , email}),
        });

        if (res.ok) {
          setUrl(result);
        }
      } catch (err) {
        console.error("Network error:", err);
      }
    }, 8000);

    // ✅ Cleanup logic on unmount
    return () => {
      console.log("Unmount detected — downloading attendance...");
      const { subject } = userRef.current;

      fetch("http://localhost:5000/getAttendence")
        .then((res) => {
          if (!res.ok) throw new Error("Failed to fetch attendance list");
          return res.json();
        })
        .then((data) => {
          if (!data || data.message === "Send some data first") {
            console.log("⚠️ No attendance records found");
            clearInterval(interval);
            return;
          }

          return fetch("http://127.0.0.1:5000/export_excel")
            .then(async (res) => {
              if (!res.ok) throw new Error("Failed to export attendance file");
              const blob = await res.blob();
              const fileName = `attendance_${subject}_${new Date()
                .toISOString()
                .split("T")[0]}.xlsx`;
              const fileUrl = window.URL.createObjectURL(blob);

              const a = document.createElement("a");
              a.href = fileUrl;
              a.download = fileName;
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(fileUrl);

              console.log("✅ File downloaded:", fileName);

              // ✅ Delete attendance after export
              return fetch("http://127.0.0.1:5000/deleteAttendence");
            })
            .then(() => console.log("🧹 Attendance records deleted"))
            .catch((err) => console.error("Download error:", err))
            .finally(() => clearInterval(interval));
        })
        .catch((err) => console.error("Error fetching attendance:", err));
    };
  }, []);

  return (
    <div>
      {url ? (
        <div className="w-[208px] mx-auto border-[2vh] border-zinc-100 rounded-2xl shadow-2xl shadow-gray-800">
          <QRCodeCanvas
            ref={qrRef}
            value={url}
            size={180}
            bgColor="white"
            fgColor="black"
            level="Q"
          />
        </div>
      ) : (
        <p className="text-xl font-semibold text-center">
          Generating QR-CODE...
        </p>
      )}
    </div>
  );
}
