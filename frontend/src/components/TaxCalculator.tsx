'use client'

import { useState, useCallback } from 'react'
import { Calculator, Loader2, TrendingDown, Wallet, PiggyBank, AlertTriangle, Info, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TaxBreakdown {
  bracket: string
  rate: string
  taxable_amount: number
  tax: number
}

interface TaxResult {
  gross_income: number
  total_allowances: number
  total_reliefs: number
  consolidated_relief: number
  taxable_income: number
  tax_due: number
  effective_rate: number
  breakdown: TaxBreakdown[]
  minimum_tax_applies: boolean
  minimum_tax_amount: number
  net_income: number
  monthly_tax: number
}

interface FormData {
  income: string
  allowances: string
  reliefs: string
  pension: string
  includeCRA: boolean
}

const initialFormData: FormData = {
  income: '',
  allowances: '',
  reliefs: '',
  pension: '',
  includeCRA: true,
}

export default function TaxCalculator() {
  const [formData, setFormData] = useState<FormData>(initialFormData)
  const [result, setResult] = useState<TaxResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleInputChange = useCallback((field: keyof FormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setError('')
  }, [])

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const income = parseFloat(formData.income)
    if (!income || income <= 0) {
      setError('Please enter a valid income amount')
      return
    }

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      // Create abort controller for timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000) // 15 second timeout
      
      const response = await fetch('/api/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          income,
          allowances: parseFloat(formData.allowances) || 0,
          reliefs: parseFloat(formData.reliefs) || 0,
          pension: parseFloat(formData.pension) || 0,
          include_cra: formData.includeCRA,
        }),
        signal: controller.signal,
      })

      clearTimeout(timeoutId)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || `API error: ${response.status}`)
      }

      setResult(data)
    } catch (err) {
      console.error('Error:', err)
      if (err instanceof Error && err.name === 'AbortError') {
        setError('Request timed out. Please check your connection and try again.')
      } else {
        setError(err instanceof Error ? err.message : 'Failed to calculate tax. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = useCallback(() => {
    setFormData(initialFormData)
    setResult(null)
    setError('')
  }, [])

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(amount)
  }

  const formatPercent = (value: number) => `${value.toFixed(2)}%`

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Calculator className="w-7 h-7 text-primary-600" />
            Personal Income Tax Calculator
          </h2>
          <p className="text-gray-600 mt-2">
            Calculate your tax liability based on the Nigeria Tax Act 2025
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="space-y-6">
            <form onSubmit={handleCalculate} className="space-y-5">
              {/* Income Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Gross Annual Income (₦) <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₦</span>
                  <input
                    type="number"
                    value={formData.income}
                    onChange={(e) => handleInputChange('income', e.target.value)}
                    placeholder="5,000,000"
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    required
                    min="0"
                    step="1000"
                  />
                </div>
              </div>

              {/* Allowances Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Total Allowances (₦)
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₦</span>
                  <input
                    type="number"
                    value={formData.allowances}
                    onChange={(e) => handleInputChange('allowances', e.target.value)}
                    placeholder="0"
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    min="0"
                    step="1000"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                  <Info className="w-3 h-3" /> Housing, transport, meal, and utility allowances
                </p>
              </div>

              {/* Reliefs Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Tax Reliefs (₦)
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₦</span>
                  <input
                    type="number"
                    value={formData.reliefs}
                    onChange={(e) => handleInputChange('reliefs', e.target.value)}
                    placeholder="0"
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    min="0"
                    step="1000"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                  <Info className="w-3 h-3" /> Life insurance, NHF contributions, mortgage interest
                </p>
              </div>

              {/* Pension Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Pension Contribution (₦)
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₦</span>
                  <input
                    type="number"
                    value={formData.pension}
                    onChange={(e) => handleInputChange('pension', e.target.value)}
                    placeholder="0"
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    min="0"
                    step="1000"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                  <Info className="w-3 h-3" /> Employee pension contribution (8% of basic is tax-exempt)
                </p>
              </div>

              {/* CRA Toggle */}
              <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                <input
                  type="checkbox"
                  id="includeCRA"
                  checked={formData.includeCRA}
                  onChange={(e) => handleInputChange('includeCRA', e.target.checked)}
                  className="w-5 h-5 rounded text-primary-600 focus:ring-primary-500"
                />
                <label htmlFor="includeCRA" className="flex-1">
                  <span className="text-sm font-medium text-gray-900">
                    Include Consolidated Relief Allowance (CRA)
                  </span>
                  <p className="text-xs text-gray-500 mt-0.5">
                    ₦200,000 + 20% of gross income (automatically applied by law)
                  </p>
                </label>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 px-6 py-3.5 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 font-semibold shadow-lg shadow-primary-600/25"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Calculating...
                    </>
                  ) : (
                    <>
                      <Calculator className="w-5 h-5" />
                      Calculate Tax
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-4 py-3.5 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-all"
                  title="Reset form"
                >
                  <RefreshCw className="w-5 h-5" />
                </button>
              </div>
            </form>

            {/* Error Display */}
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* Results Panel */}
          <div className="space-y-6">
            {result ? (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
                    <div className="flex items-center gap-2 text-green-700 mb-1">
                      <Wallet className="w-4 h-4" />
                      <span className="text-xs font-medium">Net Income</span>
                    </div>
                    <p className="text-xl font-bold text-green-800">
                      {formatCurrency(result.net_income)}
                    </p>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-red-50 to-rose-50 rounded-xl border border-red-200">
                    <div className="flex items-center gap-2 text-red-700 mb-1">
                      <TrendingDown className="w-4 h-4" />
                      <span className="text-xs font-medium">Annual Tax</span>
                    </div>
                    <p className="text-xl font-bold text-red-800">
                      {formatCurrency(result.tax_due)}
                    </p>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-200">
                    <div className="flex items-center gap-2 text-blue-700 mb-1">
                      <PiggyBank className="w-4 h-4" />
                      <span className="text-xs font-medium">Monthly Tax</span>
                    </div>
                    <p className="text-xl font-bold text-blue-800">
                      {formatCurrency(result.monthly_tax)}
                    </p>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl border border-purple-200">
                    <div className="flex items-center gap-2 text-purple-700 mb-1">
                      <Calculator className="w-4 h-4" />
                      <span className="text-xs font-medium">Effective Rate</span>
                    </div>
                    <p className="text-xl font-bold text-purple-800">
                      {formatPercent(result.effective_rate)}
                    </p>
                  </div>
                </div>

                {/* Detailed Breakdown */}
                <div className="p-6 bg-white rounded-xl border border-gray-200 shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Calculation Breakdown
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Gross Income</span>
                      <span className="font-medium">{formatCurrency(result.gross_income)}</span>
                    </div>
                    {result.consolidated_relief > 0 && (
                      <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-gray-600">Less: Consolidated Relief (CRA)</span>
                        <span className="font-medium text-green-600">
                          -{formatCurrency(result.consolidated_relief)}
                        </span>
                      </div>
                    )}
                    {result.total_allowances > 0 && (
                      <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-gray-600">Less: Allowances</span>
                        <span className="font-medium text-green-600">
                          -{formatCurrency(result.total_allowances)}
                        </span>
                      </div>
                    )}
                    {result.total_reliefs > 0 && (
                      <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-gray-600">Less: Reliefs</span>
                        <span className="font-medium text-green-600">
                          -{formatCurrency(result.total_reliefs)}
                        </span>
                      </div>
                    )}
                    <div className="flex justify-between py-2 border-b-2 border-gray-300">
                      <span className="text-gray-900 font-semibold">Taxable Income</span>
                      <span className="font-bold">{formatCurrency(result.taxable_income)}</span>
                    </div>
                  </div>
                </div>

                {/* Tax Brackets */}
                {result.breakdown && result.breakdown.length > 0 && (
                  <div className="p-6 bg-white rounded-xl border border-gray-200 shadow-sm">
                    <h4 className="font-semibold text-gray-900 mb-4">Tax by Bracket</h4>
                    <div className="space-y-2">
                      {result.breakdown.map((item, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between py-2.5 px-3 bg-gray-50 rounded-lg"
                        >
                          <div>
                            <span className="text-sm font-medium text-gray-900">{item.bracket}</span>
                            <span className="text-xs text-gray-500 ml-2">@ {item.rate}</span>
                          </div>
                          <span className="text-sm font-semibold text-red-600">
                            {formatCurrency(item.tax)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Minimum Tax Notice */}
                {result.minimum_tax_applies && (
                  <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-amber-800 font-medium text-sm">Minimum Tax Applied</p>
                      <p className="text-amber-700 text-xs mt-1">
                        Your calculated tax is below the 1% minimum tax threshold ({formatCurrency(result.minimum_tax_amount)}).
                        The minimum tax amount has been applied.
                      </p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="h-full flex items-center justify-center p-12 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
                <div className="text-center">
                  <Calculator className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 font-medium">Enter your income details</p>
                  <p className="text-gray-400 text-sm mt-1">Results will appear here</p>
                </div>
              </div>
            )}

            {/* Disclaimer */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <p className="text-xs text-blue-800">
                <strong>Disclaimer:</strong> This calculator provides estimates based on the Nigeria Tax Act 2025.
                For official tax filings, please consult a certified tax professional or the Federal Inland Revenue Service (FIRS).
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
