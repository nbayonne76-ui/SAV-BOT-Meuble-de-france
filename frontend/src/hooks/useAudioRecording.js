import { useState, useRef, useEffect, useCallback } from "react";

export const useAudioRecording = (maxDuration = 30000) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevels, setAudioLevels] = useState([]);
  const [micPermission, setMicPermission] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const recordingTimerRef = useRef(null);
  const animationFrameRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    audioContextRef.current = new (window.AudioContext ||
      window.webkitAudioContext)();

    const requestPermission = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 44100,
          },
        });
        setMicPermission("granted");
        stream.getTracks().forEach((track) => track.stop());
      } catch (err) {
        console.error("Microphone permission denied:", err);
        setMicPermission("denied");
      }
    };

    requestPermission();

    return () => {
      if (recordingTimerRef.current) clearInterval(recordingTimerRef.current);
      if (animationFrameRef.current)
        cancelAnimationFrame(animationFrameRef.current);
      if (audioContextRef.current?.state !== "closed")
        audioContextRef.current.close();
    };
  }, []);

  useEffect(() => {
    if (!isRecording) return;

    const timer = setTimeout(() => {
      if (mediaRecorderRef.current?.state === "recording") {
        mediaRecorderRef.current.stop();
        setIsRecording(false);
      }
    }, maxDuration);

    return () => clearTimeout(timer);
  }, [isRecording, maxDuration]);

  const visualizeAudio = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteTimeDomainData(dataArray);

    const levels = [];
    for (let i = 0; i < 40; i++) {
      const index = Math.floor((i / 40) * dataArray.length);
      levels.push(Math.abs(dataArray[index] - 128));
    }
    setAudioLevels(levels);

    animationFrameRef.current = requestAnimationFrame(visualizeAudio);
  }, []);

  const startRecording = useCallback(
    async (onComplete) => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 44100,
          },
        });

        streamRef.current = stream;
        audioChunksRef.current = [];
        setRecordingTime(0);
        setAudioLevels([]);

        const audioContext = audioContextRef.current;
        const source = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;
        analyser.smoothingTimeConstant = 0.8;
        source.connect(analyser);
        analyserRef.current = analyser;

        const startTime = Date.now();
        recordingTimerRef.current = setInterval(() => {
          const elapsed = Math.floor((Date.now() - startTime) / 1000);
          setRecordingTime(elapsed);
        }, 100);

        visualizeAudio();

        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: "audio/webm;codecs=opus",
        });

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          if (recordingTimerRef.current) {
            clearInterval(recordingTimerRef.current);
            recordingTimerRef.current = null;
          }
          if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
            animationFrameRef.current = null;
          }
          setRecordingTime(0);
          setAudioLevels([]);

          const audioBlob = new Blob(audioChunksRef.current, {
            type: "audio/webm",
          });

          if (audioBlob.size > 500 && onComplete) {
            onComplete(audioBlob);
          }
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start();
        setIsRecording(true);

        return true;
      } catch (err) {
        console.error("Failed to start recording:", err);
        return false;
      }
    },
    [visualizeAudio]
  );

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }

    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    setIsRecording(false);
    setRecordingTime(0);
    setAudioLevels([]);
  }, []);

  return {
    isRecording,
    recordingTime,
    audioLevels,
    micPermission,
    startRecording,
    stopRecording,
    stream: streamRef.current,
  };
};
