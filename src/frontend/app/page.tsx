// frontend/src/app/page.tsx
"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";
import { UploadCloud, Video, Loader2, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

// --- Types based on your backend response ---
interface PipelineResults {
  visual: { visual_score: number; details: { engagement: number; energy: number } };
  audio: { prosody_score: number; details: { pace_bpm: number; silence_ratio: number } };
  content: { content_score: number; accuracy_score: number; structure_score: number; key_strengths: string[]; missing_concepts: string[] };
}

interface AnalysisResult {
  overall_score: number;
  pipelines: PipelineResults;
  transcript: string;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // --- Drag and Drop Logic ---
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0];
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setError(null);
    setResult(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'video/*': [] },
    maxFiles: 1,
  });

  // --- API Submission Logic ---
  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("topic", "General Teaching"); // You could add an input field for this

    try {
      // IMPORTANT: This URL needs to point to wherever your backend is running.
      // For local dev: http://localhost:8000/analyze
      // For Vercel deployment: You'll use an environment variable.
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
      //const backendUrl = "http://127.0.0.1:8000";
      const response = await axios.post(`${backendUrl}/analyze`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 300000, // 5 minute timeout for heavy processing
      });
      setResult(response.data);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Analysis failed. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  // --- Helper Component for Metric Cards ---
  const MetricCard = ({ title, score, colorClass = "bg-primary" }: { title: string; score: number; colorClass?: string }) => (
    <Card className="shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold text-gray-800 mb-2">{score}</div>
        {/* Normalize score to percentage for progress bar if needed. Assuming scores are 0-10 */}
        <Progress value={score * 10} className={`h-2 ${colorClass.replace("bg-", "[&>div]:bg-")}`} />
      </CardContent>
    </Card>
  );

  // ================= View: Results =================
  if (result) {
    const { pipelines } = result;
    return (
      <main className="container mx-auto p-6 max-w-5xl space-y-6">
         <Button variant="ghost" onClick={() => { setResult(null); setFile(null); setPreviewUrl(null) }} className="mb-4 text-white hover:text-white/80 hover:bg-white/10">
            ← Analyze another video
        </Button>

        {/* Overall Score Circle */}
        <Card className="relative overflow-hidden text-center py-10 shadow-lg border-none">
           <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent pointer-events-none"></div>
          <h2 className="text-xl font-semibold mb-6 text-gray-700">Overall Teaching Score</h2>
          <div className="relative inline-flex items-center justify-center">
            {/* Simple CSS circle for demo, could use a charting lib for real gauge */}
            <div className="w-40 h-40 rounded-full bg-gradient-to-tr from-primary to-violet-400 flex items-center justify-center shadow-xl">
               <div className="w-32 h-32 rounded-full bg-white flex items-center justify-center">
                  <span className="text-5xl font-extrabold text-primary">{result.overall_score}</span>
               </div>
            </div>
          </div>
        </Card>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Mapping your backend data to the UI cards mentioned in screenshots */}
            <MetricCard 
              title="Clarity (Content)" 
              score={pipelines?.content?.content_score ?? 0} 
            />
            <MetricCard 
              title="Engagement (Visual)" 
              score={pipelines?.visual?.details?.engagement ?? 0} 
              colorClass="bg-blue-500" 
            />
            <MetricCard 
              title="Tone/Variety (Audio)" 
              score={pipelines?.audio?.prosody_score ?? 0} 
              colorClass="bg-indigo-500" 
            />
            <MetricCard 
              title="Technical Correctness" 
              score={pipelines?.content?.accuracy_score ?? 0} 
              colorClass="bg-green-500" 
            />
            <MetricCard 
              title="Confidence (Energy)" 
              score={pipelines?.visual?.details?.energy ?? 0} 
              colorClass="bg-purple-500" 
            />
            {/* Pacing needs normalization. Assuming 120bpm is ideal (10/10) */}
            <MetricCard 
              title="Pacing (BPM)" 
              score={Math.min(Math.round(pipelines?.audio?.details?.pace_bpm ?? 0), 160)} 
              colorClass="bg-pink-500" 
            />
          </div>
        
         <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             {/* Summary / Transcript */}
            <Card className="shadow-md">
                <CardHeader>
                    <CardTitle>Generating Transcript Summary...</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-sm leading-relaxed h-48 overflow-y-auto p-2 bg-slate-50 rounded-md">
                      {/* You would use the LLM to generate a real summary based on the transcript. For now, showing transcript fragment. */}
                      {result.transcript || "No transcript available."}
                  </p>
                </CardContent>
            </Card>

             {/* Strengths & Recommendations - SAFE VERSION */}
              <div className="space-y-6">
                  <Card className="shadow-md">
                      <CardHeader>
                          <CardTitle>Key Strengths</CardTitle>
                      </CardHeader>
                      <CardContent>
                          <ul className="space-y-2">
                              {/* SAFE CHECK: pipelines?.content?.key_strengths */}
                              {pipelines?.content?.key_strengths?.map((strength, i) => (
                                  <li key={i} className="flex items-start gap-2">
                                      <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5" />
                                      <span className="text-sm">{strength}</span>
                                  </li>
                              )) || <li className="text-sm text-muted-foreground">Analysis provided no specific strengths.</li>}
                          </ul>
                      </CardContent>
                  </Card>

                  <Card className="shadow-md border-l-4 border-l-yellow-400">
                      <CardHeader>
                          <CardTitle>Insights & Recommendations</CardTitle>
                      </CardHeader>
                      <CardContent>
                          <ul className="space-y-2">
                              {/* SAFE CHECK: pipelines?.content?.missing_concepts */}
                              {pipelines?.content?.missing_concepts?.map((concept, i) => (
                                  <li key={i} className="text-sm flex items-start gap-2 before:content-['•'] before:mr-2 before:text-yellow-500">
                                      Consider covering: {concept}
                                  </li>
                              )) || (
                                  <li className="text-sm text-muted-foreground">Keep up the great work!</li>
                              )}
                              
                              {/* SAFE CHECK: pipelines?.audio?.details?.pace_bpm */}
                              {(pipelines?.audio?.details?.pace_bpm ?? 0) > 150 && (
                                  <li className="text-sm flex gap-2 before:content-['•'] before:mr-2 before:text-yellow-500">
                                      Try slowing down your speaking pace slightly.
                                  </li>
                              )}
                          </ul>
                      </CardContent>
                  </Card>
              </div>
         </div>
      </main>
    );
  }


  // ================= View: Upload Page =================
  return (
    <main className="container mx-auto p-6 min-h-screen flex flex-col items-center justify-center">
      <Card className="w-full max-w-3xl shadow-2xl border-white/20 bg-white/95 backdrop-blur-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-primary">AI-Powered Teaching Quality Analysis</CardTitle>
          <p className="text-muted-foreground">Upload your lecture to get instant pedagogical feedback.</p>
        </CardHeader>
        <CardContent className="space-y-6">
          
          {/* Dropzone Area */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
              isDragActive ? "border-primary bg-primary/5" : "border-gray-300 hover:border-primary/50 hover:bg-gray-50"
            }`}
          >
            <input {...getInputProps()} />
            <UploadCloud className={`h-16 w-16 mx-auto mb-4 ${isDragActive ? 'text-primary' : 'text-gray-400'}`} />
            {isDragActive ? (
              <p className="text-lg text-primary font-medium">Drop the video here...</p>
            ) : (
              <div>
                <p className="text-lg font-medium text-gray-700">Drop your teaching video here or click to browse</p>
                <p className="text-sm text-muted-foreground mt-2">Supports MP4, MOV, AVI (Max 200MB)</p>
              </div>
            )}
          </div>

          {/* Preview & Analyze Button */}
          {file && (
            <div className="space-y-4 animate-in fade-in-0 slide-in-from-bottom-4">
               <div className="bg-violet-50 p-3 rounded-lg flex items-center gap-3">
                 <Video className="text-primary h-5 w-5"/>
                 <span className="text-sm font-medium text-gray-700 truncate">{file.name}</span>
               </div>
               
               {previewUrl && (
                 <div className="rounded-lg overflow-hidden shadow-md mx-auto max-w-md">
                    <video src={previewUrl} controls className="w-full" />
                 </div>
               )}

               {error && (
                   <Alert variant="destructive">
                     <AlertTitle>Error</AlertTitle>
                     <AlertDescription>{error}</AlertDescription>
                   </Alert>
               )}

              <Button onClick={handleAnalyze} disabled={loading} className="w-full text-lg py-6 bg-gradient-to-r from-primary to-violet-600 hover:from-primary/90 hover:to-violet-600/90 transition-all shadow-md">
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Analyzing Pipeline...
                  </>
                ) : (
                  "Analyze Performance 🚀"
                )}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
