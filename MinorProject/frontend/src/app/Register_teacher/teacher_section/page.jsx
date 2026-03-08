import Footer from '@/component/Footer'
import Header from '@/component/Header'
import Link from 'next/link'
import React from 'react'
import { AiFillSchedule } from 'react-icons/ai';
import { SiGoogleclassroom } from 'react-icons/si';
import { GrSchedulePlay } from "react-icons/gr";


export default function page() {
  return (
    <div>
      <Header />
      <main className="justify-evenly w-[80%] bg-gray-900 h-[400px] flex items-center mx-auto my-10 rounded-lg shadow-xl shadow-gray-300">
        <Link href={"teacher_section/CreateSession"}>
          <section className="px-6 bg-gray-200 w-[20vw] h-[40vh] flex flex-col items-center justify-center rounded-3xl hover:scale-105 transition-transform duration-500 shadow-lg">
            <SiGoogleclassroom size={80} className="mb-4 text-gray-800" />
            <p className="text-xl font-semibold text-gray-800">Create a Session</p>
          </section>
        </Link>
        <Link href={"teacher_section/Creating_schedule"}>
          <section className="px-6  bg-gray-200 w-[20vw] h-[40vh] flex flex-col items-center justify-center rounded-3xl hover:scale-105 transition-transform duration-500 shadow-lg">
            <AiFillSchedule size={80} className="mb-4 text-gray-800" />
            <p className="text-xl font-semibold text-gray-800">Create a Schedule</p>
          </section>
        </Link>
        <Link href={"teacher_section/Continue_schedule"}>
          <section className="px-6  bg-gray-200 w-[20vw] h-[40vh] flex flex-col items-center justify-center rounded-3xl hover:scale-105 transition-transform duration-500 shadow-lg">
            <GrSchedulePlay size={80} className="mb-4 text-gray-800" />
            <p className="text-xl font-semibold text-gray-800">Continue the Schedule</p>
          </section>
        </Link>
      </main>
      <Footer />
    </div>
  )
}
