import React from 'react';
import { Badge } from '../../components/ui/Badge';
import type { CohortAssignment } from '../../types/api';

export function AssignmentRow({ item }: { item: CohortAssignment }) {
  return (
    <tr className="hover:bg-slate-50/60 transition-colors">
      <td className="py-2.5 px-3 text-center text-slate-400 font-mono">{item.step}</td>
      <td className="py-2.5 px-4 font-medium text-slate-900">
        <div>{item.student_name}</div>
        <span className="text-[10px] text-slate-400 font-mono">{item.student_id}</span>
      </td>
      <td className="py-2.5 px-4">
        <p className="font-medium text-slate-800 line-clamp-2">{item.thesis_title}</p>
        {item.field_category && (
          <span className="text-[10px] text-indigo-600 font-medium">{item.field_category}</span>
        )}
      </td>
      <td className="py-2.5 px-4">
        <div className="font-semibold text-slate-900">{item.assigned_advisor_name}</div>
        {item.academic_title && <span className="text-[10px] text-slate-500">{item.academic_title}</span>}
      </td>
      <td className="py-2.5 px-3 text-right font-mono font-semibold text-indigo-600">
        {item.compatibility_score.toFixed(4)}
      </td>
      <td className="py-2.5 px-4">
        <div className="text-slate-600 text-xs">{item.historical_advisor || '—'}</div>
        {item.historical_match && (
          <Badge variant="success" className="text-[9px] py-0 px-1 mt-0.5">Trùng khớp</Badge>
        )}
      </td>
    </tr>
  );
}
