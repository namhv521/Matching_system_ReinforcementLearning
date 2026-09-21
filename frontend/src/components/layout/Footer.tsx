import React from 'react';

export function Footer() {
  return (
    <footer className="w-full border-t border-slate-200 bg-white py-6 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <span>Khóa luận Tốt nghiệp Đại học</span>
          <span>•</span>
          <span className="font-semibold text-slate-700">Đề tài: Mô hình Phân bổ Khóa luận Tốt nghiệp sử dụng Học tăng cường sâu (PPO) kết hợp Tối ưu hóa Hungary</span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="hover:text-indigo-600 font-medium transition-colors"
          >
            Tài liệu Swagger API (/docs)
          </a>
          <span>•</span>
          <span>FastAPI + React 18 + TypeScript + Tailwind</span>
        </div>
      </div>
    </footer>
  );
}
