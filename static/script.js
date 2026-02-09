function startVoice(){
 if(!('webkitSpeechRecognition' in window)){
  alert("Voice not supported");
  return;
 }
 const r=new webkitSpeechRecognition();
 r.lang="en-IN";
 r.onresult=e=>{
  problem.value=e.results[0][0].transcript;
 };
 r.start();
}

function speakLast(){
 const msgs=document.querySelectorAll(".ai");
 if(!msgs.length) return;
 const text=msgs[msgs.length-1].innerText;

 const u=new SpeechSynthesisUtterance(text);
 u.lang=(langsel.value=="Hindi")?"hi-IN":"en-US";

 speechSynthesis.cancel();
 speechSynthesis.speak(u);
}

function stopReading(){
 speechSynthesis.cancel();
}
