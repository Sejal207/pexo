import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
export const BackButton = ({ to }) => { const navigate = useNavigate(); return <button type="button" onClick={() => to ? navigate(to) : navigate(-1)} className="mb-5 inline-flex items-center gap-2 text-sm font-medium text-indigo-400 hover:text-indigo-300"><ArrowLeft className="h-4 w-4" />Back</button>; };
export default BackButton;
