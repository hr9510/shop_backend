"use client"
import Footer from '@/component/Footer'
import Header from '@/component/Header'
import React, { useEffect, useRef, useState } from 'react'
import { QRCodeCanvas } from 'qrcode.react'
import {HandleChange} from '@/component/Common'
import QR from '@/component/QR'

export default function Page() {
  
  const [show, setShow] = useState(false);
  const [usersData, setUserData] = useState({ subject: "", className: "" });
const submitted = (e) => {
  e.preventDefault();
  setShow(true);
};



  return (
    <div className='flex flex-col items-center min-h-screen bg-gradient-to-br from-gray-100 to-gray-300'>
      <Header />
      
      <main className='flex flex-col items-center my-10'>
        <form
          className='flex flex-col my-5 space-y-3'
          onSubmit={submitted}
        >
          <input
            className='py-[1vh] px-[1vw] rounded-3xl w-[30vw] border-black border-[2px]'
            type="text"
            placeholder="Enter Subject Name"
            onChange={(e) => HandleChange(e, usersData, setUserData)}
            name='subject'
            value={usersData.subject}
            required
          />
          <input
            className='py-[1vh] px-[1vw] rounded-3xl w-[30vw] border-black border-[2px]'
            type="text"
            placeholder="Enter Class Name"
            onChange={(e) => HandleChange(e, usersData, setUserData)}
            name='className'
            value={usersData.className}
            required
          />
          <button
            type='submit'
            className='bg-gray-900 text-white py-2 rounded-3xl hover:bg-gray-700 transition-colors duration-300 w-[10vw] mx-auto mt-4'
          >
            Create Session
          </button>
        </form>

        {show && (
          <QR useEffect={useEffect} useRef={useRef} QRCodeCanvas={QRCodeCanvas} useState={useState} usersData={usersData} />
              )}
      </main>

      <Footer />
    </div>
  )
}
