import { cp, mkdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..')
const source=path.join(root,'node_modules','@mediapipe','tasks-vision','wasm')
const destination=path.join(root,'public','mediapipe','wasm')
await mkdir(destination,{recursive:true})
await cp(source,destination,{recursive:true})
console.log('Copied MediaPipe WASM runtime to public/mediapipe/wasm for offline use.')
