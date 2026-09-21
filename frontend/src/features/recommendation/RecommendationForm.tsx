import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Sparkles, Search } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';

export const recommendFormSchema = z.object({
  title: z
    .string()
    .min(3, 'Tên đề tài phải có ít nhất 3 ký tự')
    .max(500, 'Tên đề tài không quá 500 ký tự'),
  field: z.string().max(200).optional(),
  tech_stack: z.string().max(300).optional(),
  top_k: z.coerce.number().min(1).max(20).default(5),
});

export type RecommendFormData = z.infer<typeof recommendFormSchema>;

interface RecommendationFormProps {
  onSubmit: (data: RecommendFormData) => void;
  isLoading: boolean;
}

const PRESETS = [
  {
    title: 'Xây dựng trợ lý ảo hỗ trợ chẩn đoán hình ảnh y tế dựa trên thị giác máy tính và Deep Learning',
    field: 'Khoa học dữ liệu và Trí tuệ nhân tạo',
    tech_stack: 'Python, PyTorch, YOLOv8, CNN, FastAPI',
  },
  {
    title: 'Hệ thống giám sát nông nghiệp thông minh IoT kết hợp mạng cảm biến và cảnh báo sớm sâu bệnh',
    field: 'Hệ thống nhúng và IoT',
    tech_stack: 'ESP32, MQTT, Node.js, React, Docker',
  },
  {
    title: 'Nền tảng thương mại điện tử phi tập trung ứng dụng Smart Contracts trên Blockchain',
    field: 'Công nghệ phần mềm',
    tech_stack: 'Solidity, Ethereum, React, Web3.js, Spring Boot',
  },
];

export function RecommendationForm({ onSubmit, isLoading }: RecommendationFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<RecommendFormData>({
    resolver: zodResolver(recommendFormSchema),
    defaultValues: {
      title: 'Hệ thống phân tích cảm xúc phản hồi khách hàng sử dụng Transformers và BERT',
      field: 'Khoa học máy tính',
      tech_stack: 'Python, PyTorch, HuggingFace, FastAPI, Docker',
      top_k: 5,
    },
  });

  const applyPreset = (preset: typeof PRESETS[0]) => {
    setValue('title', preset.title, { shouldValidate: true });
    setValue('field', preset.field, { shouldValidate: true });
    setValue('tech_stack', preset.tech_stack, { shouldValidate: true });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-600" />
          Nhập Thông tin Đề tài Khóa luận để Tìm GVHD
        </CardTitle>
        <CardDescription>
          Hệ thống vector hóa nội dung bằng TF-IDF và tính điểm Cosine Similarity với hồ sơ nghiên cứu của 23 GVHD
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Tên Đề tài Khóa luận (Bắt buộc)"
            placeholder="Ví dụ: Ứng dụng Học sâu phát hiện bất thường mạng..."
            error={errors.title?.message}
            {...register('title')}
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Lĩnh vực / Chuyên ngành"
              placeholder="Khoa học máy tính, AI, IoT..."
              error={errors.field?.message}
              {...register('field')}
            />

            <Input
              label="Công nghệ / Tech Stack"
              placeholder="Python, PyTorch, React, Docker..."
              error={errors.tech_stack?.message}
              {...register('tech_stack')}
            />

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wide">
                Số lượng GVHD gợi ý (Top-K)
              </label>
              <select
                {...register('top_k')}
                className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:ring-2 focus:ring-indigo-500"
              >
                <option value={3}>Top 3 GVHD</option>
                <option value={5}>Top 5 GVHD</option>
                <option value={10}>Top 10 GVHD</option>
              </select>
            </div>
          </div>

          {/* Quick presets */}
          <div className="pt-2">
            <span className="text-xs font-semibold text-slate-500">Mẫu thử nhanh:</span>
            <div className="flex flex-wrap gap-2 mt-1.5">
              {PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => applyPreset(p)}
                  className="text-[11px] px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors cursor-pointer"
                >
                  Mẫu {idx + 1}: {p.field}
                </button>
              ))}
            </div>
          </div>

          <div className="pt-3 flex justify-end">
            <Button type="submit" variant="primary" isLoading={isLoading} className="gap-2">
              <Search className="w-4 h-4" />
              Tìm kiếm GVHD Tối ưu
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
