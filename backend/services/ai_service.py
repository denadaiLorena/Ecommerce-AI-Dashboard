import os
from groq import Groq

MODEL = "openai/gpt-oss-120b"
_client = None

PRESETS = {
    "delivery_bottlenecks": "Identifique gargalos no tempo de entrega, indicando estados e faixas de prazo mais problemáticos.",
    "cancellation_peak": "Analise o que pode ter causado os picos de cancelamento e sugira hipóteses a validar.",
    "increase_ticket": "Gere recomendações práticas para aumentar o ticket médio.",
    "customer_complaints": "Analise as causas-raiz de reclamações dos clientes (notas 1 e 2 nos reviews) e proponha um plano de ação imediato para reverter a insatisfação.",
}


def _get_client():
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY não configurada no ambiente.")
        _client = Groq(api_key=key)
    return _client


def ask(question: str, summary: str) -> str:
    prompt = f"""Você é um analista de dados sênior de e-commerce.
Responda em português do Brasil usando formatação Markdown rica para facilitar a leitura:

REGRAS DE FORMATAÇÃO OBRIGATÓRIAS:
1. Comece com um título curto em ## (ex: ## Análise de Gargalos de Entrega)
2. Use **negrito** para destacar números, métricas e termos-chave
3. Use listas com bullets (- ou *) para organizar os pontos
4. Quando houver comparação de valores, crie uma tabela Markdown (com |, cabeçalho e separador ---)
5. Use ### para subtítulos que separem seções (ex: ### Diagnóstico, ### Recomendações)
6. Ao final, inclua uma seção ### 💡 Recomendações com ações práticas numeradas (1. 2. 3.)
7. Se houver um destaque crítico, use > (blockquote) para chamar atenção

Use APENAS os números do resumo abaixo. Se faltar dado para responder, diga isso e não invente.

Resumo dos dados (dataset Olist):
{summary}

Pergunta: {question}"""

    completion = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1400,
    )
    return completion.choices[0].message.content
