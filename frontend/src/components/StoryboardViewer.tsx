"use client";

import React, { useState } from "react";
import {
  Layout,
  Palette,
  Clock,
  Copy,
  Check,
  Download,
  Camera,
  BookOpen,
  Sparkles,
  Monitor,
  Smartphone,
  Edit3,
  Video,
  ShieldCheck
} from "lucide-react";

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
  aspect_ratio: string;
  visual_theme: string;
  scenes: StoryboardScene[];
}

export default function StoryboardViewer({
  onNavigateToVideo
}: {
  onNavigateToVideo?: () => void;
}) {
  const [loading, setLoading] = useState(false);
  const [aspectRatio, setAspectRatio] = useState<"16:9" | "9:16">("16:9");
  const [storyboard, setStoryboard] = useState<Storyboard | null>(null);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  // Edit scene state
  const [editingSceneNum, setEditingSceneNum] = useState<number | null>(null);
  const [editPrompt, setEditPrompt] = useState("");
  const [editVisualDesc, setEditVisualDesc] = useState("");
  const [savingScene, setSavingScene] = useState(false);

  const handleGenerateStoryboard = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/storyboards/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject: "Hoàng đế Lê Thánh Tông (1460–1497)",
          aspect_ratio: aspectRatio,
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

  const handleStartEdit = (scene: StoryboardScene) => {
    setEditingSceneNum(scene.scene_number);
    setEditPrompt(scene.ai_image_prompt);
    setEditVisualDesc(scene.visual_description);
  };

  const handleSaveScene = async (sceneNumber: number) => {
    setSavingScene(true);
    try {
      const res = await fetch(`/api/storyboards/scenes/${sceneNumber}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ai_image_prompt: editPrompt,
          visual_description: editVisualDesc
        })
      });

      if (res.ok) {
        const updated = await res.json();
        setStoryboard(updated);
        setEditingSceneNum(null);
      } else {
        alert("Lưu phân cảnh storyboard thất bại");
      }
    } catch (err) {
      console.error("Save storyboard scene error:", err);
    } finally {
      setSavingScene(false);
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
      {/* Control Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Layout className="w-5 h-5 text-amber-600" />
              Phân Cảnh Hoạt Họa 2D (Storyboard Generator)
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Chuyển hóa kịch bản thành phân cảnh trực quan: Phác họa nhân vật người que 2D tối giản, trang phục thế kỷ 15 và prompt tạo ảnh AI chuẩn hóa.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleGenerateStoryboard}
              disabled={loading}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-amber-700 to-amber-600 hover:from-amber-800 hover:to-amber-700 text-white font-semibold text-xs rounded-xl shadow-sm transition disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              {loading ? "Đang tạo phân cảnh..." : "Tạo Phân Cảnh Mới"}
            </button>
          </div>
        </div>

        {/* Aspect Ratio Selector */}
        <div className="pt-2 flex flex-col sm:flex-row sm:items-center gap-3">
          <span className="text-xs font-semibold text-slate-700">Tỷ lệ khung hình Storyboard:</span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setAspectRatio("16:9")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition ${
                aspectRatio === "16:9"
                  ? "bg-amber-50 border-amber-500 text-amber-900 font-bold"
                  : "border-slate-200 text-slate-600 hover:bg-slate-50"
              }`}
            >
              <Monitor className="w-3.5 h-3.5" />
              <span>16:9 Khung Ngang (YouTube / TV)</span>
            </button>

            <button
              type="button"
              onClick={() => setAspectRatio("9:16")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition ${
                aspectRatio === "9:16"
                  ? "bg-amber-50 border-amber-500 text-amber-900 font-bold"
                  : "border-slate-200 text-slate-600 hover:bg-slate-50"
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span>9:16 Khung Dọc (Shorts / Reels)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Storyboard Presentation */}
      {storyboard && (
        <div className="space-y-6">
          {/* Header Summary Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-100 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 uppercase">
                    Tỷ Lệ {storyboard.aspect_ratio || aspectRatio}
                  </span>
                  <span className="text-xs text-slate-500 font-medium">
                    {storyboard.total_scenes} Phân cảnh • {storyboard.total_duration_seconds}s
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mt-1">
                  {storyboard.script_title}
                </h3>
              </div>

              <div className="flex items-center gap-2">
                {onNavigateToVideo && (
                  <button
                    onClick={onNavigateToVideo}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-amber-700 hover:bg-amber-800 rounded-lg shadow-sm transition"
                  >
                    <Video className="w-3.5 h-3.5" />
                    <span>Dựng Video Này</span>
                  </button>
                )}
                <button
                  onClick={handleExportMarkdown}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  Markdown
                </button>
                <button
                  onClick={handleExportJson}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  JSON
                </button>
              </div>
            </div>

            {/* Visual Theme Directive */}
            <div className="p-4 bg-amber-50/40 rounded-xl border border-amber-200/60 text-xs">
              <span className="font-bold text-amber-900 uppercase tracking-wider text-[10px] block mb-1">
                Định Hướng Phong Cách Thị Giác Hoạt Họa (Visual Art Direction):
              </span>
              <p className="text-slate-800 leading-relaxed font-serif">
                "{storyboard.visual_theme}"
              </p>
            </div>
          </div>

          {/* Scenes Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {storyboard.scenes.map((scene) => {
              const isEditing = editingSceneNum === scene.scene_number;
              return (
                <div
                  key={scene.scene_number}
                  className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4 flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                      <span className="font-bold text-slate-900 text-xs">
                        Cảnh {scene.scene_number}: {scene.title}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-semibold text-[10px]">
                          ⏱️ {scene.estimated_duration_seconds}s
                        </span>
                        {!isEditing && (
                          <button
                            onClick={() => handleStartEdit(scene)}
                            className="p-1 text-slate-400 hover:text-amber-700 rounded transition"
                            title="Sửa prompt phân cảnh"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </div>

                    {isEditing ? (
                      <div className="p-3 bg-slate-50 rounded-xl border border-amber-300 space-y-2 text-xs">
                        <div>
                          <label className="text-[11px] text-slate-500 block mb-1">Mô tả trực quan:</label>
                          <textarea
                            rows={2}
                            value={editVisualDesc}
                            onChange={(e) => setEditVisualDesc(e.target.value)}
                            className="w-full p-2 border border-slate-300 rounded text-xs"
                          />
                        </div>
                        <div>
                          <label className="text-[11px] text-slate-500 block mb-1">AI Image Prompt:</label>
                          <textarea
                            rows={3}
                            value={editPrompt}
                            onChange={(e) => setEditPrompt(e.target.value)}
                            className="w-full p-2 border border-slate-300 rounded text-xs"
                          />
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleSaveScene(scene.scene_number)}
                            disabled={savingScene}
                            className="px-3 py-1 bg-amber-600 text-white rounded text-xs font-semibold"
                          >
                            {savingScene ? "Lưu..." : "Lưu"}
                          </button>
                          <button
                            onClick={() => setEditingSceneNum(null)}
                            className="px-3 py-1 border border-slate-300 rounded text-xs text-slate-600"
                          >
                            Hủy
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        {/* Setting & Direction */}
                        <div className="grid grid-cols-2 gap-2 text-[11px]">
                          <div className="p-2 bg-slate-50 rounded-lg">
                            <span className="text-slate-500 block">Bối cảnh lịch sử:</span>
                            <span className="font-semibold text-slate-800">{scene.historical_setting}</span>
                          </div>
                          <div className="p-2 bg-slate-50 rounded-lg">
                            <span className="text-slate-500 block">Góc máy:</span>
                            <span className="font-semibold text-slate-800">{scene.camera_direction}</span>
                          </div>
                        </div>

                        {/* Visual Description */}
                        <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1">
                          <span className="font-bold text-slate-600 text-[10px] uppercase block">
                            Bố Cục Cảnh 2D:
                          </span>
                          <p className="text-slate-700 leading-relaxed">
                            {scene.visual_description}
                          </p>
                        </div>

                        {/* AI Image Prompt */}
                        <div className="p-3 bg-amber-50/60 border border-amber-200/70 rounded-xl text-xs space-y-1 relative group">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-amber-900 text-[10px] uppercase block">
                              AI Image Prompt (Midjourney / DALL-E / Gemini):
                            </span>
                            <button
                              onClick={() => copyPrompt(scene.ai_image_prompt, scene.scene_number)}
                              className="text-amber-800 hover:text-amber-950 p-1 transition"
                              title="Sao chép prompt"
                            >
                              {copiedIdx === scene.scene_number ? (
                                <Check className="w-3.5 h-3.5 text-emerald-600" />
                              ) : (
                                <Copy className="w-3.5 h-3.5" />
                              )}
                            </button>
                          </div>
                          <p className="text-slate-800 font-mono text-[11px] leading-relaxed select-all">
                            {scene.ai_image_prompt}
                          </p>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Citations */}
                  {scene.evidence_references && scene.evidence_references.length > 0 && (
                    <div className="pt-2 border-t border-slate-100 flex items-center gap-1.5 text-[11px] text-emerald-800">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span className="truncate">
                        Bảo chứng: {scene.evidence_references[0].filename} (Trang {scene.evidence_references[0].page})
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
