"use client";

import React, { useState } from "react";
import { CheckCircle2, XCircle, HelpCircle, ShieldAlert, Sparkles, BookOpen } from "lucide-react";

interface Citation {
  filename: string;
  page: number;
  chunk_id: string;
  quote: string;
  score: number;
}

interface SingleClaimResult {
  claim: string;
  status: "SUPPORTED" | "CONTRADICTED" | "INSUFFICIENT_EVIDENCE";
  confidence: number;
  explanation: string;
  citations: Citation[];
}

interface VerificationResponse {
  total_claims: number;
  supported_count: number;
  contradicted_count: number;
  insufficient_evidence_count: number;
  results: SingleClaimResult[];
}

export default function ClaimVerifier() {
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<VerificationResponse | null>(null);

  const sampleClaims = [
    "Năm Canh Thìn 1460, hoàng tử Lê Tư Thành lên ngôi lấy niên hiệu Quang Thuận",
    "Bộ luật Hồng Đức có điều khoản bảo vệ quyền thừa kế và sở hữu tài sản của phụ nữ",
    "Lê Thánh Tông đăng cơ hoàng đế vào năm 1520",
    "Vua Lê Thánh Tông bị quân Chiêm Thành đánh bại hoàn toàn trong chiến dịch năm 1471",
    "Hoàng đế Lê Thánh Tông cử phái đoàn vượt biển sang châu Âu gặp Nữ hoàng Elizabeth",
  ];

  const handleVerify = async (claimsToVerify?: string[]) => {
    let list: string[] = [];
    if (claimsToVerify) {
      list = claimsToVerify;
    } else {
      list = inputText
        .split("\n")
        .map((l) => l.trim())
        .filter((l) => l.length > 5);
    }

    if (list.length === 0) return;

    setLoading(true);
    try {
      const res = await fetch("/api/verify/claims", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claims: list }),
      });
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error("Verification failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadSample = () => {
    setInputText(sampleClaims.join("\n"));
    handleVerify(sampleClaims);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-amber-600" />
              Thẩm Định Tuyên Bố Lịch Sử (Fact-Checking Studio)
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Phân loại 3 nhãn nghiêm ngặt: SUPPORTED (Chứng thực), CONTRADICTED (Mâu thuẫn), INSUFFICIENT_EVIDENCE (Thiếu bằng chứng).
            </p>
          </div>

          <button
            onClick={loadSample}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-amber-50 hover:bg-amber-100 text-amber-800 text-xs font-semibold rounded-lg border border-amber-200 transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-600" />
            Tải Mẫu Tuyên Bố Thử Nghiệm
          </button>
        </div>

        <div>
          <textarea
            rows={4}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Nhập các tuyên bố lịch sử cần xác minh (mỗi dòng một câu)..."
            className="w-full p-3.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 transition"
          />
        </div>

        <div className="flex justify-end">
          <button
            onClick={() => handleVerify()}
            disabled={loading || !inputText.trim()}
            className="px-5 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-lg shadow-sm transition disabled:opacity-50"
          >
            {loading ? "Đang thẩm định dữ liệu..." : "Thẩm Định Ngay"}
          </button>
        </div>
      </div>

      {/* Summary Scoreboard */}
      {results && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-500 font-medium">Tổng số tuyên bố</span>
              <p className="text-2xl font-bold text-slate-900 mt-0.5">{results.total_claims}</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-700 font-semibold">
              {results.total_claims}
            </div>
          </div>

          <div className="bg-emerald-50/70 p-4 rounded-xl border border-emerald-200 shadow-xs flex items-center justify-between">
            <div>
              <span className="text-xs text-emerald-800 font-medium">Được Chứng Thực</span>
              <p className="text-2xl font-bold text-emerald-700 mt-0.5">{results.supported_count}</p>
            </div>
            <CheckCircle2 className="w-8 h-8 text-emerald-600" />
          </div>

          <div className="bg-red-50/70 p-4 rounded-xl border border-red-200 shadow-xs flex items-center justify-between">
            <div>
              <span className="text-xs text-red-800 font-medium">Bị Mâu Thuẫn</span>
              <p className="text-2xl font-bold text-red-700 mt-0.5">{results.contradicted_count}</p>
            </div>
            <XCircle className="w-8 h-8 text-red-600" />
          </div>

          <div className="bg-amber-50/70 p-4 rounded-xl border border-amber-200 shadow-xs flex items-center justify-between">
            <div>
              <span className="text-xs text-amber-800 font-medium">Thiếu Bằng Chứng</span>
              <p className="text-2xl font-bold text-amber-700 mt-0.5">{results.insufficient_evidence_count}</p>
            </div>
            <HelpCircle className="w-8 h-8 text-amber-600" />
          </div>
        </div>
      )}

      {/* Detailed Claims Cards */}
      {results && results.results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-700">Chi Tiết Kết Quả Đối Soát</h3>

          <div className="space-y-3">
            {results.results.map((item, idx) => (
              <div
                key={idx}
                className={`p-5 rounded-xl border bg-white shadow-xs transition space-y-3 ${
                  item.status === "SUPPORTED"
                    ? "border-emerald-300 hover:border-emerald-400"
                    : item.status === "CONTRADICTED"
                    ? "border-red-300 hover:border-red-400"
                    : "border-amber-300 hover:border-amber-400"
                }`}
              >
                <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-2">
                  <h4 className="text-sm font-semibold text-slate-900 leading-snug">
                    "{item.claim}"
                  </h4>

                  {item.status === "SUPPORTED" && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 self-start">
                      <CheckCircle2 className="w-3.5 h-3.5" /> SUPPORTED
                    </span>
                  )}
                  {item.status === "CONTRADICTED" && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800 self-start">
                      <XCircle className="w-3.5 h-3.5" /> CONTRADICTED
                    </span>
                  )}
                  {item.status === "INSUFFICIENT_EVIDENCE" && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 self-start">
                      <HelpCircle className="w-3.5 h-3.5" /> INSUFFICIENT_EVIDENCE
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
                  {item.explanation}
                </p>

                {item.citations.length > 0 && (
                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    <span className="text-[11px] font-semibold text-slate-500">Căn cứ:</span>
                    {item.citations.map((c, cIdx) => (
                      <span
                        key={cIdx}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 border border-slate-200 rounded text-xs text-slate-700 font-mono"
                      >
                        <BookOpen className="w-3 h-3 text-amber-600" />
                        {c.filename} • Trang {c.page}
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
