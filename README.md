# 🛒 FoodCommerce AI Dashboard — AI Metric Pulse

> Plataforma analítica executiva de e-commerce com inteligência preditiva, detecção contínua de anomalias, simulador estratégico *What-If* e copiloto de IA analítica generativa. Construída com base no **IBM Carbon Design System**.

---

## 📌 Visão Geral

O **FoodCommerce AI Dashboard (AI Metric Pulse)** é uma aplicação full-stack voltada para diretores e gestores de e-commerce. Integrado à base de dados real do marketplace **Olist** (~100.000 pedidos), o sistema combina telemetria de negócios tradicional com algoritmos de *Machine Learning* e inteligência artificial via LLM.

### Principais Funcionalidades

- **Co-Piloto de IA Executiva (Watsonx Style):** Assistente analítico integrado alimentado por LLM via Groq, capaz de responder perguntas livres sobre o negócio ou executar diagnósticos automáticos em tempo real.
- **Previsão Preditiva de Demanda (Holt-Winters 7D):** Modelo de suavização exponencial tripla com sazonalidade semanal e intervalo de confiança a 95%, com backtesting histórico de acurácia.
- **Detecção Estatística de Anomalias (Z-Score):** Monitoramento contínuo em janela móvel de 28 dias identificando picos incomuns ou quedas bruscas de volume ($\pm 3\sigma$).
- **Simulador de Decisões Estratégicas (*What-If*):** Alavancas interativas de prazo de entrega, parcelamento e subsídio de frete com cálculo de elasticidade e impacto projetado na receita e CSAT.
- **Diagnóstico da Cadeia Logística & Detratores:** Decomposição do lead time (vendedor vs transportadora) e categorização das causas-raiz de clientes insatisfeitos (reviews 1★ e 2★).
- **Exportação & Relatório Executivo Oficial:** Emissão de documento A4/PDF executivo pronto para impressão e exportação de planilha consolidada em CSV UTF-8 com BOM.

---

## 🎨 Design System: IBM Carbon

A interface segue integralmente as diretrizes e tokens do **IBM Carbon Design System** ([carbondesignsystem.com](https://carbondesignsystem.com)):

- **Regra 60-30-10:** 60% neutros de superfície (camadas *Layer 01* e *Layer 02*), 30% secundários estruturais (*Carbon Shell Header* escuro `#161616` e tipografia nítida) e 10% cor de destaque.
- **Cor Primária Única:** *IBM Blue 60* (`#0f62fe` no modo claro e `#4589ff` no modo escuro) para todas as ações e elementos interativos.
- **Cores Semânticas Estritas:** Verde, amarelo e vermelho reservados exclusivamente para status, feedback e alertas estatísticos, nunca como ornamento.
- **Tipografia Oficial:** Famílias **IBM Plex Sans** (numerais e textos de alta legibilidade) e **IBM Plex Mono**.
- **Grade e Espaçamento (Base 8px):** Alinhamento em escala de 8px e container central limitado ao breakpoint oficial do Carbon (*1584px*), evitando distorções em telas ultrawide.
- **Acessibilidade:** Contraste em conformidade com as diretrizes **WCAG AA/AAA** tanto no modo claro quanto no modo escuro.

---

## 🏗️ Arquitetura do Projeto

```
FoodCommerce-AI-Dashboard/
├── backend/
│   ├── data/                   # Datasets públicos do Olist E-commerce (CSV)
│   ├── services/
│   │   ├── ai_service.py       # Integração com Groq LLM (GPT-OSS 120B)
│   │   └── data_service.py     # Pipeline Pandas, Holt-Winters, Z-Score & Métricas
│   ├── app.py                  # API REST Flask com rotas de métricas e health check
│   ├── requirements.txt        # Dependências Python (Flask, Pandas, Gunicorn, Groq)
│   ├── Dockerfile              # Container de produção com Python 3.11 e Gunicorn
│   ├── Procfile                # Comando de deploy para plataformas PaaS
│   └── .env.example            # Modelo de variáveis de ambiente
├── frontend/
│   ├── src/
│   │   ├── components/         # Componentes Vue (KPIs, Gráficos, IA, Simulador, Modal)
│   │   ├── css/
│   │   │   ├── tokens.css      # Design tokens centralizados do IBM Carbon
│   │   │   └── app.css         # Estilização global e resets Carbon
│   │   ├── layouts/
│   │   │   └── MainLayout.vue  # Header corporativo Carbon Shell (48px)
│   │   ├── pages/
│   │   │   └── IndexPage.vue   # Dashboard panorâmico em linhas completas
│   │   ├── api.ts              # Cliente Axios desacoplado com fallback dinâmico
│   │   └── tokens.ts           # Exportador de tokens Carbon para scripts e ApexCharts
│   ├── package.json
│   └── quasar.config.ts        # Configuração do Quasar Framework & Vite
├── start.bat                   # Inicializador rápido para Windows (CMD)
├── start.ps1                   # Inicializador rápido para Windows (PowerShell)
├── .gitignore                  # Regras globais de exclusão do Git
└── README.md
```

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- **Python 3.10+** (recomendado 3.11 ou superior)
- **Node.js 18+** ou **20+** (com npm instalado)
- Chave de API da **Groq** ([console.groq.com](https://console.groq.com))

---

### Opção 1: Inicialização Automática (Windows)

Na raiz do repositório, basta executar um dos scripts:

```cmd
start.bat
```
*ou via PowerShell:*
```powershell
.\start.ps1
```

O script inicializa automaticamente o backend na porta `5000` e o frontend na porta `9000`.

---

### Opção 2: Inicialização Manual Passo a Passo

#### 1. Configurar o Backend (Flask)
```bash
cd backend

# Criar e ativar o ambiente virtual
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/Mac:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar a variável de ambiente
cp .env.example .env
# Edite o arquivo .env e adicione sua chave GROQ_API_KEY:
# GROQ_API_KEY="gsk_..."

# Iniciar o servidor
python app.py
```
O backend estará disponível em `http://localhost:5000` (rota de verificação: `http://localhost:5000/health`).

#### 2. Configurar o Frontend (Vue / Quasar / Vite)
Em um novo terminal:
```bash
cd frontend

# Instalar dependências
npm install

# Iniciar em modo de desenvolvimento
npm run dev
```
O dashboard abrirá automaticamente no navegador em `http://localhost:9000`.

---

## 🌐 Deploy em Servidor Web / Produção

O backend foi preparado e testado com servidor de produção **Gunicorn**, suporte a porta dinâmica (`$PORT`) e checagem de saúde (`/health`).

### Deploy com Docker (Recomendado)
Dentro da pasta `backend`:
```bash
# Construir a imagem
docker build -t foodcommerce-ai-backend .

# Executar o container
docker run -d -p 5000:5000 -e GROQ_API_KEY="sua_chave_aqui" --name backend foodcommerce-ai-backend
```

### Deploy em Plataformas PaaS (Render, Railway, Fly.io, etc.)
1. Aponte o repositório para o serviço web e defina o diretório raiz como `backend`.
2. A plataforma detectará automaticamente o [Dockerfile](file:///c:/Users/loren/OneDrive/Área de Trabalho/ecommerce/FoodCommerce-AI-Dashboard/backend/Dockerfile) ou o [Procfile](file:///c:/Users/loren/OneDrive/Área de Trabalho/ecommerce/FoodCommerce-AI-Dashboard/backend/Procfile).
3. Configure a variável de ambiente no painel do serviço:
   - `GROQ_API_KEY`: sua chave de API Groq.

### Build de Produção do Frontend
Para compilar a Single Page Application (SPA):
```bash
cd frontend
npm run build
```
Os arquivos otimizados e minificados serão gerados em `frontend/dist/spa` e podem ser hospedados em qualquer CDN ou servidor estático (Vercel, Netlify, Cloudflare Pages, Nginx, S3).

> **Configuração da URL da API em produção:**
> Para apontar o frontend para a URL do seu backend na nuvem, defina a variável `API_URL` antes do build:
> ```bash
> API_URL="https://sua-api.onrender.com/api" npm run build
> ```

---

## 📡 Endpoints da API REST

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/health` | Checagem de integridade do serviço (status `healthy`) |
| `GET` | `/api/kpis` | Métricas consolidadas (faturamento, pedidos, prazo, cancelamento, CSAT) |
| `GET` | `/api/charts/orders-by-hour` | Distribuição de pedidos por hora do dia |
| `GET` | `/api/charts/sales-by-month` | Faturamento histórico mensal |
| `GET` | `/api/charts/payments` | Proporção de métodos de pagamento |
| `GET` | `/api/charts/top-states` | Top 10 estados brasileiros por volume |
| `GET` | `/api/charts/top-categories` | Top 10 categorias de produtos por receita |
| `GET` | `/api/charts/delivery-vs-score` | Correlação entre dias de entrega e nota de avaliação |
| `GET` | `/api/charts/anomalies` | Série histórica e detecção de anomalias estatísticas ($\pm 3\sigma$) |
| `GET` | `/api/charts/forecast` | Projeção preditiva dos próximos 30 dias (pedidos ou receita) |
| `GET` | `/api/charts/lead-time` | Funil de lead time por etapa (aprovação, despacho, trânsito) |
| `GET` | `/api/charts/freight-by-region`| Razão percentual de frete sobre o pedido por região do Brasil |
| `GET` | `/api/charts/installments-ticket` | Ticket médio por quantidade de parcelas no cartão |
| `GET` | `/api/charts/reviews-distribution` | Distribuição das notas dos clientes (1 a 5 estrelas) |
| `GET` | `/api/charts/review-topics` | Categorização das causas de insatisfação dos detratores |
| `POST` | `/api/simulate` | Simulação de cenários *What-If* (prazo, parcelamento, frete N/NE) |
| `POST` | `/api/ai-insight` | Consulta analítica generativa com Groq LLM |
| `GET` | `/api/export/csv` | Download do relatório completo de métricas em formato CSV UTF-8 |

---

## 🛠️ Tecnologias Utilizadas

- **Frontend:** [Vue 3](https://vuejs.org/), [Quasar Framework v2](https://quasar.dev/), [Vite](https://vitejs.dev/), [TypeScript](https://www.typescriptlang.org/), [ApexCharts](https://apexcharts.com/), [Axios](https://axios-http.com/).
- **Design System:** [IBM Carbon Design System](https://carbondesignsystem.com/) & [IBM Plex Typography](https://www.ibm.com/plex/).
- **Backend:** [Python 3.11](https://www.python.org/), [Flask](https://flask.palletsprojects.com/), [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [Gunicorn](https://gunicorn.org/).
- **Inteligência Artificial:** [Groq Cloud](https://groq.com/) (LLM `openai/gpt-oss-120b`).
- **DevOps:** [Docker](https://www.docker.com/), Procfile, Shell scripts para Windows/Linux.

---

## 📄 Licença

Este projeto é desenvolvido para fins educacionais, demonstrativos e executivos. Os dados utilizados são provenientes do [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

