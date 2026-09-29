# Optional webcam analysis

During a live interview, choose **Enable camera** and grant the browser camera permission. The bundled MediaPipe Face Landmarker model and WebAssembly runtime run in the browser. It samples frames locally while enabled; stopping the analysis stops the camera stream and saves only these session summary values to the local API:

- Face visibility: fraction of sampled frames with a detected face.
- Face centering: approximate distance of the detected face-box center from the frame center.
- Head-position stability: approximate change in landmark-bounding-box center between sampled frames.

No images, frames, face embeddings, or facial-expression/blendshape data are stored or transmitted. The app does not analyze gaze, posture, confidence, emotion, personality, honesty, or intent. These rough measurements vary with lighting, camera angle, distance, glasses, and accessibility needs and should not be used for hiring decisions.

Camera access requires a secure context (`localhost` or HTTPS) and an explicit user action/permission. If camera permission is unavailable or denied, interview practice still works normally. MediaPipe's official docs describe Face Landmarker image/video inputs and landmark outputs: https://developers.google.com/mediapipe/solutions/vision/face_landmarker
