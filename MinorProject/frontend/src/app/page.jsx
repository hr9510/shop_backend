import Link from "next/link";
import Footer from "../component/Footer";
import Header from "../component/Header";

export default function Home() {
  return (
    <div className="w-full min-h-screen overflow-hidden bg-gradient-to-tr from-gray-200 to-white">
      <Header/>
      <main className="py-6 w-[80%] bg-gray-900 h-[480px] flex flex-col items-center mx-auto mt-10 space-y-10 rounded-lg shadow-xl shadow-gray-300">
        <p className="px-4 text-xl font-semibold text-center text-white">
          Welcome to the Students Attendance Management System. This platform
          allows you to efficiently manage and track student attendance with ease.
        </p>

        <section className="flex items-center w-full px-6 justify-evenly">
          <Link href={"/Register_teacher"} className="bg-gray-200 w-[30vw] h-[40vh] flex flex-col items-center justify-center rounded-3xl hover:scale-105 transition-transform duration-500 shadow-lg">
            <img
              src="https://cdn-icons-png.flaticon.com/512/2921/2921222.png"
              alt="Teacher"
              className="w-20 mb-4"
            />
            <p className="text-xl font-semibold text-gray-800">Register As A Teacher</p>
          </Link>

          <Link href={"/Register_student"} className="bg-gray-200 w-[30vw] h-[40vh] flex flex-col items-center justify-center rounded-3xl hover:scale-105 transition-transform duration-500 shadow-lg">
            <img
              src="https://cdn-icons-png.flaticon.com/512/3135/3135755.png"
              alt="Student"
              className="w-20 mb-4"
            />
            <p className="text-xl font-semibold text-gray-800">Register As A Student</p>
          </Link>
        </section>
      </main>
      <Footer/>
    </div>
  );
}
