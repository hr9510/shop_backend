'use client';
import Footer from '@/component/Footer';
import Header from '@/component/Header';
import QR from '@/component/QR';
import { QRCodeCanvas } from 'qrcode.react';
import React, { useState, useEffect, useRef } from 'react';

export default function Page() {
  const [schedule, setSchedule] = useState([]);
  const [show, setShow] = useState(false);
  const email = localStorage.getItem("teacherEmail")
  const [QRindex, setQRindex] = useState()

 useEffect(() => {
  const fetching = async () => {
    try {
      let data = await fetch("http://localhost:5000/getSchedule");
      let res  = await data.json();

      const dayOrder = {
  monday:    1,
  tuesday:   2,
  wednesday: 3,
  thursday:  4,
  friday:    5,
  saturday:  6,
  sunday:    7
};

res.sort((a, b) => {
  const da = dayOrder[a.day.toLowerCase()];
  const db = dayOrder[b.day.toLowerCase()];
  if (da !== db) {
    return da - db;
  }

  if (a.start_time > b.start_time) return 1;

  if (a.end_time < b.end_time) return -1;
  if (a.end_time > b.end_time) return 1;

  return 0;  
});

      setSchedule(res);

    } catch (err) {
      console.error("Fetch error:", err);
    }
  };
  fetching();
}, []);


  const isBetween = (data) => {
    const currDay = data.curr_day.toLowerCase();
    const day = data.day.toLowerCase();

    if (data.start_time <= data.curr_time && currDay === day) {
      if (data.curr_time <= data.end_time) {
        return true;
      }
      return false;
    }
    return false;
  };

  return (
    <div className="min-h-screen pb-5 bg-gray-100">
      <Header />

      <div className="max-w-4xl px-4 py-8 mx-auto mt-[2vh]">
        {schedule.length > 0 && schedule.map((data, index) =>
          <div key={index}>
            {
              data.email === email ?
                <div key={index} className={` p-[2vh] mb-[2vh] rounded-lg shadow-md transition-all duration-300 transform hover:scale-102 ${isBetween(data) ? `bg-green-100` : `bg-red-100`} } flex justify-between`}>
                  <div>
                    <p className="font-semibold">Day : {data.day.toUpperCase()}</p>
                    <p className="font-semibold">Class : {data.className.toUpperCase()}</p>
                    <p className="font-medium text-gray-900">Subject : {data.subject.toUpperCase()}</p>
                    <p className="font-semibold text-gray-700">Time : {data.start_time} ➜ {data.end_time}</p>
                  </div>
                  {!show && (isBetween(data) ? <button className="font-semibold text-black" onClick={() => { setShow(true); setQRindex(index) }} >Generate QR-CODE</button> : <button disabled className="font-semibold text-gray-400 cursor-not-allowed">Schedule not Active</button>)}
                </div>
                :
                ""
            }
          </div>
        )}
      </div>
      {show && (
        <QR id="QR" useEffect={useEffect} useRef={useRef} QRCodeCanvas={QRCodeCanvas} useState={useState} usersData={{"className" : schedule[QRindex].className , "subject" : schedule[QRindex].subject}}/>
      )}
      <Footer />
    </div>
  );
}
