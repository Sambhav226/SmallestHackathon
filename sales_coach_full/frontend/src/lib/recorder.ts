export type RecorderOptions = {
  mimeType?: string;
  timesliceMs?: number;
};

export class MicRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private stream: MediaStream | null = null;

  async start(onChunk: (blob: Blob) => void, opts: RecorderOptions = {}): Promise<void> {
    const mimeType = opts.mimeType ?? 'audio/webm';
    const timeslice = opts.timesliceMs ?? 1500;
    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.mediaRecorder = new MediaRecorder(this.stream, { mimeType });
    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) onChunk(e.data);
    };
    this.mediaRecorder.start(timeslice);
  }

  stop(): void {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }
    if (this.stream) {
      this.stream.getTracks().forEach((t) => t.stop());
    }
    this.mediaRecorder = null;
    this.stream = null;
  }
} 