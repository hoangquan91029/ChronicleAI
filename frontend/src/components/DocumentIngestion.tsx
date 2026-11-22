"use client";

import React, { useState, useEffect } from "react";
import { Upload, FileText, AlertTriangle, CheckCircle, Database, Eye } from "lucide-react";

interface Chunk {
  chunk_id: string;
  page: number;
  text: string;
  source: string;
  word_count: number;
}

interface DocMetadata {
  title?: string;
  total_pages: number;
  file_size_bytes: number;
  is_scanned: boolean;
  ocr_required: boolean;
  warning_message?: string;
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

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-amber-600" />
              Nạp Tư Liệu Lịch Sử (PDF Ingestion)
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Trích xuất văn bản tiếng Việt bằng PyMuPDF, bảo toàn tuyệt đối số trang gốc, phát hiện tài liệu scan (OCR).
            </p>
          </div>

          <div className="flex items-center gap-3">
            <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-lg shadow-sm transition">
              <Upload className="w-4 h-4" />
              {uploading ? "Đang xử lý PDF..." : "Tải lên PDF Mới"}
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
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            {errorMsg}
          </div>
        )}
      </div>

      {/* Document Selector & Metadata */}
      {selectedDoc && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
            <h3 className="font-semibold text-slate-800 text-sm flex items-center gap-2">
              <Database className="w-4 h-4 text-slate-500" />
              Thông Tin Văn Bản Trích Xuất
            </h3>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between border-b pb-2">
                <span className="text-slate-500">Tên tệp:</span>
                <span className="font-medium text-slate-900 truncate max-w-[180px]">
                  {selectedDoc.filename}
                </span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-slate-500">Tổng số trang:</span>
                <span className="font-semibold text-slate-900">
                  {selectedDoc.total_pages} trang
                </span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-slate-500">Số đoạn (Chunks):</span>
                <span className="font-semibold text-slate-900">
                  {selectedDoc.total_chunks} đoạn
                </span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-slate-500">Dung lượng:</span>
                <span className="text-slate-700">
                  {(selectedDoc.metadata.file_size_bytes / 1024).toFixed(1)} KB
                </span>
              </div>
              <div className="flex justify-between items-center pt-1">
                <span className="text-slate-500">Trạng thái:</span>
                {selectedDoc.metadata.is_scanned ? (
                  <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-medium">
                    <AlertTriangle className="w-3 h-3" /> Cần OCR (Tài liệu quét)
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-medium">
                    <CheckCircle className="w-3 h-3" /> Sẵn sàng RAG
                  </span>
                )}
              </div>
            </div>

            {selectedDoc.metadata.warning_message && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 leading-relaxed">
                ⚠️ {selectedDoc.metadata.warning_message}
              </div>
            )}
          </div>

          {/* Chunk Inspector */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold text-slate-800 text-sm flex items-center gap-2">
                <Eye className="w-4 h-4 text-slate-500" />
                Kiểm Tra Các Đoạn Dữ Liệu & Số Trang Gốc ({selectedDoc.chunks.length})
              </h3>
              <span className="text-xs text-slate-500">
                Bảo toàn 100% định danh trang & ID đoạn
              </span>
            </div>

            <div className="max-h-[380px] overflow-y-auto space-y-3 pr-1">
              {selectedDoc.chunks.map((chunk, idx) => (
                <div
                  key={chunk.chunk_id || idx}
                  className="p-3.5 bg-slate-50 hover:bg-slate-100/80 rounded-lg border border-slate-200 text-xs transition"
                >
                  <div className="flex justify-between items-center mb-1.5 text-slate-500 font-mono">
                    <span className="px-2 py-0.5 bg-amber-100 text-amber-900 font-semibold rounded">
                      Trang {chunk.page}
                    </span>
                    <span className="text-[11px] text-slate-400">
                      ID: {chunk.chunk_id} • {chunk.word_count} từ
                    </span>
                  </div>
                  <p className="text-slate-800 whitespace-pre-line leading-relaxed">
                    {chunk.text}
                  </p>
                </div>
              ))}

              {selectedDoc.chunks.length === 0 && (
                <div className="p-8 text-center text-slate-400 text-sm">
                  Không có đoạn văn bản trích xuất được (Tài liệu trống hoặc bản scan cần OCR).
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
