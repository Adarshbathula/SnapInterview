import { useEffect, useRef, useState } from 'react'
import { Download, LoaderCircle, Mic, Square, Volume2 } from 'lucide-react'

export default function MicrophoneRecorder({speechReady,onTranscript,onDuration,onSegments}){
  const recorderRef=useRef(null),streamRef=useRef(null),chunksRef=useRef([]),startRef=useRef(0),urlRef=useRef(null)
  const [recording,setRecording]=useState(false),[busy,setBusy]=useState(false),[message,setMessage]=useState(''),[audioUrl,setAudioUrl]=useState(''),[error,setError]=useState('')
  const cleanup=()=>{if(streamRef.current)streamRef.current.getTracks().forEach(t=>t.stop());streamRef.current=null}
  useEffect(()=>()=>{cleanup();if(urlRef.current)URL.revokeObjectURL(urlRef.current)},[])
  const start=async()=>{
    setError('');setMessage('');setAudioUrl('');if(urlRef.current){URL.revokeObjectURL(urlRef.current);urlRef.current=null}
    if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){setError('Microphone recording is not supported in this browser.');return}
    try{
      const stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true}});streamRef.current=stream;chunksRef.current=[]
      const types=['audio/webm;codecs=opus','audio/webm','audio/ogg;codecs=opus','audio/mp4'];const mimeType=types.find(t=>MediaRecorder.isTypeSupported(t));const recorder=mimeType?new MediaRecorder(stream,{mimeType}):new MediaRecorder(stream)
      recorderRef.current=recorder;startRef.current=Date.now();recorder.ondataavailable=e=>{if(e.data?.size)chunksRef.current.push(e.data)}
      recorder.onstop=async()=>{
        const elapsed=Math.max(1,(Date.now()-startRef.current)/1000);onDuration?.(elapsed)
        const blob=new Blob(chunksRef.current,{type:recorder.mimeType||'audio/webm'});chunksRef.current=[]
        if(urlRef.current)URL.revokeObjectURL(urlRef.current);urlRef.current=URL.createObjectURL(blob);setAudioUrl(urlRef.current)
        cleanup();setBusy(true)
        if(!speechReady){setMessage('Clip kept in this browser tab only. Install the optional local Whisper model to transcribe; nothing was uploaded.');setBusy(false);return}
        try{
          const form=new FormData();form.append('file',blob,`answer.${(recorder.mimeType||'audio/webm').includes('ogg')?'ogg':(recorder.mimeType||'').includes('mp4')?'mp4':'webm'}`);form.append('language','en')
          const response=await fetch('/api/speech/transcribe',{method:'POST',body:form});const data=await response.json().catch(()=>({}))
          if(!response.ok)throw new Error(data.detail||`Transcription failed (${response.status})`)
          if(data.text)onTranscript?.(data.text,data);else setMessage('No speech was detected. Try again or type your answer.')
          onSegments?.(data.segments||[]);setMessage(data.text?'Local transcription complete. Review and edit it before submitting.':'No speech detected; type or record again.')
        }catch(e){setError(e.message||'Could not transcribe locally. The clip remains in this tab.')}
        finally{setBusy(false)}
      }
      recorder.start(300);setRecording(true)
    }catch(e){cleanup();setError(e.name==='NotAllowedError'?(window.self!==window.top?'The embedded preview may block microphone access. Run SnapInterview at http://localhost:5173 on your laptop and allow microphone access there.':'Microphone access was denied. Allow it for this site in browser and operating-system privacy settings, then retry.'):(e.message||'Could not access the microphone.'))}
  }
  const stop=()=>{if(recorderRef.current?.state==='recording'){setRecording(false);recorderRef.current.stop()}}
  return <div className="mic-recorder">
    <button className={`mic-record-button ${recording?'recording':''}`} onClick={recording?stop:start} disabled={busy} title={recording?'Stop recording':'Record an answer'}>{busy?<LoaderCircle size={14} className="spin"/>:recording?<Square size={13} fill="currentColor"/>:<Mic size={14}/>}<span>{busy?'Transcribing locally…':recording?'Stop recording':'Record answer'}</span></button>
    {recording&&<span className="recording-live"><i/> Recording locally</span>}
    {audioUrl&&!recording&&<div className="recording-preview"><audio controls src={audioUrl}/><a href={audioUrl} download="snapinterview-answer.webm" title="Download recording"><Download size={14}/></a><Volume2 size={13}/></div>}
    {message&&<span className="recorder-message">{message}</span>}{error&&<span className="recorder-error">{error}</span>}
  </div>
}
