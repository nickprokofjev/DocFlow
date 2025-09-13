import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contractsAPI } from '@/lib/api';
import { formatDate, formatCurrency } from '@/lib/utils';
import { 
  Upload, 
  FileText, 
  Plus, 
  Search,
  Calendar,
  DollarSign
} from 'lucide-react';
import { ContractUploadModal } from '@/components/ContractUploadModal';

export function Contracts() {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const queryClient = useQueryClient();

  const { data: contracts, isLoading, error } = useQuery({
    queryKey: ['contracts'],
    queryFn: () => contractsAPI.getAll()
  });

  // Mutation for deleting contracts
  // Мутация для удаления контрактов
  const deleteMutation = useMutation({
    mutationFn: contractsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
    onError: (error) => {
      console.error('Failed to delete contract:', error);
      alert('Failed to delete contract. Please try again.');
    },
  });

  const handleDeleteContract = (contractId: number) => {
    if (window.confirm('Are you sure you want to delete this contract?')) {
      deleteMutation.mutate(contractId);
    }
  };

  const filteredContracts = contracts?.filter(contract =>
    contract.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contract.subject?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Contracts</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your contracts and documents
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setShowUploadModal(true)}
            className="btn btn-primary inline-flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Upload Contract
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          className="input pl-10"
          placeholder="Search contracts..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Contracts Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading contracts</h3>
          <p className="mt-1 text-sm text-gray-500">
            Please try again later.
          </p>
        </div>
      ) : filteredContracts.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No contracts found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'Try adjusting your search terms.' : 'Get started by uploading your first contract.'}
          </p>
          {!searchTerm && (
            <div className="mt-6">
              <button
                onClick={() => setShowUploadModal(true)}
                className="btn btn-primary inline-flex items-center"
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload Contract
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filteredContracts.map((contract) => (
            <div key={contract.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {contract.number}
                  </h3>
                  
                  {contract.subject && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {contract.subject}
                    </p>
                  )}
                  
                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-500">
                      <Calendar className="w-4 h-4 mr-2" />
                      {formatDate(contract.date)}
                    </div>
                    
                    {contract.amount && (
                      <div className="flex items-center text-sm text-gray-500">
                        <DollarSign className="w-4 h-4 mr-2" />
                        {formatCurrency(contract.amount)}
                      </div>
                    )}
                    
                    {contract.deadline && (
                      <div className="flex items-center text-sm text-gray-500">
                        <Calendar className="w-4 h-4 mr-2" />
                        Deadline: {formatDate(contract.deadline)}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="ml-4">
                  <FileText className="w-6 h-6 text-gray-400" />
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                  <div className="flex items-center space-x-2">
                    <button className="text-sm text-primary-600 hover:text-primary-500">
                      View Details
                    </button>
                    <button 
                      onClick={() => handleDeleteContract(contract.id)}
                      className="text-sm text-red-600 hover:text-red-500"
                      disabled={deleteMutation.isPending}
                    >
                      {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <ContractUploadModal
          onClose={() => setShowUploadModal(false)}
          onSuccess={() => {
            setShowUploadModal(false);
            queryClient.invalidateQueries({ queryKey: ['contracts'] });
          }}
        />
      )}
    </div>
  );
}