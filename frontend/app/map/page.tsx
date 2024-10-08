import React from "react";

const innerHtml = "";

const Page = () => {
  return (
    <div className="w-screen h-full items-center justify-center flex flex-col">
      <h1 className="text-3xl text-center">Layout</h1>
      <div
        className="w-[80vw] h-[80vh] mt-5 bg-zinc-500 rounded-lg"
        dangerouslySetInnerHTML={{
          __html: innerHtml,
        }}
      ></div>
    </div>
  );
};

export default Page;
