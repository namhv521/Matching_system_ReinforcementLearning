import React, { useState } from 'react';
import { Maximize2, FileImage } from 'lucide-react';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Skeleton } from '../../components/ui/Skeleton';
import { useFigures } from '../../hooks/useMatchingData';
import type { FigureItem } from '../../types/api';

export function ResearchFiguresGallery() {
  const { data: figures, isLoading } = useFigures();
  const [selectedFigure, setSelectedFigure] = useState<FigureItem | null>(null);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map(i => (
          <Card key={i} className="p-4">
            <Skeleton className="h-40 w-full mb-3 rounded-lg" />
            <Skeleton className="h-5 w-3/4 mb-2" />
            <Skeleton className="h-4 w-full" />
          </Card>
        ))}
      </div>
    );
  }

  if (!figures || figures.length === 0) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-bold text-slate-900 text-base flex items-center gap-2">
            <FileImage className="w-5 h-5 text-indigo-600" />
            Sơ đồ & Biểu đồ Nghiên cứu Luận văn KLTN
          </h4>
          <p className="text-xs text-slate-500">
            Các sơ đồ kiến trúc và biểu đồ được tái tạo trực tiếp từ artifact thực nghiệm
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {figures.map(fig => {
          const imgUrl = `/figures/${fig.filename}`;
          return (
            <Card
              key={fig.id}
              className="hover:border-indigo-300 hover:shadow-sm transition-all overflow-hidden flex flex-col"
            >
              <button
                type="button"
                aria-label={`Phóng to ${fig.title}`}
                className="relative bg-slate-100 aspect-video overflow-hidden cursor-pointer group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-indigo-500"
                onClick={() => setSelectedFigure(fig)}
              >
                <img
                  src={imgUrl}
                  alt={fig.title}
                  className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-300"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-slate-900/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <span className="bg-white/90 text-slate-800 text-xs font-semibold px-2.5 py-1.5 rounded-lg shadow-sm flex items-center gap-1.5">
                    <Maximize2 className="w-3.5 h-3.5" /> Phóng to
                  </span>
                </div>
              </button>
              <CardContent className="p-4 flex-1 flex flex-col justify-between">
                <div>
                  <h5 className="font-bold text-slate-900 text-sm">{fig.title}</h5>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-2">{fig.caption}</p>
                </div>
                <div className="pt-3 mt-3 border-t border-slate-100 flex justify-end">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedFigure(fig)}
                    className="text-xs gap-1 h-7"
                  >
                    <Maximize2 className="w-3 h-3" /> Chi tiết
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Full Modal Viewer */}
      {selectedFigure && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedFigure(null)}
          title={selectedFigure.title}
          description={selectedFigure.caption}
          maxWidth="4xl"
        >
          <div className="space-y-4">
            <div className="bg-slate-950/5 rounded-xl p-2 flex items-center justify-center overflow-hidden border border-slate-200">
              <img
                src={`/figures/${selectedFigure.filename}`}
                alt={selectedFigure.title}
                className="max-h-[65vh] w-auto object-contain rounded-lg shadow-xs"
              />
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-600 leading-relaxed">
              <strong className="text-slate-800 font-semibold block mb-1">Thuyết minh học thuật:</strong>
              {selectedFigure.caption}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
