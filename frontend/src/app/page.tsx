"use client";

import React, { useState } from "react";
import {
  FileText,
  Search,
  ShieldCheck,
  Film,
  Layout,
  Crown,
  BookOpen,
  Sparkles,
  GitBranch
} from "lucide-react";

import DocumentIngestion from "../components/DocumentIngestion";
import EvidenceExplorer from "../components/EvidenceExplorer";
import ClaimVerifier from "../components/ClaimVerifier";
import ScriptStudio from "../components/ScriptStudio";
import StoryboardViewer from "../components/StoryboardViewer";

type TabType = "ingest" | "rag" | "verify" | "script" | "storyboard";

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>("ingest");
  const [currentDocName, setCurrentDocName] = useState<string>("le_thanh_tong_dai_viet.pdf");

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-700 to-amber-500 flex items-center justify-center text-white shadow-sm shadow-amber-500/20">
              <Crown className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">ChronicleAI</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 tracking-wide uppercase">
                  v1.0 MVP
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Nền tảng Nghiên cứu Lịch sử & Sản xuất Video Giáo dục AI
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-amber-50 rounded-lg border border-amber-200/80 text-xs text-amber-900">
              <BookOpen className="w-3.5 h-3.5 text-amber-600" />
              <span>Chuyên đề 1: <strong>Lê Thánh Tông (1460–1497)</strong></span>
            </div>

            <a
              href="https://github.com/hoangquan91029/ChronicleAI"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-lg border border-slate-200 transition"
            >
              <GitBranch className="w-4 h-4" />
              <span>Mã Nguồn Mở</span>
            </a>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex overflow-x-auto gap-1 border-t border-slate-100">
          <button
            onClick={() => setActiveTab("ingest")}
            className={`flex items-center gap-2 py-3 px-3.5 border-b-2 text-xs font-semibold whitespace-nowrap transition ${
              activeTab === "ingest"
                ? "border-amber-600 text-amber-700"
                : "border-transparent text-slate-600 hover:text-slate-900"
            }`}
          >
            <FileText className="w-4 h-4" />
            1. Xử Lý PDF & Phân Đoạn (Milestone 1)
          </button>

          <button
            onClick={() => setActiveTab("rag")}
            className={`flex items-center gap-2 py-3 px-3.5 border-b-2 text-xs font-semibold whitespace-nowrap transition ${
              activeTab === "rag"
                ? "border-amber-600 text-amber-700"
                : "border-transparent text-slate-600 hover:text-slate-900"
            }`}
          >
            <Search className="w-4 h-4" />
            2. Tra Cứu Chứng Cứ RAG (Milestone 2)
          </button>

          <button
            onClick={() => setActiveTab("verify")}
            className={`flex items-center gap-2 py-3 px-3.5 border-b-2 text-xs font-semibold whitespace-nowrap transition ${
              activeTab === "verify"
                ? "border-amber-600 text-amber-700"
                : "border-transparent text-slate-600 hover:text-slate-900"
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            3. Thẩm Định Tuyên Bố Lịch Sử
          </button>

          <button
            onClick={() => setActiveTab("script")}
            className={`flex items-center gap-2 py-3 px-3.5 border-b-2 text-xs font-semibold whitespace-nowrap transition ${
              activeTab === "script"
                ? "border-amber-600 text-amber-700"
                : "border-transparent text-slate-600 hover:text-slate-900"
            }`}
          >
            <Film className="w-4 h-4" />
            4. Xưởng Biên Kịch (Milestone 3)
          </button>

          <button
            onClick={() => setActiveTab("storyboard")}
            className={`flex items-center gap-2 py-3 px-3.5 border-b-2 text-xs font-semibold whitespace-nowrap transition ${
              activeTab === "storyboard"
                ? "border-amber-600 text-amber-700"
                : "border-transparent text-slate-600 hover:text-slate-900"
            }`}
          >
            <Layout className="w-4 h-4" />
            5. Phân Cảnh Hoạt Họa 2D (Milestone 4)
          </button>
        </div>
      </header>

      {/* Main Body */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-6">
        {/* Banner */}
        <div className="bg-gradient-to-r from-amber-900 via-amber-800 to-amber-950 text-white rounded-2xl p-6 sm:p-8 shadow-md">
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-200 border border-amber-400/30">
              <Sparkles className="w-3.5 h-3.5" />
              Đại Việt Sử Ký Toàn Thư & Quốc Triều Hình Luật
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Khảo Cứu & Chuyển Hóa Sử Liệu Hoàng Đế Lê Thánh Tông
            </h1>
            <p className="text-amber-100/90 text-sm leading-relaxed">
              Quy trình khép kín: <strong>Tải lên PDF → Trích xuất & Bảo toàn số trang → Nhúng đa ngữ → Truy xuất RAG → Thẩm định tuyên bố (Supported / Contradicted / Insufficient Evidence) → Kịch bản 15–20 phút → Storyboard hoạt họa 2D tối giản</strong>.
            </p>
          </div>
        </div>

        {/* Tab Content Panels */}
        {activeTab === "ingest" && (
          <DocumentIngestion
            onDocumentLoaded={(doc) => setCurrentDocName(doc.filename)}
          />
        )}
        {activeTab === "rag" && <EvidenceExplorer />}
        {activeTab === "verify" && <ClaimVerifier />}
        {activeTab === "script" && <ScriptStudio />}
        {activeTab === "storyboard" && <StoryboardViewer />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 mt-12 text-center text-xs text-slate-500 space-y-1">
        <p>
          <strong>ChronicleAI</strong> — Nền tảng Nguồn mở Kiến tạo Video Lịch sử Chứng thực.
        </p>
        <p className="text-slate-400">
          Xây dựng bằng FastAPI, PyMuPDF, RAG Multilingual, Next.js & Tailwind CSS. Thẩm định cho Devin Software Engineering Challenge.
        </p>
      </footer>
    </div>
  );
}
