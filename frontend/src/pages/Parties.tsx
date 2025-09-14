import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { partiesAPI } from '@/lib/api';
import { 
  Users, 
  Plus, 
  Search,
  Building,
  Edit,
  Trash2,
  X,
  Save
} from 'lucide-react';
import type { Party, CreatePartyRequest } from '@/types';

export function Parties() {
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingParty, setEditingParty] = useState<Party | null>(null);
  const [roleFilter, setRoleFilter] = useState<string>('');
  
  const queryClient = useQueryClient();

  const { data: parties, isLoading, error } = useQuery({
    queryKey: ['parties', roleFilter],
    queryFn: () => partiesAPI.getAll({ role: roleFilter || undefined })
  });

  const createMutation = useMutation({
    mutationFn: partiesAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parties'] });
      setShowCreateModal(false);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<CreatePartyRequest> }) =>
      partiesAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parties'] });
      setEditingParty(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => partiesAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parties'] });
    },
  });

  const filteredParties = parties?.filter(party =>
    party.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    party.inn?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Parties</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage customers and contractors
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary inline-flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Party
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="input pl-10"
            placeholder="Search parties..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select
          className="input w-full sm:w-auto"
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
        >
          <option value="">All Roles</option>
          <option value="customer">Customers</option>
          <option value="contractor">Contractors</option>
        </select>
      </div>

      {/* Parties List */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading parties</h3>
          <p className="mt-1 text-sm text-gray-500">
            Please try again later.
          </p>
        </div>
      ) : filteredParties.length === 0 ? (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No parties found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'Try adjusting your search terms.' : 'Get started by adding your first party.'}
          </p>
          {!searchTerm && (
            <div className="mt-6">
              <button
                onClick={() => setShowCreateModal(true)}
                className="btn btn-primary inline-flex items-center"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Party
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {filteredParties.map((party) => (
              <li key={party.id}>
                {editingParty?.id === party.id ? (
                  <EditPartyForm
                    party={party}
                    onSave={(data) => updateMutation.mutate({ id: party.id, data })}
                    onCancel={() => setEditingParty(null)}
                    isLoading={updateMutation.isPending}
                  />
                ) : (
                  <div className="px-4 py-4 flex items-center justify-between hover:bg-gray-50">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center">
                          <Building className="h-5 w-5 text-gray-500" />
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="flex items-center">
                          <div className="text-sm font-medium text-gray-900">
                            {party.name}
                          </div>
                          <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            party.role === 'customer' 
                              ? 'bg-blue-100 text-blue-800' 
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {party.role}
                          </span>
                        </div>
                        <div className="text-sm text-gray-500">
                          {party.inn && `INN: ${party.inn}`}
                          {party.inn && party.kpp && ' • '}
                          {party.kpp && `KPP: ${party.kpp}`}
                        </div>
                        {party.address && (
                          <div className="text-sm text-gray-500">
                            {party.address}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setEditingParty(party)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm('Are you sure you want to delete this party?')) {
                            deleteMutation.mutate(party.id);
                          }
                        }}
                        className="text-gray-400 hover:text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Create Party Modal */}
      {showCreateModal && (
        <CreatePartyModal
          onClose={() => setShowCreateModal(false)}
          onSave={(data: CreatePartyRequest) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
        />
      )}
    </div>
  );
}

interface EditPartyFormProps {
  party: Party;
  onSave: (data: Partial<CreatePartyRequest>) => void;
  onCancel: () => void;
  isLoading: boolean;
}

function EditPartyForm({ party, onSave, onCancel, isLoading }: EditPartyFormProps) {
  const [formData, setFormData] = useState({
    name: party.name,
    inn: party.inn || '',
    kpp: party.kpp || '',
    address: party.address || '',
    role: party.role,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="px-4 py-4 bg-gray-50">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">Name</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="mt-1 input"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Role</label>
          <select
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value as 'customer' | 'contractor' })}
            className="mt-1 input"
          >
            <option value="customer">Customer</option>
            <option value="contractor">Contractor</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">INN</label>
          <input
            type="text"
            value={formData.inn}
            onChange={(e) => setFormData({ ...formData, inn: e.target.value })}
            className="mt-1 input"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">KPP</label>
          <input
            type="text"
            value={formData.kpp}
            onChange={(e) => setFormData({ ...formData, kpp: e.target.value })}
            className="mt-1 input"
          />
        </div>
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-gray-700">Address</label>
          <input
            type="text"
            value={formData.address}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
            className="mt-1 input"
          />
        </div>
      </div>
      <div className="mt-4 flex justify-end space-x-2">
        <button
          type="button"
          onClick={onCancel}
          className="btn btn-secondary"
          disabled={isLoading}
        >
          <X className="w-4 h-4 mr-2" />
          Cancel
        </button>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isLoading}
        >
          <Save className="w-4 h-4 mr-2" />
          {isLoading ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  );
}

interface CreatePartyModalProps {
  onClose: () => void;
  onSave: (data: CreatePartyRequest) => void;
  isLoading: boolean;
}

function CreatePartyModal({ onClose, onSave, isLoading }: CreatePartyModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    inn: '',
    kpp: '',
    address: '',
    role: 'customer' as 'customer' | 'contractor',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      ...formData,
      inn: formData.inn || undefined,
      kpp: formData.kpp || undefined,
      address: formData.address || undefined,
    });
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div className="absolute top-0 right-0 pt-4 pr-4">
            <button
              type="button"
              className="bg-white rounded-md text-gray-400 hover:text-gray-600"
              onClick={onClose}
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="sm:flex sm:items-start">
            <div className="w-full">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Add New Party
              </h3>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="mt-1 input"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Role *</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value as 'customer' | 'contractor' })}
                    className="mt-1 input"
                  >
                    <option value="customer">Customer</option>
                    <option value="contractor">Contractor</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">INN</label>
                  <input
                    type="text"
                    value={formData.inn}
                    onChange={(e) => setFormData({ ...formData, inn: e.target.value })}
                    className="mt-1 input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">KPP</label>
                  <input
                    type="text"
                    value={formData.kpp}
                    onChange={(e) => setFormData({ ...formData, kpp: e.target.value })}
                    className="mt-1 input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Address</label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    className="mt-1 input"
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={onClose}
                    className="btn btn-secondary"
                    disabled={isLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Creating...' : 'Create Party'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}