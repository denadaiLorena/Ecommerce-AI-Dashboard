/**
 * IBM Carbon Design System - Tokens para Scripts / Visualizações de Dados
 * Todos os valores correspondem exatamente às variáveis CSS de tokens.css.
 */

export interface ThemeTokens {
  bg: string
  layer01: string
  layer02: string
  layer03: string
  borderSubtle: string
  borderStrong: string
  borderInteractive: string
  textPrimary: string
  textSecondary: string
  textHelper: string
  textOnColor: string
  primary: string
  primaryHover: string
  primaryLight: string
  primaryDark: string
  success: string
  successBg: string
  warning: string
  warningBg: string
  warningText: string
  danger: string
  dangerBg: string
  info: string
  infoBg: string
  chartGrid: string
  chartText: string
  chartSeries: string[]
  chartConfidence: string
}

export const lightTokens: ThemeTokens = {
  bg: '#f4f4f4',
  layer01: '#ffffff',
  layer02: '#f4f4f4',
  layer03: '#e0e0e0',
  borderSubtle: '#e0e0e0',
  borderStrong: '#8d8d8d',
  borderInteractive: '#0f62fe',
  textPrimary: '#161616',
  textSecondary: '#525252',
  textHelper: '#6f6f6f',
  textOnColor: '#ffffff',
  primary: '#0f62fe',
  primaryHover: '#0353e9',
  primaryLight: '#edf5ff',
  primaryDark: '#001d6c',
  success: '#24a148',
  successBg: '#defbe6',
  warning: '#f1c21b',
  warningBg: '#fdf5d6',
  warningText: '#8a6100',
  danger: '#da1e28',
  dangerBg: '#fff1f1',
  info: '#0043ce',
  infoBg: '#edf5ff',
  chartGrid: '#e0e0e0',
  chartText: '#525252',
  chartSeries: ['#0f62fe', '#0072c3', '#007d79', '#8a3ffc', '#1192e8'],
  chartConfidence: 'rgba(15, 98, 254, 0.15)'
}

export const darkTokens: ThemeTokens = {
  bg: '#161616',
  layer01: '#262626',
  layer02: '#393939',
  layer03: '#525252',
  borderSubtle: '#393939',
  borderStrong: '#6f6f6f',
  borderInteractive: '#4589ff',
  textPrimary: '#f4f4f4',
  textSecondary: '#c6c6c6',
  textHelper: '#8d8d8d',
  textOnColor: '#ffffff',
  primary: '#4589ff',
  primaryHover: '#78a9ff',
  primaryLight: '#002d9c',
  primaryDark: '#001141',
  success: '#42be65',
  successBg: '#044317',
  warning: '#f1c21b',
  warningBg: '#483700',
  warningText: '#f1c21b',
  danger: '#fa4d56',
  dangerBg: '#520408',
  info: '#4589ff',
  infoBg: '#002d9c',
  chartGrid: '#393939',
  chartText: '#c6c6c6',
  chartSeries: ['#4589ff', '#1192e8', '#009d9a', '#be95ff', '#a6c8ff'],
  chartConfidence: 'rgba(69, 137, 255, 0.2)'
}

export function getCarbonTokens(isDark: boolean): ThemeTokens {
  return isDark ? darkTokens : lightTokens
}

