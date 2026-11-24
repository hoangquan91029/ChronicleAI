"use client";

import React, { useState, useEffect } from "react";
import {
  Upload,
  FileText,
  AlertTriangle,
  CheckCircle,
  Database,
  Eye,
  Trash2,
  Globe,
  Plus,
  BookOpen,
  Sparkles,
  ShieldCheck
} from "lucide-react";

interface Chunk {
  chunk_id: string;
  page: number;
  text: string;
  source: string;
  word_count: number;
  folio_ref?: string;
  original_url?: string;
}

interface DocMetadata {
  title?: string;
  total_pages: number;
  file_size_bytes: number;
  is_scanned: boolean;
  ocr_required: boolean;
  warning_message?: string;
  extra?: Record<string, any>;
}

interface IngestResponse {
  document_id: string;
  filename: string;
  total_pages: number;
  total_chunks: number;
  status: string;
  metadata: DocMetadata;
  chunks: Chunk[];
}

export default function DocumentIngestion({
  onDocumentLoaded
}: {
  onDocumentLoaded?: (doc: IngestResponse) => void;
}) {
  const [documents, setDocuments] = useState<IngestResponse[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<IngestResponse | null>(null);
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [showUrlModal, setShowUrlModal] = useState(false);
  const [registeringUrl, setRegisteringUrl] = useState(false);

  // URL registration form states
  const [urlInput, setUrlInput] = useState("");
  const [urlTitle, setUrlTitle] = useState("");
  const [urlFolioRef, setUrlFolioRef] = useState("");
  const [urlSampleText, setUrlSampleText] = useState("");

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await fetch("/api/documents");
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
        if (data.length > 0 && !selectedDoc) {
          setSelectedDoc(data[0]);
          if (onDocumentLoaded) onDocumentLoaded(data[0]);
        }
      }
    } catch (err) {
      console.error("Error fetching documents:", err);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 25 * 1024 * 1024) {
      setErrorMsg("Kích thước tệp vượt quá giới hạn 25MB cho phép.");
      return;
    }

    setUploading(true);
    setErrorMsg(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Tải lên thất bại");
      }

      const doc = await res.json();
      setDocuments((prev) => [doc, ...prev]);
      setSelectedDoc(doc);
      if (onDocumentLoaded) onDocumentLoaded(doc);
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleRegisterUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput || !urlTitle) return;

    setRegisteringUrl(true);
    setErrorMsg(null);

    try {
      const res = await fetch("/api/documents/register-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: urlInput,
          title: urlTitle,
          folio_ref: urlFolioRef || undefined,
          sample_content: urlSampleText || undefined
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Đăng ký URL thất bại");
      }

      const newDoc = await res.json();
      setDocuments((prev) => [newDoc, ...prev]);
      setSelectedDoc(newDoc);
      setShowUrlModal(false);
      setUrlInput("");
      setUrlTitle("");
      setUrlFolioRef("");
      setUrlSampleText("");
      if (onDocumentLoaded) onDocumentLoaded(newDoc);
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setRegisteringUrl(false);
    }
  };

  const handleDeleteDocument = async (docId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Bạn có chắc chắn muốn xóa tài liệu này khỏi cơ sở dữ liệu và vector index?")) return;

    try {
      const res = await fetch(`/api/documents/${docId}`, { method: "DELETE" });
      if (res.ok) {
        setDocuments((prev) => prev.filter((d) => d.document_id !== docId));
        if (selectedDoc?.document_id === docId) {
          const remaining = documents.filter((d) => d.document_id !== docId);
          setSelectedDoc(remaining.length > 0 ? remaining[0] : null);
        }
      } else {
        const err = await res.json();
        alert(err.detail || "Xóa tài liệu thất bại");
      }
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Zone & Action Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-amber-600" />
              Nạp & Quản Lý Tư Liệu Lịch Sử (Document Ingestion & Registry)
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Hỗ trợ tệp PDF học thuật (PyMuPDF, bảo toàn số trang gốc, phát hiện bản scan OCR, giới hạn 25MB) và Thư tịch số hóa trực tuyến (URL Archive).
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowUrlModal(true)}
              className="inline-flex items-center gap-2 px-3.5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-xs rounded-xl border border-slate-300 transition"
            >
              <Globe className="w-4 h-4 text-amber-700" />
              <span>Đăng Ký URL Thư Tịch</span>
            </button>

            <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-amber-700 to-amber-600 hover:from-amber-800 hover:to-amber-700 text-white font-semibold text-xs rounded-xl shadow-sm transition">
              <Upload className="w-4 h-4" />
              {uploading ? "Đang xử lý PDF..." : "Tải lên PDF (≤25MB)"}
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                disabled={uploading}
                onChange={handleFileUpload}
              />
            </label>
          </div>
        </div>

        {errorMsg && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* URL Registration Modal */}
      {showUrlModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Globe className="w-4 h-4 text-amber-600" />
                Đăng Ký Nguồn Thư Tịch Số Hóa (URL Source)
              </h3>
              <button
                onClick={() => setShowUrlModal(false)}
                className="text-slate-400 hover:text-slate-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleRegisterUrl} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Đường dẫn URL Thư tịch / Văn khố số:
                </label>
                <input
                  type="url"
                  required
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://nlv.gov.vn/digital-collections/..."
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Tiêu đề tài liệu / Hồ sơ:
                </label>
                <input
                  type="text"
                  required
                  value={urlTitle}
                  onChange={(e) => setUrlTitle(e.target.value)}
                  placeholder="Đại Việt Sử Ký Toàn Thư (Bản Kỷ Thực Lục)..."
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Ký hiệu tờ / Quyển (Folio ref - tùy chọn):
                </label>
                <input
                  type="text"
                  value={urlFolioRef}
                  onChange={(e) => setUrlFolioRef(e.target.value)}
                  placeholder="Quyển XII, Tờ 8a..."
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Nội dung trích lục / Khảo dịch (Text Transcript):
                </label>
                <textarea
                  rows={4}
                  value={urlSampleText}
                  onChange={(e) => setUrlSampleText(e.target.value)}
                  placeholder="Dán nội dung khảo cứu hoặc trích lục sử liệu tại đây..."
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-amber-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowUrlModal(false)}
                  className="px-3.5 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 font-medium"
                >
                  Hủy Bỏ
                </button>
                <button
                  type="submit"
                  disabled={registeringUrl}
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold shadow-sm transition"
                >
                  {registeringUrl ? "Đang lưu..." : "Xác Nhận Đăng Ký"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Document Library Horizontal Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-amber-600" />
            Thư Viện Sử Liệu Đã Nạp ({documents.length} tài liệu)
          </h3>
          <span className="text-[11px] text-slate-400">
            Lưu trữ bền vững trong SQLite (chronicle.db)
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {documents.map((doc) => {
            const isSelected = selectedDoc?.document_id === doc.document_id;
            return (
              <div
                key={doc.document_id}
                onClick={() => {
                  setSelectedDoc(doc);
                  if (onDocumentLoaded) onDocumentLoaded(doc);
                }}
                className={`p-3.5 rounded-xl border cursor-pointer text-xs transition relative group ${
                  isSelected
                    ? "bg-amber-50/70 border-amber-500 shadow-xs ring-1 ring-amber-500"
                    : "bg-slate-50/50 border-slate-200 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="truncate font-bold text-slate-900">
                    {doc.filename}
                  </div>
                  <button
                    onClick={(e) => handleDeleteDocument(doc.document_id, e)}
                    className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-600 transition p-1"
                    title="Xóa tài liệu này"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="flex items-center gap-2 mt-2 text-[11px] text-slate-500">
                  <span>{doc.total_pages} trang</span>
                  <span>•</span>
                  <span>{doc.total_chunks} đoạn</span>
                  <span>•</span>
                  <span className="font-medium text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">
                    {doc.status}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Document Details & Chunks Inspector */}
      {selectedDoc && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-2">
              <Database className="w-4 h-4 text-slate-500" />
              Chi Tiết Kỹ Thuật Hồ Sơ
            </h3>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between border-b pb-2">
                <span className="text-slate-500">ID Tài liệu:</span>
                <span className="font-mono font-medium text-slate-800 text-[11px]">
                  {selectedDoc.document_id}
                </span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-slate-500">Tên nguồn:</span>
                <span className="font-semibold text-slate-900 truncate max-w-[180px]">
                  {selectedDoc.filename}
                </span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-slate-500">Số trang gốc:</span>
                <span className="font-bold text-slate-900">
                  {selectedDoc.total_pages} trang
                </span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-slate-500">Số đoạn (Chunks):</span>
                <span className="font-bold text-slate-900">
                  {selectedDoc.total_chunks} đoạn
                </span>
              </div>
              <div className="flex justify-between items-center pt-1">
                <span className="text-slate-500">Thẩm định OCR:</span>
                {selectedDoc.metadata.is_scanned ? (
                  <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 font-bold">
                    <AlertTriangle className="w-3 h-3" /> Cần OCR
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-900 font-bold">
                    <CheckCircle className="w-3 h-3" /> Đã Lập Chỉ Mục RAG
                  </span>
                )}
              </div>
            </div>

            {selectedDoc.metadata.warning_message && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 leading-relaxed">
                ⚠️ {selectedDoc.metadata.warning_message}
              </div>
            )}
          </div>

          {/* Chunk Inspector */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-2">
                <Eye className="w-4 h-4 text-slate-500" />
                Kiểm Tra Các Đoạn Dữ Liệu & Số Trang Gốc ({selectedDoc.chunks.length})
              </h3>
              <span className="text-[11px] text-slate-500 font-medium">
                Bảo toàn 100% định danh trang & ID đoạn
              </span>
            </div>

            <div className="max-h-[420px] overflow-y-auto space-y-3 pr-1">
              {selectedDoc.chunks.map((chunk, idx) => (
                <div
                  key={chunk.chunk_id || idx}
                  className="p-3.5 bg-slate-50/70 hover:bg-slate-100/80 rounded-xl border border-slate-200/80 text-xs transition"
                >
                  <div className="flex justify-between items-center mb-1.5 font-mono">
                    <span className="px-2 py-0.5 bg-amber-100 text-amber-900 font-bold rounded">
                      {chunk.folio_ref ? `Tờ ${chunk.folio_ref} (Quyển ${chunk.page})` : `Trang ${chunk.page}`}
                    </span>
                    <span className="text-[10px] text-slate-400">
                      ID: {chunk.chunk_id} • {chunk.word_count} từ
                    </span>
                  </div>
                  <p className="text-slate-800 whitespace-pre-line leading-relaxed">
                    {chunk.text}
                  </p>
                </div>
              ))}

              {selectedDoc.chunks.length === 0 && (
                <div className="p-8 text-center text-slate-400 text-xs">
                  Không có đoạn văn bản trích xuất được.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
