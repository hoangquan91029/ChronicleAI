"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Film,
  Play,
  Download,
  RefreshCw,
  Clock,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Monitor,
  Smartphone,
  Layers,
  Sparkles,
  Info
} from "lucide-react";

interface SceneInfo {
  scene_number: number;
  title: string;
  duration_seconds: number;
  narration: string;
  citations: Array<{ filename: string; page: number; quote: string }>;
}

interface VideoMetadata {
  video_id: string;
  title: string;
  duration_seconds: number;
  aspect_ratio: string;
  resolution: string;
  fps: number;
  format: string;
  file_size_bytes: number;
  scenes_count: number;
  created_at: string;
  download_url: string;
  stream_url: string;
  scenes_summary: SceneInfo[];
}

export default function VideoStudio() {
  const [selectedFormat, setSelectedFormat] = useState<"SHORTS" | "EXPLAINER" | "DOCUMENTARY">("SHORTS");
  const [selectedAspect, setSelectedAspect] = useState<"16:9" | "9:16">("16:9");
  const [subject, setSubject] = useState("Hoàng đế Lê Thánh Tông (1460–1497)");
  const [rendering, setRendering] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [currentVideo, setCurrentVideo] = useState<VideoMetadata | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    fetchLatestVideo();
  }, []);

  const fetchLatestVideo = async () => {
    try {
      const res = await fetch("/api/videos/latest");
      if (res.ok) {
        const data = await res.json();
        setCurrentVideo(data);
      }
    } catch (err) {
      console.warn("No existing video render found yet:", err);
    }
  };

  const handleRenderVideo = async () => {
    setRendering(true);
    setErrorMsg(null);
    setStatusMessage("Đang khởi tạo tiến trình dựng video phát sóng (Pillow + FFmpeg)...");

    try {
      // Trigger render
      const res = await fetch("/api/videos/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject: subject,
          format: selectedFormat,
          aspect_ratio: selectedAspect
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Khởi tạo render video thất bại");
      }

      const initData = await res.json();
      const videoId = initData.video_id;

      // Poll for completion
      setStatusMessage("Đang vẽ hoạt họa 2D tối giản, tổng hợp âm thanh đa âm & mux phụ đề mov_text...");
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`/api/videos/${videoId}/status`);
          if (statusRes.ok) {
            const statusData = await statusRes.json();
            if (statusData.status === "completed") {
              clearInterval(pollInterval);
              setRendering(false);
              setStatusMessage("Xuất bản video thành công!");
              setCurrentVideo(statusData);
              if (videoRef.current) {
                videoRef.current.load();
              }
            } else if (statusData.status === "failed") {
              clearInterval(pollInterval);
              setRendering(false);
              setErrorMsg(statusData.error_message || "Dựng video thất bại");
            }
          }
        } catch (e) {
          console.error("Polling error:", e);
        }
      }, 2500);

    } catch (err: any) {
      setErrorMsg(err.message || "Lỗi dựng video");
      setRendering(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls Panel */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-5">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-2 rounded-xl bg-amber-100 text-amber-800">
                <Film className="w-5 h-5" />
              </span>
              <h2 className="text-xl font-bold text-slate-900">
                Xưởng Xuất Bản Video Giáo Dục Phát Sóng (Video Studio)
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Quy trình sản xuất video 100% tự chủ ngoại tuyến: Render hoạt họa vector 2D, tổng hợp hòa âm đa âm, gắn nhãn bảo chứng sử liệu & nhúng phụ đề MP4 chuẩn quốc tế.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleRenderVideo}
              disabled={rendering}
              className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white shadow-sm transition ${
                rendering
                  ? "bg-slate-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-amber-700 to-amber-600 hover:from-amber-800 hover:to-amber-700 active:scale-95"
              }`}
            >
              <RefreshCw className={`w-4 h-4 ${rendering ? "animate-spin" : ""}`} />
              <span>{rendering ? "Đang dựng Video..." : "Render Video Phát Sóng"}</span>
            </button>
          </div>
        </div>

        {/* Configuration Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-5">
          {/* Format Selection */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-amber-600" />
              Định dạng & Thời lượng
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setSelectedFormat("SHORTS")}
                className={`py-2 px-2 text-xs font-medium rounded-lg border text-center transition ${
                  selectedFormat === "SHORTS"
                    ? "bg-amber-50 border-amber-500 text-amber-900 font-bold"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                Shorts (30-60s)
              </button>
              <button
                type="button"
                onClick={() => setSelectedFormat("EXPLAINER")}
                className={`py-2 px-2 text-xs font-medium rounded-lg border text-center transition ${
                  selectedFormat === "EXPLAINER"
                    ? "bg-amber-50 border-amber-500 text-amber-900 font-bold"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                Giải thích (3-5m)
              </button>
              <button
                type="button"
                onClick={() => setSelectedFormat("DOCUMENTARY")}
                className={`py-2 px-2 text-xs font-medium rounded-lg border text-center transition ${
                  selectedFormat === "DOCUMENTARY"
                    ? "bg-amber-50 border-amber-500 text-amber-900 font-bold"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                Tài liệu (10-20m)
              </button>
            </div>
          </div>

          {/* Aspect Ratio Selection */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Monitor className="w-3.5 h-3.5 text-amber-600" />
              Tỷ lệ khung hình (Aspect Ratio)
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setSelectedAspect("16:9")}
                className={`flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-medium rounded-lg border transition ${
                  selectedAspect === "16:9"
                    ? "bg-amber-50 border-amber-500 text-amber-900 font-bold"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                <Monitor className="w-3.5 h-3.5" />
                <span>16:9 Ngang (YouTube)</span>
              </button>
              <button
                type="button"
                onClick={() => setSelectedAspect("9:16")}
                className={`flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-medium rounded-lg border transition ${
                  selectedAspect === "9:16"
                    ? "bg-amber-50 border-amber-500 text-amber-900 font-bold"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                <Smartphone className="w-3.5 h-3.5" />
                <span>9:16 Dọc (TikTok/Reels)</span>
              </button>
            </div>
          </div>

          {/* Subject Field */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-amber-600" />
              Chủ đề lịch sử
            </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500"
              placeholder="Nhập tên nhân vật hoặc thời kỳ..."
            />
          </div>
        </div>

        {/* Status notification banner */}
        {rendering && (
          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-center gap-3 text-xs text-amber-900 animate-pulse">
            <RefreshCw className="w-4 h-4 animate-spin text-amber-600" />
            <span>{statusMessage}</span>
          </div>
        )}

        {errorMsg && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-xs text-red-900">
            <AlertCircle className="w-4 h-4 text-red-600" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Main Video Presentation Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Player & Specs */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-slate-900 rounded-2xl overflow-hidden shadow-lg border border-slate-800">
            {/* Player Container */}
            <div className={`relative flex items-center justify-center bg-black ${selectedAspect === "9:16" ? "max-w-xs mx-auto aspect-[9/16]" : "w-full aspect-video"}`}>
              {currentVideo ? (
                <video
                  ref={videoRef}
                  controls
                  playsInline
                  className="w-full h-full object-contain"
                  src={`/api/videos/${currentVideo.video_id}/stream`}
                >
                  Trình duyệt của bạn không hỗ trợ thẻ video HTML5.
                </video>
              ) : (
                <div className="text-center p-8 space-y-3">
                  <Film className="w-12 h-12 text-slate-600 mx-auto" />
                  <p className="text-sm font-medium text-slate-400">
                    Chưa có bản ghi video nào. Bấm <strong>"Render Video Phát Sóng"</strong> để tạo ngay!
                  </p>
                </div>
              )}
            </div>

            {/* Video Controls & Download Bar */}
            {currentVideo && (
              <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white tracking-tight">
                    {currentVideo.title}
                  </h4>
                  <p className="text-xs text-slate-400">
                    Thời lượng: {currentVideo.duration_seconds}s • Độ phân giải: {currentVideo.resolution} ({currentVideo.aspect_ratio})
                  </p>
                </div>

                <a
                  href={`/api/videos/${currentVideo.video_id}/download`}
                  download
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Tải Video MP4</span>
                </a>
              </div>
            )}
          </div>

          {/* Technical Specifications Card */}
          {currentVideo && (
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                Thông Số Kỹ Thuật Đã Chứng Thực
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block">Độ Phân Giải</span>
                  <span className="font-bold text-slate-800">{currentVideo.resolution}</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block">Tốc Độ Khung Hình</span>
                  <span className="font-bold text-slate-800">{currentVideo.fps} FPS</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block">Bộ Mã Hóa (Codecs)</span>
                  <span className="font-bold text-slate-800">H.264 / AAC / Subtitle</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block">Dung Lượng Tệp</span>
                  <span className="font-bold text-slate-800">
                    {(currentVideo.file_size_bytes / (1024 * 1024)).toFixed(2)} MB
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Scene Breakdown & Citations */}
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm h-full">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Layers className="w-4 h-4 text-amber-600" />
              Dòng Thời Gian Phân Cảnh (Timeline)
            </h3>

            {currentVideo && currentVideo.scenes_summary && currentVideo.scenes_summary.length > 0 ? (
              <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
                {currentVideo.scenes_summary.map((scene) => (
                  <div
                    key={scene.scene_number}
                    className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">
                        Cảnh {scene.scene_number}: {scene.title}
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold text-[10px]">
                        {scene.duration_seconds}s
                      </span>
                    </div>

                    <p className="text-slate-600 line-clamp-3 leading-relaxed">
                      "{scene.narration}"
                    </p>

                    {scene.citations && scene.citations.length > 0 && (
                      <div className="pt-1.5 border-t border-slate-200/60 flex items-center gap-1.5 text-[11px] text-emerald-800">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                        <span className="truncate">
                          Nguồn: {scene.citations[0].filename} (Trang {scene.citations[0].page})
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-12 text-center text-slate-400 text-xs">
                Render video để xem danh sách chi tiết các cảnh và chứng cứ sử liệu tương ứng.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
