"use client";

import React, { useState } from "react";
import { Search, BookOpen, Quote, ShieldCheck, Compass } from "lucide-react";

interface Citation {
  filename: string;
  page: number;
  chunk_id: string;
  quote: string;
  score: number;
}

interface SearchResult {
  chunk_id: string;
  page: number;
  text: string;
  source: string;
  score: number;
  citation: Citation;
}

export default function EvidenceExplorer() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<"search" | "qa">("qa");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [qaAnswer, setQaAnswer] = useState<string | null>(null);
  const [qaCitations, setQaCitations] = useState<Citation[]>([]);

  const handleSearch = async (customQuery?: string) => {
    const q = (customQuery || query).trim();
    if (!q) return;

    setLoading(true);
    setQaAnswer(null);
    setQaCitations([]);

    try {
      if (mode === "search") {
        const res = await fetch("/api/rag/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: q, top_k: 4 }),
        });
        const data = await res.json();
        setResults(data.results || []);
      } else {
        const res = await fetch("/api/rag/answer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: q, top_k: 4 }),
        });
        const data = await res.json();
        setQaAnswer(data.answer);
        setQaCitations(data.citations || []);
        setResults(data.retrieved_chunks || []);
      }
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const sampleQueries = [
    "Quyền lợi của phụ nữ trong Bộ luật Hồng Đức được quy định thế nào?",
    "Ai là tác giả câu nói Hiền tài là nguyên khí quốc gia?",
    "Lời răn dạy của Lê Thánh Tông về việc bảo vệ chủ quyền biên cương?",
    "Cải cách hành chính 13 đạo thừa tuyên và cơ chế Tam ty",
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
              <Compass className="w-5 h-5 text-amber-600" />
              Tra Cứu & Đối Soát Bằng Chứng (RAG Evidence Explorer)
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Tìm kiếm ngữ nghĩa đa ngôn ngữ kết hợp trích dẫn số trang chính xác và Q&A chứng thực.
            </p>
          </div>

          <div className="flex bg-slate-100 p-1 rounded-lg self-start sm:self-auto">
            <button
              onClick={() => setMode("qa")}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition ${
                mode === "qa"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Hỏi Đáp Bảo Chứng (Grounded Q&A)
            </button>
            <button
              onClick={() => setMode("search")}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition ${
                mode === "search"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Truy Xuất Đoạn (Raw Chunks)
            </button>
          </div>
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              placeholder={
                mode === "qa"
                  ? "Đặt câu hỏi lịch sử cần giải đáp dựa trên nguồn tư liệu..."
                  : "Nhập từ khóa tìm kiếm chứng cứ lịch sử..."
              }
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 transition"
            />
          </div>
          <button
            onClick={() => handleSearch()}
            disabled={loading}
            className="px-5 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-lg shadow-sm transition disabled:opacity-50"
          >
            {loading ? "Đang truy vấn..." : "Truy Vấn"}
          </button>
        </div>

        {/* Quick Sample Queries */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
          <span className="text-slate-400 font-medium">Gợi ý câu hỏi:</span>
          {sampleQueries.map((q, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(q);
                handleSearch(q);
              }}
              className="px-2.5 py-1 bg-slate-100 hover:bg-amber-50 hover:text-amber-800 border border-slate-200/80 rounded-md text-slate-600 transition truncate max-w-[280px]"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Q&A Grounded Answer Box */}
      {qaAnswer && (
        <div className="bg-gradient-to-br from-amber-50/60 to-white rounded-xl border border-amber-200/80 p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-amber-900 font-semibold text-sm">
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
            Câu Trả Lời Được Bảo Chứng Bằng Tư Liệu Lịch Sử
          </div>

          <div className="text-sm text-slate-800 leading-relaxed whitespace-pre-line bg-white/80 p-4 rounded-lg border border-amber-100">
            {qaAnswer}
          </div>

          {qaCitations.length > 0 && (
            <div className="space-y-2 pt-1">
              <span className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
                Trích Dẫn Gốc Có Thể Đối Soát:
              </span>
              <div className="flex flex-wrap gap-2">
                {qaCitations.map((cit, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 p-2 bg-white rounded-md border border-slate-200 text-xs shadow-xs"
                  >
                    <BookOpen className="w-3.5 h-3.5 text-amber-600" />
                    <span className="font-semibold text-slate-800">{cit.filename}</span>
                    <span className="px-1.5 py-0.5 bg-amber-100 text-amber-900 rounded font-medium">
                      Trang {cit.page}
                    </span>
                    <span className="text-slate-400 font-mono text-[10px]">({cit.chunk_id})</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Retrieved Chunks */}
      {results.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <Quote className="w-4 h-4 text-slate-500" />
            Đoạn Tư Liệu Khớp ({results.length})
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {results.map((res, idx) => (
              <div
                key={idx}
                className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:border-amber-300 transition space-y-2.5 text-xs"
              >
                <div className="flex justify-between items-center text-slate-500">
                  <span className="px-2 py-0.5 bg-amber-100 text-amber-900 rounded font-semibold">
                    Trang {res.page}
                  </span>
                  <span className="font-mono text-slate-400">
                    Độ tương đồng: {(res.score * 100).toFixed(1)}%
                  </span>
                </div>

                <p className="text-slate-800 leading-relaxed line-clamp-5">
                  {res.text}
                </p>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                  <span className="truncate max-w-[200px]">{res.source}</span>
                  <span className="font-mono">{res.chunk_id}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
