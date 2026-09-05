import { useParams } from 'react-router-dom';

export const TimeOffRequestDetailPage = () => {
  const { id } = useParams();

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Time Off Request #{id}</h1>
      <div className="bg-slate-800 rounded-lg p-6">
        <p className="text-slate-300">Time off request details will be displayed here.</p>
      </div>
    </div>
  );
};
