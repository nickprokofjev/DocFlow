import { X, Calendar, DollarSign, MapPin, Building, Shield, FileText, Users, Clock, AlertTriangle } from 'lucide-react';
import { ContractWithParties } from '@/types';
import { formatDate, formatCurrency } from '@/lib/utils';

interface ContractDetailModalProps {
  contract: ContractWithParties;
  onClose: () => void;
}

export function ContractDetailModal({ contract, onClose }: ContractDetailModalProps) {
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full sm:p-6">
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
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl leading-6 font-bold text-gray-900">
                  Contract {contract.number}
                </h3>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  contract.status === 'active' ? 'bg-green-100 text-green-800' :
                  contract.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                  contract.status === 'terminated' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {contract.status || 'Active'}
                </span>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Basic Information */}
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">Basic Information</h4>
                  
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <Calendar className="w-5 h-5 text-gray-400 mr-3" />
                      <div>
                        <span className="text-sm text-gray-500">Date:</span>
                        <span className="ml-2 text-sm font-medium">{formatDate(contract.date)}</span>
                      </div>
                    </div>

                    {contract.contract_type && (
                      <div className="flex items-center">
                        <FileText className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Type:</span>
                          <span className="ml-2 text-sm font-medium">{contract.contract_type}</span>
                        </div>
                      </div>
                    )}

                    {contract.place_of_conclusion && (
                      <div className="flex items-center">
                        <MapPin className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Place:</span>
                          <span className="ml-2 text-sm font-medium">{contract.place_of_conclusion}</span>
                        </div>
                      </div>
                    )}

                    {contract.subject && (
                      <div>
                        <span className="text-sm text-gray-500">Subject:</span>
                        <p className="mt-1 text-sm text-gray-900">{contract.subject}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Parties */}
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">Parties</h4>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center mb-2">
                        <Users className="w-5 h-5 text-blue-500 mr-2" />
                        <span className="text-sm font-medium text-blue-700">Customer</span>
                      </div>
                      <div className="ml-7">
                        <p className="text-sm font-medium text-gray-900">{contract.customer.name}</p>
                        {contract.customer.inn && (
                          <p className="text-xs text-gray-500">INN: {contract.customer.inn}</p>
                        )}
                        {contract.customer.director_name && (
                          <p className="text-xs text-gray-500">Director: {contract.customer.director_name}</p>
                        )}
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center mb-2">
                        <Users className="w-5 h-5 text-green-500 mr-2" />
                        <span className="text-sm font-medium text-green-700">Contractor</span>
                      </div>
                      <div className="ml-7">
                        <p className="text-sm font-medium text-gray-900">{contract.contractor.name}</p>
                        {contract.contractor.inn && (
                          <p className="text-xs text-gray-500">INN: {contract.contractor.inn}</p>
                        )}
                        {contract.contractor.director_name && (
                          <p className="text-xs text-gray-500">Director: {contract.contractor.director_name}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Financial Information */}
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">Financial Terms</h4>
                  
                  <div className="space-y-3">
                    {(contract.amount || contract.amount_including_vat) && (
                      <div className="flex items-center">
                        <DollarSign className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Amount:</span>
                          <span className="ml-2 text-sm font-medium">
                            {formatCurrency(
                              (contract.amount_including_vat || contract.amount) || 0, 
                              contract.currency
                            )}
                          </span>
                          {contract.amount_including_vat && contract.vat_rate && (
                            <span className="ml-1 text-xs text-gray-500">(VAT {contract.vat_rate}%)</span>
                          )}
                        </div>
                      </div>
                    )}

                    {contract.vat_amount && (
                      <div className="flex items-center">
                        <div className="w-5 h-5 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">VAT Amount:</span>
                          <span className="ml-2 text-sm font-medium">{formatCurrency(contract.vat_amount, contract.currency)}</span>
                        </div>
                      </div>
                    )}

                    {contract.retention_percentage && (
                      <div className="flex items-center">
                        <div className="w-5 h-5 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Retention:</span>
                          <span className="ml-2 text-sm font-medium">{contract.retention_percentage}%</span>
                        </div>
                      </div>
                    )}

                    {contract.payment_terms_days && (
                      <div className="flex items-center">
                        <Clock className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Payment Terms:</span>
                          <span className="ml-2 text-sm font-medium">{contract.payment_terms_days} days</span>
                        </div>
                      </div>
                    )}

                    {contract.currency && (
                      <div className="flex items-center">
                        <div className="w-5 h-5 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Currency:</span>
                          <span className="ml-2 text-sm font-medium">{contract.currency}</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Work Object */}
                {(contract.work_object_name || contract.work_object_address || contract.cadastral_number) && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">Work Object</h4>
                    
                    <div className="space-y-3">
                      {contract.work_object_name && (
                        <div className="flex items-start">
                          <Building className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                          <div>
                            <span className="text-sm text-gray-500">Object:</span>
                            <p className="text-sm font-medium text-gray-900">{contract.work_object_name}</p>
                          </div>
                        </div>
                      )}

                      {contract.work_object_address && (
                        <div className="flex items-start">
                          <MapPin className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                          <div>
                            <span className="text-sm text-gray-500">Address:</span>
                            <p className="text-sm font-medium text-gray-900">{contract.work_object_address}</p>
                          </div>
                        </div>
                      )}

                      {contract.cadastral_number && (
                        <div className="flex items-center">
                          <FileText className="w-5 h-5 text-gray-400 mr-3" />
                          <div>
                            <span className="text-sm text-gray-500">Cadastral Number:</span>
                            <span className="ml-2 text-sm font-medium">{contract.cadastral_number}</span>
                          </div>
                        </div>
                      )}

                      {contract.land_area && (
                        <div className="flex items-center">
                          <div className="w-5 h-5 mr-3" />
                          <div>
                            <span className="text-sm text-gray-500">Land Area:</span>
                            <span className="ml-2 text-sm font-medium">{contract.land_area} sq.m</span>
                          </div>
                        </div>
                      )}

                      {contract.construction_permit && (
                        <div className="flex items-center">
                          <Shield className="w-5 h-5 text-gray-400 mr-3" />
                          <div>
                            <span className="text-sm text-gray-500">Construction Permit:</span>
                            <span className="ml-2 text-sm font-medium">{contract.construction_permit}</span>
                            {contract.permit_date && (
                              <span className="ml-1 text-xs text-gray-500">({formatDate(contract.permit_date)})</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Deadlines and Warranty */}
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">Timeline & Warranty</h4>
                  
                  <div className="space-y-3">
                    {contract.deadline && (
                      <div className="flex items-center">
                        <Calendar className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Deadline:</span>
                          <span className="ml-2 text-sm font-medium">{formatDate(contract.deadline)}</span>
                        </div>
                      </div>
                    )}

                    {contract.work_start_date && (
                      <div className="flex items-center">
                        <Clock className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Work Start:</span>
                          <span className="ml-2 text-sm font-medium">{formatDate(contract.work_start_date)}</span>
                        </div>
                      </div>
                    )}

                    {contract.work_completion_date && (
                      <div className="flex items-center">
                        <Clock className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Work Completion:</span>
                          <span className="ml-2 text-sm font-medium">{formatDate(contract.work_completion_date)}</span>
                        </div>
                      </div>
                    )}

                    {contract.warranty_period_months && (
                      <div className="flex items-center">
                        <Shield className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Warranty:</span>
                          <span className="ml-2 text-sm font-medium">{contract.warranty_period_months} months</span>
                        </div>
                      </div>
                    )}

                    {contract.warranty_start_basis && (
                      <div className="flex items-start">
                        <div className="w-5 h-5 mr-3" />
                        <div>
                          <span className="text-sm text-gray-500">Warranty Basis:</span>
                          <p className="text-sm font-medium text-gray-900">{contract.warranty_start_basis}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Penalties */}
                {(contract.delay_penalty_first_week || contract.delay_penalty_after_week || contract.penalties) && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">Penalties</h4>
                    
                    <div className="space-y-3">
                      {contract.delay_penalty_first_week && (
                        <div className="flex items-center">
                          <AlertTriangle className="w-5 h-5 text-yellow-500 mr-3" />
                          <div>
                            <span className="text-sm text-gray-500">Delay Penalty (first week):</span>
                            <span className="ml-2 text-sm font-medium">{contract.delay_penalty_first_week}%</span>
                          </div>
                        </div>
                      )}

                      {contract.delay_penalty_after_week && (
                        <div className="flex items-center">
                          <AlertTriangle className="w-5 h-5 text-red-500 mr-3" />
                          <div>
                            <span className="text-sm text-gray-500">Delay Penalty (after week):</span>
                            <span className="ml-2 text-sm font-medium">{contract.delay_penalty_after_week}%</span>
                          </div>
                        </div>
                      )}

                      {contract.document_penalty_amount && (
                        <div className="flex items-center">
                          <FileText className="w-5 h-5 text-gray-400 mr-3" />
                          <div>
                            <span className="text-sm text-gray-500">Document Penalty:</span>
                            <span className="ml-2 text-sm font-medium">{formatCurrency(contract.document_penalty_amount, contract.currency)}</span>
                          </div>
                        </div>
                      )}

                      {contract.site_violation_penalty && (
                        <div className="flex items-center">
                          <Building className="w-5 h-5 text-gray-400 mr-3" />
                          <div>
                            <span className="text-sm text-gray-500">Site Violation Penalty:</span>
                            <span className="ml-2 text-sm font-medium">{formatCurrency(contract.site_violation_penalty, contract.currency)}</span>
                          </div>
                        </div>
                      )}

                      {contract.penalties && (
                        <div className="flex items-start">
                          <AlertTriangle className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                          <div>
                            <span className="text-sm text-gray-500">General Penalties:</span>
                            <p className="text-sm font-medium text-gray-900">{contract.penalties}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Additional Information */}
              {contract.project_documentation && (
                <div className="mt-6 pt-6 border-t">
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Project Documentation</h4>
                  <p className="text-sm text-gray-900">{contract.project_documentation}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end space-x-3 pt-6 mt-6 border-t">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn btn-secondary"
                >
                  Close
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                >
                  Edit Contract
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}