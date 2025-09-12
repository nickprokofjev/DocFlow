import { useState } from 'react';
import { useMutation } from 'react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { contractsAPI } from '@/lib/api';
import { X, Upload, AlertCircle, CheckCircle } from 'lucide-react';

const contractSchema = z.object({
  number: z.string().min(1, 'Contract number is required'),
  contract_date: z.string().min(1, 'Contract date is required'),
  subject: z.string().optional(),
  amount: z.string().optional(),
  deadline: z.string().optional(),
  penalties: z.string().optional(),
  customer_name: z.string().min(1, 'Customer name is required'),
  contractor_name: z.string().min(1, 'Contractor name is required'),
});

type ContractFormData = z.infer<typeof contractSchema>;

interface ContractUploadModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function ContractUploadModal({ onClose, onSuccess }: ContractUploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [ocrResult, setOcrResult] = useState<any>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ContractFormData>({
    resolver: zodResolver(contractSchema),
  });

  const uploadMutation = useMutation(contractsAPI.upload, {
    onSuccess: (data) => {
      setUploadStatus('success');
      setOcrResult(data);
      setTimeout(() => {
        onSuccess();
      }, 2000);
    },
    onError: (error) => {
      setUploadStatus('error');
      console.error('Upload failed:', error);
    },
  });

  const onSubmit = async (data: ContractFormData) => {
    if (!file) {
      alert('Please select a file');
      return;
    }

    setUploadStatus('uploading');

    const uploadData = {
      ...data,
      amount: data.amount ? parseFloat(data.amount) : undefined,
      file,
    };

    uploadMutation.mutate(uploadData);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full sm:p-6">
          <div className="absolute top-0 right-0 pt-4 pr-4">
            <button
              type="button"
              className="bg-white rounded-md text-gray-400 hover:text-gray-600 focus:outline-none"
              onClick={onClose}
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="sm:flex sm:items-start">
            <div className="w-full">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Upload Contract
              </h3>

              {uploadStatus === 'success' ? (
                <div className="text-center py-8">
                  <CheckCircle className="mx-auto h-12 w-12 text-green-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Upload Successful!</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Contract has been processed and saved.
                  </p>
                  {ocrResult && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-md text-left">
                      <h4 className="text-sm font-medium text-gray-900">OCR Results:</h4>
                      <p className="text-xs text-gray-600 mt-2">
                        {ocrResult.ocr_text.substring(0, 200)}...
                      </p>
                    </div>
                  )}
                </div>
              ) : uploadStatus === 'error' ? (
                <div className="text-center py-8">
                  <AlertCircle className="mx-auto h-12 w-12 text-red-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Upload Failed</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Please try again or contact support.
                  </p>
                  <button
                    onClick={() => setUploadStatus('idle')}
                    className="mt-4 btn btn-secondary"
                  >
                    Try Again
                  </button>
                </div>
              ) : (
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  {/* File Upload */}
                  <div className="form-group">
                    <label className="form-label">Contract File</label>
                    <div
                      className={`mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-md transition-colors ${
                        dragActive
                          ? 'border-primary-400 bg-primary-50'
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                      onDragEnter={handleDrag}
                      onDragLeave={handleDrag}
                      onDragOver={handleDrag}
                      onDrop={handleDrop}
                    >
                      <div className="space-y-1 text-center">
                        <Upload className="mx-auto h-12 w-12 text-gray-400" />
                        <div className="flex text-sm text-gray-600">
                          <label className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500">
                            <span>Upload a file</span>
                            <input
                              type="file"
                              className="sr-only"
                              accept=".pdf,.jpg,.jpeg,.png"
                              onChange={handleFileChange}
                            />
                          </label>
                          <p className="pl-1">or drag and drop</p>
                        </div>
                        <p className="text-xs text-gray-500">PDF, PNG, JPG up to 10MB</p>
                        {file && (
                          <p className="text-sm text-primary-600 font-medium">
                            Selected: {file.name}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Form Fields */}
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div className="form-group">
                      <label className="form-label">Contract Number *</label>
                      <input
                        type="text"
                        className="input"
                        {...register('number')}
                      />
                      {errors.number && (
                        <p className="form-error">{errors.number.message}</p>
                      )}
                    </div>

                    <div className="form-group">
                      <label className="form-label">Contract Date *</label>
                      <input
                        type="date"
                        className="input"
                        {...register('contract_date')}
                      />
                      {errors.contract_date && (
                        <p className="form-error">{errors.contract_date.message}</p>
                      )}
                    </div>

                    <div className="form-group">
                      <label className="form-label">Customer Name *</label>
                      <input
                        type="text"
                        className="input"
                        {...register('customer_name')}
                      />
                      {errors.customer_name && (
                        <p className="form-error">{errors.customer_name.message}</p>
                      )}
                    </div>

                    <div className="form-group">
                      <label className="form-label">Contractor Name *</label>
                      <input
                        type="text"
                        className="input"
                        {...register('contractor_name')}
                      />
                      {errors.contractor_name && (
                        <p className="form-error">{errors.contractor_name.message}</p>
                      )}
                    </div>

                    <div className="form-group">
                      <label className="form-label">Amount</label>
                      <input
                        type="number"
                        step="0.01"
                        className="input"
                        {...register('amount')}
                      />
                    </div>

                    <div className="form-group">
                      <label className="form-label">Deadline</label>
                      <input
                        type="date"
                        className="input"
                        {...register('deadline')}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Subject</label>
                    <input
                      type="text"
                      className="input"
                      {...register('subject')}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Penalties</label>
                    <textarea
                      className="input"
                      rows={3}
                      {...register('penalties')}
                    />
                  </div>

                  {/* Actions */}
                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={onClose}
                      className="btn btn-secondary"
                      disabled={uploadStatus === 'uploading'}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={uploadStatus === 'uploading' || !file}
                    >
                      {uploadStatus === 'uploading' ? (
                        <div className="flex items-center">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                          Uploading...
                        </div>
                      ) : (
                        'Upload Contract'
                      )}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}