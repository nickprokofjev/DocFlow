import { useState, useEffect, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { contractsAPI, JobStatus } from "@/lib/api";
import {
  X,
  Upload,
  AlertCircle,
  CheckCircle,
  FileText,
  Loader2,
  Clock,
} from "lucide-react";

type UploadStep =
  | "upload"
  | "extracting"
  | "review"
  | "saving"
  | "success"
  | "error";

interface ContractUploadModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function ContractUploadModal({
  onClose,
  onSuccess,
}: ContractUploadModalProps) {
  const [step, setStep] = useState<UploadStep>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [extractedData, setExtractedData] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [editedData, setEditedData] = useState<any>({});
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [progress, setProgress] = useState(0);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Очистка интервала при размонтировании компонента
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // Функция для опроса статуса задачи
  const pollJobStatus = async (currentJobId: string) => {
    try {
      const response = await contractsAPI.getJobStatus(currentJobId);

      if (response.success && response.data) {
        const status = response.data;
        setJobStatus(status);
        setProgress(status.progress);

        if (status.status === "completed") {
          // Задача завершена успешно
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }

          if (status.result) {
            setExtractedData(status.result);
            setEditedData(status.result.contract_data || {});
            setStep("review");
          } else {
            setErrorMessage("Результат обработки пуст");
            setStep("error");
          }
        } else if (status.status === "failed") {
          // Задача завершена с ошибкой
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }

          setErrorMessage(status.error || "Неизвестная ошибка при обработке");
          setStep("error");
        } else if (status.status === "cancelled") {
          // Задача отменена
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }

          setErrorMessage("Обработка была отменена");
          setStep("error");
        }
        // Для статусов 'pending' и 'processing' продолжаем опрос
      }
    } catch (error: any) {
      console.error("Ошибка при получении статуса задачи:", error);
      // Не прерываем опрос при сетевых ошибках, попробуем ещё раз
    }
  };

  // Мутация для запуска извлечения данных
  const extractMutation = useMutation({
    mutationFn: (file: File) => contractsAPI.extractData(file),
    onSuccess: (response) => {
      if (response.success && response.data?.job_id) {
        const newJobId = response.data.job_id;
        setJobId(newJobId);
        setStep("extracting");
        setProgress(0);

        // Начинаем опрос статуса каждые 1 секунду для более быстрой реакции
        pollingIntervalRef.current = setInterval(() => {
          pollJobStatus(newJobId);
        }, 1000);

        // Сразу проверяем статус
        pollJobStatus(newJobId);
      } else {
        setErrorMessage(response.message || "Ошибка при запуске обработки");
        setStep("error");
      }
    },
    onError: (error: any) => {
      setErrorMessage(error.message || "Ошибка сети");
      setStep("error");
    },
  });

  // Мутация для сохранения контракта
  const uploadMutation = useMutation({
    mutationFn: (data: any) => contractsAPI.upload(data),
    onSuccess: () => {
      setStep("success");
      setTimeout(() => {
        handleClose();
        onSuccess();
      }, 2000);
    },
    onError: (error: any) => {
      setErrorMessage(error.message || "Ошибка при сохранении");
      setStep("error");
    },
  });

  // Мутация для сохранения извлеченных данных
  const saveExtractedMutation = useMutation({
    mutationFn: (data: any) => contractsAPI.saveExtracted(data),
    onSuccess: () => {
      setStep("success");
      setTimeout(() => {
        handleClose();
        onSuccess();
      }, 2000);
    },
    onError: (error: any) => {
      setErrorMessage(error.message || "Ошибка при сохранении");
      setStep("error");
    },
  });

  const handleFileUpload = () => {
    if (!file) return;
    // Immediately transition to extracting step to show progress
    setStep("extracting");
    setProgress(0);
    extractMutation.mutate(file);
  };

  const handleSave = () => {
    if (!file) return;
    setStep("saving");

    // Prepare the contract data with extracted information
    const contractData = {
      ...editedData,
      // Add required fields with default values if empty
      number: editedData.number || "Номер не указан",
      contract_date:
        editedData.contract_date || new Date().toISOString().split("T")[0],
      customer_name: editedData.customer_name || "Заказчик не указан",
      contractor_name: editedData.contractor_name || "Подрядчик не указан",
      // Add attachments if they exist
      attachments: extractedData?.contract_data?.attachments || [],
    };

    // Use the new saveExtracted endpoint instead of the old upload endpoint
    saveExtractedMutation.mutate(contractData);
  };

  const handleClose = () => {
    // Отменяем задачу, если она выполняется
    if (jobId && jobStatus?.status === "processing") {
      contractsAPI.cancelJob(jobId).catch(console.error);
    }

    // Очищаем интервал
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }

    // Сбрасываем состояние
    setFile(null);
    setStep("upload");
    setExtractedData(null);
    setErrorMessage("");
    setJobId(null);
    setJobStatus(null);
    setProgress(0);
    onClose();
  };

  const handleRetry = () => {
    // Очищаем предыдущее состояние
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }

    setJobId(null);
    setJobStatus(null);
    setProgress(0);
    setErrorMessage("");
    setStep("upload");
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
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

  const updateField = (field: string, value: string) => {
    setEditedData((prev: any) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={handleClose}
        />

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full sm:p-6">
          <div className="absolute top-0 right-0 pt-4 pr-4">
            <button
              type="button"
              className="bg-white rounded-md text-gray-400 hover:text-gray-600 focus:outline-none"
              onClick={handleClose}
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="w-full">
            {/* Прогресс-бар */}
            <div className="mb-6">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span
                  className={
                    step === "upload" ? "font-medium text-blue-600" : ""
                  }
                >
                  1. Загрузка файла
                </span>
                <span
                  className={
                    ["extracting", "review", "saving", "success"].includes(step)
                      ? "font-medium text-blue-600"
                      : ""
                  }
                >
                  2. Извлечение данных
                </span>
                <span
                  className={
                    ["review", "saving", "success"].includes(step)
                      ? "font-medium text-blue-600"
                      : ""
                  }
                >
                  3. Проверка
                </span>
                <span
                  className={
                    ["saving", "success"].includes(step)
                      ? "font-medium text-blue-600"
                      : ""
                  }
                >
                  4. Сохранение
                </span>
              </div>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                  style={{
                    width:
                      step === "upload"
                        ? "25%"
                        : step === "extracting"
                        ? "50%"
                        : step === "review"
                        ? "75%"
                        : ["saving", "success"].includes(step)
                        ? "100%"
                        : "0%",
                  }}
                />
              </div>
            </div>

            {/* Этап загрузки */}
            {step === "upload" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Загрузите договор
                  </h3>
                  <p className="text-gray-600">
                    Система автоматически извлечёт все данные из вашего
                    документа
                  </p>
                </div>

                <div
                  className={`flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-md transition-colors ${
                    dragActive
                      ? "border-blue-400 bg-blue-50"
                      : "border-gray-300 hover:border-gray-400"
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <div className="space-y-1 text-center">
                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                    <div className="flex text-sm text-gray-600">
                      <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500">
                        <span>Выбрать файл</span>
                        <input
                          type="file"
                          className="sr-only"
                          accept=".pdf,.jpg,.jpeg,.png"
                          onChange={handleFileChange}
                        />
                      </label>
                      <p className="pl-1">или перетащите сюда</p>
                    </div>
                    <p className="text-xs text-gray-500">
                      PDF, PNG, JPG до 50MB
                    </p>
                    {file && (
                      <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-md">
                        <div className="flex items-center">
                          <FileText className="h-5 w-5 text-green-600 mr-2" />
                          <span className="text-sm font-medium text-green-800">
                            {file.name}
                          </span>
                        </div>
                        <p className="text-xs text-green-600 mt-1">
                          Размер: {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={handleFileUpload}
                    disabled={!file}
                    className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Извлечь данные
                  </button>
                </div>
              </div>
            )}

            {/* Этап извлечения */}
            {step === "extracting" && (
              <div className="text-center py-12">
                <Loader2 className="mx-auto h-16 w-16 text-blue-600 animate-spin mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Обрабатываем {file?.name}
                </h3>

                {/* Прогресс-бар */}
                <div className="max-w-md mx-auto mb-4">
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-sm text-gray-600 mt-2">
                    <span>{progress}%</span>
                    <span>Прогресс</span>
                  </div>
                </div>

                {/* Статус сообщение */}
                <p className="text-gray-600 mb-4">
                  {jobStatus?.message || "Подготовка к обработке..."}
                </p>

                {/* Подсказка о времени */}
                <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                  <Clock className="h-4 w-4" />
                  <span>Обработка может занять несколько минут</span>
                </div>

                {/* Кнопка отмены */}
                <button
                  onClick={() => {
                    if (jobId) {
                      contractsAPI
                        .cancelJob(jobId)
                        .then(() => {
                          handleClose();
                        })
                        .catch(console.error);
                    } else {
                      handleClose();
                    }
                  }}
                  className="mt-6 btn btn-secondary"
                >
                  Отменить
                </button>
              </div>
            )}

            {/* Этап проверки */}
            {step === "review" && extractedData && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Проверьте извлечённые данные
                  </h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>
                      Извлечено полей:{" "}
                      {extractedData.extraction_stats?.fields_extracted || 0}
                    </span>
                    <span>
                      Длина текста:{" "}
                      {extractedData.extraction_stats?.text_length || 0}{" "}
                      символов
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div className="form-group">
                    <label className="form-label">Номер договора</label>
                    <input
                      type="text"
                      className="input"
                      value={editedData.number || ""}
                      onChange={(e) => updateField("number", e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Дата договора</label>
                    <input
                      type="date"
                      className="input"
                      value={editedData.contract_date || ""}
                      onChange={(e) =>
                        updateField("contract_date", e.target.value)
                      }
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Заказчик</label>
                    <input
                      type="text"
                      className="input"
                      value={editedData.customer_name || ""}
                      onChange={(e) =>
                        updateField("customer_name", e.target.value)
                      }
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Подрядчик</label>
                    <input
                      type="text"
                      className="input"
                      value={editedData.contractor_name || ""}
                      onChange={(e) =>
                        updateField("contractor_name", e.target.value)
                      }
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Сумма (с НДС)</label>
                    <input
                      type="number"
                      step="0.01"
                      className="input"
                      value={editedData.amount_including_vat || ""}
                      onChange={(e) =>
                        updateField("amount_including_vat", e.target.value)
                      }
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Кадастровый номер</label>
                    <input
                      type="text"
                      className="input"
                      value={editedData.cadastral_number || ""}
                      onChange={(e) =>
                        updateField("cadastral_number", e.target.value)
                      }
                    />
                  </div>
                </div>

                <div className="flex justify-between pt-4">
                  <button
                    type="button"
                    onClick={() => setStep("upload")}
                    className="btn btn-secondary"
                  >
                    Назад
                  </button>
                  <button
                    type="button"
                    onClick={handleSave}
                    className="btn btn-primary"
                  >
                    Сохранить договор
                  </button>
                </div>
              </div>
            )}

            {/* Этап сохранения */}
            {step === "saving" && (
              <div className="text-center py-12">
                <Loader2 className="mx-auto h-16 w-16 text-green-600 animate-spin mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Сохраняем договор...
                </h3>
                <p className="text-gray-600">Пожалуйста, подождите</p>
              </div>
            )}

            {/* Этап успеха */}
            {step === "success" && (
              <div className="text-center py-12">
                <CheckCircle className="mx-auto h-16 w-16 text-green-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Договор успешно сохранён!
                </h3>
                <p className="text-gray-600 mb-4">
                  Все данные были автоматически извлечены и сохранены
                </p>
              </div>
            )}

            {/* Этап ошибки */}
            {step === "error" && (
              <div className="text-center py-12">
                <AlertCircle className="mx-auto h-16 w-16 text-red-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Ошибка обработки
                </h3>
                <div className="max-w-md mx-auto">
                  <p className="text-gray-600 mb-6 text-sm leading-relaxed">
                    {errorMessage}
                  </p>

                  {/* Подсказки по решению проблем */}
                  {errorMessage.includes("Gateway Time-out") && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 text-left">
                      <h4 className="font-medium text-yellow-800 mb-2">
                        Рекомендации:
                      </h4>
                      <ul className="text-sm text-yellow-700 space-y-1">
                        <li>• Попробуйте уменьшить размер файла</li>
                        <li>• Убедитесь, что документ читаемый</li>
                        <li>• Попробуйте повторить позже</li>
                      </ul>
                    </div>
                  )}

                  {errorMessage.includes("OCR") && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left">
                      <h4 className="font-medium text-blue-800 mb-2">
                        Проблема с распознаванием текста:
                      </h4>
                      <ul className="text-sm text-blue-700 space-y-1">
                        <li>• Проверьте качество скана</li>
                        <li>• Используйте формат PDF вместо изображения</li>
                        <li>• Убедитесь, что текст чёткий</li>
                      </ul>
                    </div>
                  )}
                </div>

                <div className="flex justify-center space-x-4">
                  <button onClick={handleRetry} className="btn btn-secondary">
                    Выбрать другой файл
                  </button>
                  <button onClick={handleRetry} className="btn btn-primary">
                    Повторить
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
