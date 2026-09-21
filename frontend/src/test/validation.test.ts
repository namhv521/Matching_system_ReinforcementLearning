import { describe, it, expect } from 'vitest';
import { recommendFormSchema } from '../features/recommendation/RecommendationForm';
import { formatPercent, formatScore } from '../lib/utils';

describe('Recommendation Form Schema Validation', () => {
  it('should accept valid thesis recommendation form payload', () => {
    const validData = {
      title: 'Hệ thống nhận diện biển số xe sử dụng YOLO và OCR',
      field: 'Khoa học máy tính',
      tech_stack: 'Python, PyTorch',
      top_k: 5,
    };
    const result = recommendFormSchema.safeParse(validData);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.title).toBe(validData.title);
      expect(result.data.top_k).toBe(5);
    }
  });

  it('should reject thesis title with less than 3 characters', () => {
    const invalidData = {
      title: 'AI',
      top_k: 5,
    };
    const result = recommendFormSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toContain('ít nhất 3 ký tự');
    }
  });

  it('should reject top_k out of bounds', () => {
    const invalidTopK = {
      title: 'Nghiên cứu mô hình ngôn ngữ lớn tiếng Việt',
      top_k: 50,
    };
    const result = recommendFormSchema.safeParse(invalidTopK);
    expect(result.success).toBe(false);
  });
});

describe('Formatting Utility Functions', () => {
  it('formats percentages correctly', () => {
    expect(formatPercent(0.8523)).toBe('85.2%');
    expect(formatPercent(1.0)).toBe('100.0%');
    expect(formatPercent(NaN)).toBe('0%');
  });

  it('formats compatibility scores correctly', () => {
    expect(formatScore(0.06557)).toBe('0.0656');
    expect(formatScore(0.12)).toBe('0.1200');
    expect(formatScore(NaN)).toBe('0.0000');
  });
});
