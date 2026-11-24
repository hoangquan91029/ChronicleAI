"use client";

import React, { useState } from "react";
import {
  Film,
  Clock,
  BookOpen,
  AlertCircle,
  Download,
  Sparkles,
  MessageSquareQuote,
  Edit3,
  Check,
  X,
  ShieldCheck,
  Zap
} from "lucide-react";

interface Citation {
  filename: string;
  page: number;
  chunk_id: string;
  quote: string;
  score: number;
}

interface DialogueLine {
  speaker: string;
  text: string;
  dialogue_type: "HISTORICAL_QUOTE" | "FICTIONAL_DRAMATIZATION" | "NARRATION";
  is_fictional: boolean;
  citation?: Citation;
}

interface ScriptScene {
  scene_number: number;
  title: string;
  scene_type: string;
  estimated_duration_seconds: number;
  historical_setting: string;
  narration: string;
  dialogues: DialogueLine[];
  key_historical_facts: string[];
  citations: Citation[];
  needs_review: boolean;
  review_notes?: string;
}

interface VideoScript {
  title: string;
  subject: string;
  format?: "SHORTS" | "EXPLAINER" | "DOCUMENTARY";
  target_duration_minutes: number;
  total_estimated_duration_seconds: number;
  hook: string;
  background_summary: string;
  scenes: ScriptScene[];
  conclusion: string;
  total_scenes: number;
  verified_claims_count: number;
  flagged_for_review_count: number;
  sources_consulted: string[];
  provider_diagnostics?: {
    provider_name: string;
    model: string;
    is_fallback: boolean;
    duration_ms: number;
  };
}

export default function ScriptStudio({
  onScriptGenerated
}: {
  onScriptGenerated?: (script: VideoScript) => void;
}) {
  const [subject, setSubject] = useState("Hoàng đế Lê Thánh Tông (1460–1497)");
  const [selectedFormat, setSelectedFormat] = useState<"SHORTS" | "EXPLAINER" | "DOCUMENTARY">("DOCUMENTARY");
  const [loading, setLoading] = useState(false);
  const [script, setScript] = useState<VideoScript | null>(null);

  // Scene editing state
  const [editingSceneNum, setEditingSceneNum] = useState<number | null>(null);
  const [editNarration, setEditNarration] = useState("");
  const [editDuration, setEditDuration] = useState(30);
  const [savingScene, setSavingScene] = useState(false);

  const handleGenerateScript = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/scripts/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject: subject,
          format: selectedFormat
        }),
      });

      if (!res.ok) throw new Error("Tạo kịch bản thất bại");
      const data = await res.json();
      setScript(data);
      if (onScriptGenerated) onScriptGenerated(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartEdit = (scene: ScriptScene) => {
    setEditingSceneNum(scene.scene_number);
    setEditNarration(scene.narration);
    setEditDuration(scene.estimated_duration_seconds);
  };

  const handleSaveScene = async (sceneNumber: number) => {
    setSavingScene(true);
    try {
      const res = await fetch(`/api/scripts/scenes/${sceneNumber}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          narration: editNarration,
          estimated_duration_seconds: editDuration
        })
      });

      if (res.ok) {
        const updated = await res.json();
        setScript(updated);
        setEditingSceneNum(null);
      } else {
        alert("Lưu phân cảnh thất bại");
      }
    } catch (err) {
      console.error("Save scene error:", err);
    } finally {
      setSavingScene(false);
    }
  };

  const handleExportMarkdown = async () => {
    if (!script) return;
    try {
      const res = await fetch("/api/scripts/export/markdown", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(script),
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "chronicle_script.md";
      a.click();
    } catch (err) {
      console.error("Export MD failed:", err);
    }
  };

  const handleExportJson = () => {
    if (!script) return;
    const blob = new Blob([JSON.stringify(script, null, 2)], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "chronicle_script.json";
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Control Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Film className="w-5 h-5 text-amber-600" />
              Xưởng Biên Kịch Sử Liệu (Scriptwriting Studio)
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Tạo kịch bản video giáo dục đa độ dài (Shorts 30–60s, Giải thích 3–5m, Phim tài liệu 10–20m), bảo chứng trích dẫn và phân định rõ đối thoại lịch sử vs hư cấu.
            </p>
          </div>

          <button
            onClick={handleGenerateScript}
            disabled={loading}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-amber-700 to-amber-600 hover:from-amber-800 hover:to-amber-700 text-white font-semibold text-xs rounded-xl shadow-sm transition disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            {loading ? "Đang biên soạn kịch bản..." : "Biên Soạn Kịch Bản Mới"}
          </button>
        </div>

        {/* Configuration Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Chủ đề nghiên cứu lịch sử:
            </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Định dạng video & Quy mô phân cảnh:
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
                Shorts (30–60s)
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
                Giải thích (3–5m)
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
                Tài liệu (10–20m)
              </button>
            </div>
          </div>
        </div>

        {/* Diagnostics Card if present */}
        {script?.provider_diagnostics && (
          <div className="pt-2">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between text-xs text-slate-600">
              <div className="flex items-center gap-2">
                <Zap className="w-3.5 h-3.5 text-amber-600" />
                <span>
                  Động cơ LLM: <strong>{script.provider_diagnostics.provider_name}</strong> ({script.provider_diagnostics.model})
                </span>
                {script.provider_diagnostics.is_fallback && (
                  <span className="px-1.5 py-0.5 rounded bg-slate-200 text-slate-700 text-[10px] font-semibold">
                    Quy tắc Ngoại Tuyến (Offline Deterministic)
                  </span>
                )}
              </div>
              <span className="text-[11px] text-slate-400">
                Thời gian xử lý: {script.provider_diagnostics.duration_ms}ms
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Script Presentation */}
      {script && (
        <div className="space-y-6">
          {/* Header Summary */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-100 pb-4">
              <div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 tracking-wide uppercase">
                  {script.format || selectedFormat}
                </span>
                <h3 className="text-xl font-bold text-slate-900 mt-1">
                  {script.title}
                </h3>
                <p className="text-xs text-slate-500">
                  Tổng thời lượng dự kiến: {script.total_estimated_duration_seconds}s (~{Math.round(script.total_estimated_duration_seconds / 60)} phút) • {script.total_scenes} Phân cảnh
                </p>
              </div>

              <div className="flex items-center gap-2">
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

            {/* Hook & Background */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 bg-amber-50/50 rounded-xl border border-amber-200/60 space-y-1">
                <span className="font-bold text-amber-900 uppercase tracking-wider text-[10px] block">
                  Lời Mở Đầu Thu Hút (Opening Hook)
                </span>
                <p className="text-slate-800 leading-relaxed font-medium">
                  {script.hook}
                </p>
              </div>

              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                <span className="font-bold text-slate-700 uppercase tracking-wider text-[10px] block">
                  Bối Cảnh & Đại Cục Lịch Sử
                </span>
                <p className="text-slate-700 leading-relaxed">
                  {script.background_summary}
                </p>
              </div>
            </div>
          </div>

          {/* Scenes Breakdown */}
          <div className="space-y-4">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-600" />
              Chi Tiết Từng Phân Cảnh ({script.scenes.length} cảnh)
            </h4>

            {script.scenes.map((scene) => {
              const isEditing = editingSceneNum === scene.scene_number;
              return (
                <div
                  key={scene.scene_number}
                  className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4"
                >
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-amber-700 text-white font-bold text-xs flex items-center justify-center">
                        {scene.scene_number}
                      </span>
                      <h5 className="font-bold text-slate-900 text-sm">
                        {scene.title}
                      </h5>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-600">
                        {scene.scene_type}
                      </span>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-xs font-semibold text-slate-500">
                        ⏱️ {scene.estimated_duration_seconds}s
                      </span>
                      {!isEditing && (
                        <button
                          onClick={() => handleStartEdit(scene)}
                          className="p-1.5 text-slate-400 hover:text-amber-700 rounded-lg hover:bg-slate-50 transition"
                          title="Chỉnh sửa cảnh này"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>

                  {isEditing ? (
                    <div className="p-4 bg-slate-50 rounded-xl border border-amber-300 space-y-3 text-xs">
                      <span className="font-bold text-slate-800 block">
                        Chỉnh sửa lời bình & thời lượng cảnh {scene.scene_number}:
                      </span>
                      <div>
                        <label className="text-[11px] text-slate-500 block mb-1">Lời bình (Narration):</label>
                        <textarea
                          rows={3}
                          value={editNarration}
                          onChange={(e) => setEditNarration(e.target.value)}
                          className="w-full p-2 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-amber-500"
                        />
                      </div>
                      <div>
                        <label className="text-[11px] text-slate-500 block mb-1">Thời lượng (giây):</label>
                        <input
                          type="number"
                          value={editDuration}
                          onChange={(e) => setEditDuration(parseInt(e.target.value) || 10)}
                          className="w-24 p-2 border border-slate-300 rounded-lg text-xs"
                        />
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleSaveScene(scene.scene_number)}
                          disabled={savingScene}
                          className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold flex items-center gap-1"
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>{savingScene ? "Đang lưu..." : "Lưu Thay Đổi"}</span>
                        </button>
                        <button
                          onClick={() => setEditingSceneNum(null)}
                          className="px-3 py-1.5 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-100 font-medium"
                        >
                          Hủy
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3 text-xs">
                      {/* Narration */}
                      <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                          Lời Bình Voiceover:
                        </span>
                        <p className="text-slate-800 leading-relaxed">
                          "{scene.narration}"
                        </p>
                      </div>

                      {/* Dialogues */}
                      {scene.dialogues && scene.dialogues.length > 0 && (
                        <div className="space-y-1.5">
                          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                            Hội Thoại & Phát Biểu Lịch Sử:
                          </span>
                          {scene.dialogues.map((dlg, dIdx) => (
                            <div
                              key={dIdx}
                              className={`p-2.5 rounded-lg border text-xs flex items-start gap-2 ${
                                dlg.is_fictional
                                  ? "bg-purple-50/60 border-purple-200 text-purple-950"
                                  : "bg-emerald-50/60 border-emerald-200 text-emerald-950"
                              }`}
                            >
                              <MessageSquareQuote className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                              <div className="space-y-0.5">
                                <span className="font-bold">{dlg.speaker}:</span>
                                <span> "{dlg.text}"</span>
                                <div className="text-[10px] opacity-75">
                                  {dlg.is_fictional ? "🎭 Tái hiện kịch tính (Hư cấu)" : "📜 Trích dẫn sử liệu nguyên bản"}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Citations */}
                      {scene.citations && scene.citations.length > 0 && (
                        <div className="pt-2 border-t border-slate-100 flex flex-wrap gap-2">
                          {scene.citations.map((c, cIdx) => (
                            <span
                              key={cIdx}
                              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-900 border border-emerald-200 text-[11px]"
                            >
                              <ShieldCheck className="w-3 h-3 text-emerald-600" />
                              <span>{c.filename} (Trang {c.page})</span>
                            </span>
                          ))}
                        </div>
                      )}
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
