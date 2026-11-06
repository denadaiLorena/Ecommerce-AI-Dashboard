export interface Kpis {
  total_sales: number
  total_orders: number
  avg_delivery_days: number
  cancellation_rate: number
  avg_review_score: number
  late_rate: number
}

export interface HourChart { hours: string[]; series: number[] }
export interface MonthChart { months: string[]; series: number[] }
export interface DeliveryScoreChart { faixas: string[]; series: number[] }
export interface PaymentChart { labels: string[]; series: number[] }
export interface StatesChart { states: string[]; series: number[] }
export interface CategoriesChart { categories: string[]; series: number[] }

export interface AnomalyPoint {
  date: string
  value: number
  expected: number
  z: number
  type: 'pico' | 'queda'
}

export interface AnomalyChartData {
  dates: string[]
  series: number[]
  upper: (number | null)[]
  lower: (number | null)[]
  anomalies: AnomalyPoint[]
}

export interface ForecastChartData {
  history_dates: string[]
  history: number[]
  forecast_dates: string[]
  forecast: number[]
  lower: number[]
  upper: number[]
  horizon_days: number
  total_forecast: number
}

export type PresetKey = 'delivery_bottlenecks' | 'cancellation_peak' | 'increase_ticket'

export type InsightPayload =
  | { preset: PresetKey }
  | { question: string }

export interface InsightResponse { insight: string }