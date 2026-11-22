"use client";

import React, { useState } from "react";
import { Layout, Palette, Clock, Copy, Check, Download, Camera, BookOpen, Sparkles } from "lucide-react";

interface Citation {
  filename: string;
  page: number;
  chunk_id: string;
  quote: string;
  score: number;
}

interface StoryboardScene {
  scene_number: number;
  title: string;
  estimated_duration_seconds: number;
  narration: string;
  character_dialogue: string;
  historical_setting: string;
  visual_description: string;
  camera_direction: string;
  character_poses: string[];
  ai_image_prompt: string;
  evidence_references: Citation[];
}

interface Storyboard {
  script_title: string;
  subject: string;
  total_scenes: number;
  total_duration_seconds: number;
  visual_theme: string;
  scenes: StoryboardScene[];
}

export default function StoryboardViewer() {
  const [loading, setLoading] = useState(false);
  const [storyboard, setStoryboard] = useState<Storyboard | null>(null);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const handleGenerateStoryboard = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/storyboards/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject: "Hoàng đế Lê Thánh Tông (1460–1497)",
          visual_style_preference: "minimalist_2d_stick_figure",
        }),
      });

      if (!res.ok) throw new Error("Tạo phân cảnh thất bại");
      const data = await res.json();
      setStoryboard(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyPrompt = (prompt: string, idx: number) => {
    navigator.clipboard.writeText(prompt);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const handleExportMarkdown = async () => {
    if (!storyboard) return;
    try {
      const res = await fetch("/api/storyboards/export/markdown", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(storyboard),
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "chronicle_storyboard.md";
      a.click();
    } catch (err) {
      console.error(err);
    }
  };

  const handleExportJson = () => {
    if (!storyboard) return;
    const blob = new Blob([JSON.stringify(storyboard, null, 2)], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "chronicle_storyboard.json";
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Control Box */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
              <Layout className="w-5 h-5 text-amber-600" />
              Bảng Phân Cảnh Thị Giác (Storyboard Generator)
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Chuyển hóa kịch bản thành các khung hình hoạt họa 2D tối giản (minimalist stick-figure), góc máy điện ảnh và prompt tạo ảnh AI.
            </p>
          </div>

          <button
            onClick={handleGenerateStoryboard}
            disabled={loading}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-lg shadow-sm transition disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            {loading ? "Đang tạo storyboard..." : "Tạo Storyboard 2D"}
          </button>
        </div>

        <div className="p-3.5 bg-amber-50/70 border border-amber-200/80 rounded-lg text-xs text-amber-900 flex items-start gap-2">
          <Palette className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
          <div>
            <span className="font-semibold">Phong cách mỹ thuật định hướng: </span>
            Hoạt họa 2D tối giản Việt Nam (Minimalist 2D Animation), nhân vật hình que (stick-figure) biểu cảm cao, trang phục truyền thống thế kỷ 15 (áo giao lĩnh, khăn đóng), hậu cảnh màu nước cổ điển.
          </div>
        </div>
      </div>

      {/* Storyboard Cards */}
      {storyboard && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <div>
              <span className="text-xs font-semibold text-amber-700 uppercase tracking-wider">
                Bảng Phân Cảnh Hoàn Chỉnh
              </span>
              <h3 className="text-lg font-bold text-slate-900 mt-0.5">{storyboard.script_title}</h3>
              <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                <span>{storyboard.total_scenes} Phân cảnh</span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400" />
                  {storyboard.total_duration_seconds} giây
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleExportMarkdown}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium rounded-lg transition"
              >
                <Download className="w-3.5 h-3.5 text-slate-600" />
                Xuất Markdown
              </button>
              <button
                onClick={handleExportJson}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium rounded-lg transition"
              >
                <Download className="w-3.5 h-3.5 text-slate-600" />
                Xuất JSON
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6">
            {storyboard.scenes.map((s, idx) => (
              <div
                key={s.scene_number}
                className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4 hover:border-amber-300 transition"
              >
                <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 border-b border-slate-100 pb-3">
                  <div className="flex items-center gap-2.5">
                    <span className="w-7 h-7 rounded-full bg-slate-900 text-white font-bold text-xs flex items-center justify-center">
                      #{s.scene_number}
                    </span>
                    <h4 className="font-semibold text-slate-900 text-base">{s.title}</h4>
                  </div>
                  <span className="px-2.5 py-1 bg-amber-100 text-amber-900 rounded font-semibold text-xs self-start">
                    ⏱️ Thời lượng: {s.estimated_duration_seconds}s
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="space-y-2 bg-slate-50 p-4 rounded-lg border border-slate-100">
                    <span className="font-semibold text-slate-700 block">Bối cảnh lịch sử & Hoạt cảnh:</span>
                    <p className="text-slate-600 leading-relaxed">{s.visual_description}</p>
                    <div className="pt-2 flex items-center gap-1.5 text-slate-500">
                      <Camera className="w-3.5 h-3.5 text-amber-600" />
                      <span>{s.camera_direction}</span>
                    </div>
                  </div>

                  <div className="space-y-2 bg-slate-50 p-4 rounded-lg border border-slate-100">
                    <span className="font-semibold text-slate-700 block">Lời bình & Thoại:</span>
                    <p className="text-slate-700 leading-relaxed italic">"{s.narration}"</p>
                    {s.character_dialogue && (
                      <p className="text-amber-900 font-medium pt-1">
                        💬 {s.character_dialogue}
                      </p>
                    )}
                  </div>
                </div>

                {/* AI Prompt Card */}
                <div className="bg-slate-900 text-slate-200 p-4 rounded-lg space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-amber-400 font-mono font-medium flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      Prompt Tạo Ảnh AI (DALL-E 3 / Midjourney / Imagen):
                    </span>
                    <button
                      onClick={() => copyPrompt(s.ai_image_prompt, idx)}
                      className="inline-flex items-center gap-1 text-[11px] px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition"
                    >
                      {copiedIdx === idx ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" /> Đã sao chép!
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" /> Sao chép Prompt
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-xs font-mono leading-relaxed text-slate-300 bg-slate-950/60 p-3 rounded border border-slate-800">
                    {s.ai_image_prompt}
                  </p>
                </div>

                {/* Citations references */}
                {s.evidence_references && s.evidence_references.length > 0 && (
                  <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
                    <span className="font-semibold text-slate-500">Căn cứ sử liệu cảnh quay:</span>
                    {s.evidence_references.map((c, cIdx) => (
                      <span
                        key={cIdx}
                        className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-slate-100 border border-slate-200 rounded font-mono text-[11px] text-slate-700"
                      >
                        <BookOpen className="w-3 h-3 text-amber-600" />
                        {c.filename} (Trang {c.page})
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
