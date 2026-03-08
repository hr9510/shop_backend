"use client"
import { HandleChange } from '@/component/Common'
import Footer from '@/component/Footer'
import Header from '@/component/Header'
import { useRouter } from 'next/navigation'
import React, { useState } from 'react'

export default function Page() {
  let email = localStorage.getItem("teacherEmail")
  let router = useRouter()
  let [schedule, setSchedule] = useState({
    email: email,
    className : "",
    day: "",
    subject: "",
    start_time: "",
    end_time: ""
  });

  let handleSubmit = (e) => {
    e.preventDefault()
    fetch("http://localhost:5000/Creating_schedule", {
      method: "POST",
      headers: { "Content-type": "application/json" },
      body: JSON.stringify(schedule)
    })
    alert("schedule added successfully")
    setSchedule({
      day: "",
      className : "",
    subject: "",
    start_time: "",
    end_time: ""
    })
    router.push("/Register_teacher/teacher_section")
  }

  return (
    <div>
      <Header />
      <form onSubmit={handleSubmit} className="flex flex-col items-center my-[15vh] space-y-4">
        <input
          required
          className="outline-none w-[30vw] border-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
          name="subject"
          value={schedule.subject}
          onChange={(e) => HandleChange(e, schedule, setSchedule)}
          type="text"
          placeholder="Enter subject"
        />
        <input
          required
          className="outline-none w-[30vw] border-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
          name="className"
          value={schedule.className}
          onChange={(e) => HandleChange(e, schedule, setSchedule)}
          type="text"
          placeholder="Enter class"
        />
        <input
          required
          className="outline-none w-[30vw] border-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
          name="day"
          value={schedule.day}
          onChange={(e) => HandleChange(e, schedule, setSchedule)}
          type="text"
          placeholder="Enter day"
        />

        <div className='relative'>
          <span className='absolute bg-white left-6 bottom-7'>Enter starting time</span>
        <input
          required
          className="outline-none w-[30vw] border-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
          name="start_time"
          value={schedule.start_time}
          onChange={(e) => HandleChange(e, schedule, setSchedule)}
          type="time"
        />
        </div>
        <div className='relative'>
          <span className='absolute bg-white left-6 bottom-7'>Enter ending time</span>
        <input
          required
          className="outline-none w-[30vw] border-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
          name="end_time"
          value={schedule.end_time}
          onChange={(e) => HandleChange(e, schedule, setSchedule)}
          type="time"
        />
        </div>
        

        <button
          className="w-[30vw] border-black text-white text-xl font-semibold bg-black border-[2px] px-[1vw] py-[1vh] rounded-3xl"
          type="submit"
        >
          Submit
        </button>
      </form>
      <Footer/>
    </div>
  )
}
