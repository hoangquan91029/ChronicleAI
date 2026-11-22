"use client";

import React, { useState } from "react";
import { Film, Clock, BookOpen, AlertCircle, Download, Sparkles, MessageSquareQuote } from "lucide-react";

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
}

export default function ScriptStudio({
  onScriptGenerated
}: {
  onScriptGenerated?: (script: VideoScript) => void;
}) {
  const [subject, setSubject] = useState("Hoàng đế Lê Thánh Tông (1460–1497)");
  const [targetMinutes, setTargetMinutes] = useState(16);
  const [loading, setLoading] = useState(false);
  const [script, setScript] = useState<VideoScript | null>(null);

  const handleGenerateScript = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/scripts/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject: subject,
          target_minutes: targetMinutes,
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
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
              <Film className="w-5 h-5 text-amber-600" />
              Xưởng Biên Kịch Lịch Sử (Scriptwriting Agent)
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Tạo kịch bản video giáo dục chuẩn 15–20 phút, gắn trích dẫn bảo chứng và phân định rõ hội thoại hư cấu.
            </p>
          </div>

          <button
            onClick={handleGenerateScript}
            disabled={loading}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-lg shadow-sm transition disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            {loading ? "Đang kiến tạo kịch bản..." : "Tạo Kịch Bản Mới"}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Chủ đề nghiên cứu lịch sử:
            </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Thời lượng mục tiêu: {targetMinutes} phút ({targetMinutes * 60} giây)
            </label>
            <input
              type="range"
              min={12}
              max={22}
              step={1}
              value={targetMinutes}
              onChange={(e) => setTargetMinutes(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-600 mt-2"
            />
          </div>
        </div>
      </div>

      {/* Script Content Viewer */}
      {script && (
        <div className="space-y-6">
          {/* Header Stats */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <span className="text-xs font-semibold text-amber-700 uppercase tracking-wider">
                Kịch Bản Video Giáo Dục
              </span>
              <h3 className="text-xl font-bold text-slate-900 mt-0.5">{script.title}</h3>
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 mt-2">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400" />
                  {script.target_duration_minutes} phút ({script.total_estimated_duration_seconds}s)
                </span>
                <span>•</span>
                <span>{script.total_scenes} Phân cảnh</span>
                <span>•</span>
                <span className="text-emerald-700 font-medium">
                  {script.verified_claims_count} Trích dẫn chứng thực
                </span>
                {script.flagged_for_review_count > 0 && (
                  <>
                    <span>•</span>
                    <span className="text-amber-700 font-medium">
                      ⚠️ {script.flagged_for_review_count} Cần duyệt lại
                    </span>
                  </>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleExportMarkdown}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium rounded-lg transition"
              >
                <Download className="w-3.5 h-3.5 text-slate-600" />
                Xuất Markdown (.md)
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

          {/* Hook & Background Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-amber-50/60 rounded-xl border border-amber-200/80 p-5 shadow-xs">
              <h4 className="text-xs font-bold text-amber-900 uppercase tracking-wider mb-2">
                🎬 Mở Đầu Thu Hút (Opening Hook)
              </h4>
              <p className="text-sm text-slate-800 leading-relaxed italic">
                "{script.hook}"
              </p>
            </div>

            <div className="bg-slate-50 rounded-xl border border-slate-200 p-5 shadow-xs">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                📜 Bối Cảnh Lịch Sử (Context)
              </h4>
              <p className="text-sm text-slate-800 leading-relaxed">
                {script.background_summary}
              </p>
            </div>
          </div>

          {/* Scene Breakdown */}
          <div className="space-y-4">
            <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
              Chi Tiết Các Phân Cảnh (Scenes)
            </h4>

            {script.scenes.map((scene) => (
              <div
                key={scene.scene_number}
                className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4 hover:border-amber-300 transition"
              >
                <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 border-b border-slate-100 pb-3">
                  <div className="flex items-center gap-2.5">
                    <span className="w-7 h-7 rounded-full bg-amber-600 text-white font-bold text-xs flex items-center justify-center">
                      {scene.scene_number}
                    </span>
                    <h5 className="font-semibold text-slate-900 text-base">{scene.title}</h5>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="px-2 py-0.5 bg-slate-100 text-slate-700 rounded font-mono">
                      {scene.scene_type}
                    </span>
                    <span className="px-2 py-0.5 bg-amber-100 text-amber-900 rounded font-semibold">
                      {scene.estimated_duration_seconds}s
                    </span>
                  </div>
                </div>

                <div className="text-xs text-slate-500 italic">
                  📍 Bối cảnh: {scene.historical_setting}
                </div>

                {/* Narration */}
                <div className="text-sm text-slate-800 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100">
                  <span className="font-semibold text-slate-700 block mb-1">Lời bình (Voiceover):</span>
                  {scene.narration}
                </div>

                {/* Dialogues */}
                {scene.dialogues.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-xs font-semibold text-slate-600 flex items-center gap-1.5">
                      <MessageSquareQuote className="w-3.5 h-3.5 text-amber-600" />
                      Hội Thoại Nhân Vật:
                    </span>
                    <div className="space-y-2">
                      {scene.dialogues.map((d, dIdx) => (
                        <div
                          key={dIdx}
                          className="flex items-start gap-2 p-3 rounded-lg border border-slate-200 text-xs bg-white"
                        >
                          <span
                            className={`px-2 py-0.5 rounded font-semibold whitespace-nowrap text-[11px] ${
                              d.is_fictional
                                ? "bg-purple-100 text-purple-900"
                                : "bg-emerald-100 text-emerald-900"
                            }`}
                          >
                            {d.is_fictional ? "[HƯ CẤU NGHỆ THUẬT]" : "[CHÍNH SỬ]"}
                          </span>
                          <div>
                            <span className="font-bold text-slate-900">{d.speaker}: </span>
                            <span className="text-slate-800 italic">"{d.text}"</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Citations */}
                {scene.citations.length > 0 && (
                  <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-xs">
                    <span className="font-semibold text-slate-500">Bảo chứng:</span>
                    {scene.citations.map((c, cIdx) => (
                      <span
                        key={cIdx}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-amber-50 text-amber-900 border border-amber-200/80 rounded font-mono text-[11px]"
                      >
                        <BookOpen className="w-3 h-3 text-amber-600" />
                        {c.filename} (Trang {c.page})
                      </span>
                    ))}
                  </div>
                )}

                {/* Needs Review Flag */}
                {scene.needs_review && (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                    <span>⚠️ {scene.review_notes || "Cần chuyên gia sử học thẩm định lại."}</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Conclusion */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-2">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              🏆 Kết Luận & Ý Nghĩa Lịch Sử
            </h4>
            <p className="text-sm text-slate-800 leading-relaxed italic bg-slate-50 p-4 rounded-lg">
              "{script.conclusion}"
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
