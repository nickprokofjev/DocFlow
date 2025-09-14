// Утилитарные функции для приложения DocFlow

/**
 * Форматирует дату в локальном формате
 */
export const formatDate = (dateString: string | Date): string => {
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};

/**
 * Форматирует валюту в рублях
 */
export const formatCurrency = (amount: number, currency?: string): string => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: currency || 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
};

/**
 * Форматирует размер файла
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Склонение слов в зависимости от числа
 */
export const pluralize = (count: number, singular: string, few: string, many: string): string => {
  const lastDigit = count % 10;
  const lastTwoDigits = count % 100;

  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
    return many;
  } else if (lastDigit === 1) {
    return singular;
  } else if (lastDigit >= 2 && lastDigit <= 4) {
    return few;
  } else {
    return many;
  }
};

/**
 * Обрезает строку до заданной длины
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Проверяет валидность email
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Проверяет валидность ИНН
 */
export const isValidINN = (inn: string): boolean => {
  if (!inn || typeof inn !== 'string') return false;
  
  // Удаляем пробелы
  inn = inn.replace(/\s/g, '');
  
  // Проверяем длину (10 или 12 цифр)
  if (!/^\d{10}$/.test(inn) && !/^\d{12}$/.test(inn)) return false;
  
  // Проверяем контрольные цифры
  if (inn.length === 10) {
    return checkINN10(inn);
  } else {
    return checkINN12(inn);
  }
};

function checkINN10(inn: string): boolean {
  const coefficients = [2, 4, 10, 3, 5, 9, 4, 6, 8];
  let sum = 0;
  
  for (let i = 0; i < 9; i++) {
    sum += parseInt(inn[i]) * coefficients[i];
  }
  
  const controlDigit = (sum % 11) % 10;
  return controlDigit === parseInt(inn[9]);
}

function checkINN12(inn: string): boolean {
  const coefficients1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8];
  const coefficients2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8];
  
  let sum1 = 0;
  let sum2 = 0;
  
  for (let i = 0; i < 10; i++) {
    sum1 += parseInt(inn[i]) * coefficients1[i];
  }
  
  for (let i = 0; i < 11; i++) {
    sum2 += parseInt(inn[i]) * coefficients2[i];
  }
  
  const control1 = (sum1 % 11) % 10;
  const control2 = (sum2 % 11) % 10;
  
  return control1 === parseInt(inn[10]) && control2 === parseInt(inn[11]);
}

/**
 * Проверяет валидность КПП
 */
export const isValidKPP = (kpp: string): boolean => {
  if (!kpp || typeof kpp !== 'string') return false;
  
  // Удаляем пробелы
  kpp = kpp.replace(/\s/g, '');
  
  // КПП должен содержать 9 символов: 4 цифры, 2 буквы или цифры, 3 цифры
  return /^\d{4}[\dA-Z]{2}\d{3}$/.test(kpp);
};

/**
 * Генерирует случайный ID
 */
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9);
};

/**
 * Задержка выполнения
 */
export const delay = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Определяет цвет статуса
 */
export const getStatusColor = (status: string): string => {
  switch (status?.toLowerCase()) {
    case 'active':
    case 'completed':
    case 'healthy':
      return 'text-green-600 bg-green-100';
    case 'pending':
    case 'processing':
      return 'text-yellow-600 bg-yellow-100';
    case 'failed':
    case 'error':
    case 'cancelled':
      return 'text-red-600 bg-red-100';
    case 'draft':
      return 'text-gray-600 bg-gray-100';
    default:
      return 'text-blue-600 bg-blue-100';
  }
};

/**
 * Получает читаемое название статуса
 */
export const getStatusLabel = (status: string): string => {
  const statusLabels: Record<string, string> = {
    active: 'Активный',
    completed: 'Завершён',
    pending: 'Ожидает',
    processing: 'Обрабатывается',
    failed: 'Ошибка',
    cancelled: 'Отменён',
    draft: 'Черновик',
    healthy: 'Работает',
  };
  
  return statusLabels[status?.toLowerCase()] || status;
};