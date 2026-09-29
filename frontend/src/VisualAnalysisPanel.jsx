import { useEffect, useRef, useState } from 'react'
import { FaceLandmarker, FilesetResolver } from '@mediapipe/tasks-vision'
import { Camera, CameraOff, CircleHelp, LoaderCircle, LockKeyhole, ScanFace, Square } from 'lucide-react'

const emptyStats=()=>({samples:0,faceSamples:0,centerTotal:0,motionTotal:0,lastCenter:null,startedAt:0})
function summarize(s){
  const visibility=s.samples?Math.round(100*s.faceSamples/s.samples):0
  const centering=s.faceSamples?Math.round(100*s.centerTotal/s.faceSamples):0
  const stability=s.faceSamples>1?Math.round(Math.max(0,100-Math.min(100,(s.motionTotal/(s.faceSamples-1))*350))):0
  return {face_visibility:visibility,face_centering:centering,head_position_stability:stability,samples:s.samples,duration_seconds:s.startedAt?Math.round((Date.now()-s.startedAt)/1000):0,source:'MediaPipe Face Landmarker, on-device; no frames stored'}
}

export default function VisualAnalysisPanel({onMetrics}){
  const videoRef=useRef(null),streamRef=useRef(null),landmarkerRef=useRef(null),rafRef=useRef(null),runningRef=useRef(false),statsRef=useRef(emptyStats())
  const [active,setActive]=useState(false),[loading,setLoading]=useState(false),[error,setError]=useState(''),[status,setStatus]=useState('Camera is off'),[metrics,setMetrics]=useState(null)
  const stopResources=()=>{runningRef.current=false;if(rafRef.current)cancelAnimationFrame(rafRef.current);rafRef.current=null;if(streamRef.current)streamRef.current.getTracks().forEach(t=>t.stop());streamRef.current=null;if(landmarkerRef.current){landmarkerRef.current.close();landmarkerRef.current=null}if(videoRef.current)videoRef.current.srcObject=null}
  useEffect(()=>()=>stopResources(),[])
  const start=async()=>{
    setError('');setMetrics(null);setLoading(true);setStatus('Requesting camera permission…')
    try{
      if(!navigator.mediaDevices?.getUserMedia)throw new Error('Camera access is not available in this browser. Use localhost or HTTPS and check browser permissions.')
      const stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'user',width:{ideal:640},height:{ideal:480}},audio:false})
      streamRef.current=stream
      const video=videoRef.current;video.srcObject=stream;await video.play()
      setStatus('Loading local face-landmark model…')
      const files=await FilesetResolver.forVisionTasks('/mediapipe/wasm')
      const task=await FaceLandmarker.createFromOptions(files,{baseOptions:{modelAssetPath:'/models/face_landmarker.task'},runningMode:'VIDEO',numFaces:1,minFaceDetectionConfidence:.5,minFacePresenceConfidence:.5,minTrackingConfidence:.5})
      landmarkerRef.current=task;statsRef.current={...emptyStats(),startedAt:Date.now()};runningRef.current=true;setActive(true);setLoading(false);setStatus('Analyzing on this device')
      let last=0
      const loop=(now)=>{
        if(!runningRef.current)return
        if(now-last>650&&video.readyState>=2){
          last=now
          try{
            const result=task.detectForVideo(video,now)
            const s=statsRef.current;s.samples+=1
            const landmarks=result.faceLandmarks?.[0]
            if(landmarks?.length){
              s.faceSamples+=1
              const xs=landmarks.map(p=>p.x),ys=landmarks.map(p=>p.y)
              const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys)
              const cx=(minX+maxX)/2,cy=(minY+maxY)/2
              const distance=Math.sqrt((cx-.5)**2+(cy-.48)**2)
              s.centerTotal+=Math.max(0,1-Math.min(1,distance/.5))
              if(s.lastCenter){s.motionTotal+=Math.sqrt((cx-s.lastCenter.x)**2+(cy-s.lastCenter.y)**2)}
              s.lastCenter={x:cx,y:cy}
            }
            setStatus(landmarks?'Face in frame · local analysis':'Looking for a face…')
          }catch(e){setStatus('Analysis paused');setError(e.message||'Frame analysis failed.')}
        }
        rafRef.current=requestAnimationFrame(loop)
      }
      rafRef.current=requestAnimationFrame(loop)
    }catch(e){stopResources();setLoading(false);setActive(false);setStatus('Camera is off');const denied=e.name==='NotAllowedError'?(window.self!==window.top?'The embedded preview may block camera access. Run SnapInterview at http://localhost:5173 on your laptop and allow camera access there.':'Camera access was denied. Allow it for this site in browser and operating-system privacy settings, then retry.'):null;setError(denied||e.message||'Could not start camera.')}
  }
  const stop=()=>{
    const result=summarize(statsRef.current);stopResources();setActive(false);setLoading(false);setMetrics(result);setStatus('Camera off · summary saved locally');onMetrics?.(result)
  }
  return <div className="visual-panel">
    <div className="visual-panel-head"><div className="visual-head-icon"><ScanFace size={15}/></div><div className="visual-head-copy"><b>Visual communication</b><span>Optional · camera stays local</span></div><button className="visual-help" title="This measures face-in-frame and approximate head-position signals only; it does not infer emotion, confidence, or personality."><CircleHelp size={14}/></button></div>
    {active||loading?<div className="camera-preview"><video ref={videoRef} autoPlay muted playsInline/><span className="camera-live"><i/>{loading?'STARTING':status}</span>{active&&<div className="camera-overlay">LOCAL ONLY</div>}</div>:<div className="camera-placeholder"><Camera size={19}/><span>{metrics?`${metrics.samples} local frames analyzed`:'Camera is off until you enable it'}</span></div>}
    {error&&<div className="visual-error">{error}</div>}
    {metrics&&<div className="visual-metrics"><div><b>{metrics.face_visibility}%</b><span>Face in frame</span></div><div><b>{metrics.face_centering}%</b><span>Face centering</span></div><div><b>{metrics.head_position_stability}%</b><span>Head position stability*</span></div><small>*Approximate frame-to-frame landmark stability; not a psychological measure.</small></div>}
    <div className="visual-panel-foot"><span><LockKeyhole size={12}/> No frames recorded or uploaded</span>{active?<button className="camera-stop" onClick={stop}><Square size={12} fill="currentColor"/> Stop</button>:<button className="camera-start" onClick={start} disabled={loading}>{loading?<LoaderCircle size={13} className="spin"/>:<Camera size={13}/>} {loading?'Starting…':metrics?'Start again':'Enable camera'}</button>}</div>
    <div className="camera-disclaimer">Face presence and centering are rough webcam signals, affected by lighting and camera placement. No gaze, emotion, honesty, or confidence score.</div>
  </div>
}
