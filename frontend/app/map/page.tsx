import Image from "next/image";
import React from "react";

const Page = () => {
  return (
    <div className="w-screen h-full items-center justify-center flex flex-col">
      <h1 className="text-3xl text-center">Layout</h1>
      <div className="relative h-[80vh] mt-5 overflow-hidden w-fit bg-zinc-500 rounded-lg">
        <Image src={"/3_office.jpg"} alt="" width={1200} height={100} />
        <p className="bg-green-500 border-2 border-green-800 z-10 absolute top-28 left-[200px]">
          Vacant
        </p>
        <p className="bg-red-500 border-2 border-red-800 z-10 absolute top-28 left-[400px]">
          Occupied
        </p>
      </div>
    </div>
  );
};

export default Page;
