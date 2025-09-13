import { useQuery } from '@tanstack/react-query';
import { contractsAPI, partiesAPI, healthAPI } from '@/lib/api';
import { FileText, Users, CheckCircle, AlertCircle } from 'lucide-react';

export function Dashboard() {
  const { data: contracts, isLoading: contractsLoading } = useQuery({
    queryKey: ['contracts'],
    queryFn: () => contractsAPI.getAll({ limit: 5 })
  });

  const { data: parties, isLoading: partiesLoading } = useQuery({
    queryKey: ['parties'], 
    queryFn: () => partiesAPI.getAll({ limit: 5 })
  });

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: healthAPI.check,
    refetchInterval: 30000
  });

  const stats = [
    {
      name: 'Total Contracts',
      value: contracts?.length || 0,
      icon: FileText,
      color: 'text-blue-600 bg-blue-100',
      loading: contractsLoading,
    },
    {
      name: 'Total Parties',
      value: parties?.length || 0,
      icon: Users,
      color: 'text-green-600 bg-green-100',
      loading: partiesLoading,
    },
    {
      name: 'System Status',
      value: health?.status === 'healthy' ? 'Healthy' : 'Issues',
      icon: health?.status === 'healthy' ? CheckCircle : AlertCircle,
      color: health?.status === 'healthy' 
        ? 'text-green-600 bg-green-100' 
        : 'text-red-600 bg-red-100',
      loading: false,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome to DocFlow document management system
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className={`p-3 rounded-md ${stat.color}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stat.loading ? (
                        <div className="animate-pulse h-6 bg-gray-200 rounded w-16"></div>
                      ) : (
                        stat.value
                      )}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Contracts */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Recent Contracts</h3>
            <a
              href="/contracts"
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              View all
            </a>
          </div>
          
          {contractsLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : contracts && contracts.length > 0 ? (
            <div className="space-y-3">
              {contracts.slice(0, 5).map((contract) => (
                <div key={contract.id} className="border-l-4 border-primary-400 pl-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {contract.number}
                      </p>
                      <p className="text-sm text-gray-500">
                        {contract.subject || 'No subject'}
                      </p>
                    </div>
                    <span className="text-xs text-gray-400">
                      {new Date(contract.date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No contracts found</p>
          )}
        </div>

        {/* Recent Parties */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Recent Parties</h3>
            <a
              href="/parties"
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              View all
            </a>
          </div>
          
          {partiesLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : parties && parties.length > 0 ? (
            <div className="space-y-3">
              {parties.slice(0, 5).map((party) => (
                <div key={party.id} className="border-l-4 border-green-400 pl-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {party.name}
                      </p>
                      <p className="text-sm text-gray-500 capitalize">
                        {party.role}
                      </p>
                    </div>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                      {party.role}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No parties found</p>
          )}
        </div>
      </div>
    </div>
  );
}