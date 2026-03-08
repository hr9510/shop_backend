"use client";
import Footer from "@/component/Footer";
import Header from "@/component/Header";
import React, { useState } from "react";
import { FaRegEye, FaRegEyeSlash } from "react-icons/fa6";
import { useRouter } from "next/navigation";
import { HandleChange } from "@/component/Common";

export default function Page() {
  const [show, setShow] = useState(false);
  const [userData, setUserData] = useState({ name: "", email: "", password: "" });
  const router = useRouter();

  const submitted = (e) => {
    e.preventDefault();
    fetch("http://localhost:5000/registerTeacher", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body : JSON.stringify(userData)
    })
    localStorage.setItem("teacherEmail", userData.email)
    setUserData({name : "", email : "", password : ""})
    alert("Teacher Registered Successfully ✅");
    router.push("/Register_teacher/teacher_section");
  };
  

  return (
    <div className="w-full min-h-screen overflow-hidden bg-gradient-to-tr from-gray-200 to-white">
      <Header />

      <main className="h-[450px] mx-auto flex flex-col items-center justify-center">
        <span className="font-semibold text-white bg-gray-900 w-[30vw] text-center py-[1vh] my-[2vh] rounded-4xl text-lg hover:bg-gray-700">
          TEACHER SECTION
        </span>

        <form className="space-y-2" onSubmit={submitted}>
          <input
            onChange={(e)=>{HandleChange(e, userData, setUserData)}}
            name="name"
            value={userData.name}
            className="outline-none w-[30vw] border-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
            type="text"
            placeholder="Name"
            required
          />
          <br />
          <input
            onChange={(e)=>{HandleChange(e, userData, setUserData)}}
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
              onChange={(e)=>{HandleChange(e, userData, setUserData)}}
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
            Register
          </button>
        </form>
      </main>

      <Footer />
    </div>
  );
}
