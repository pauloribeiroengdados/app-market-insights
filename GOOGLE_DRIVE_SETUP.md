# 🗂️ Configuração de Google Drive para Market Insights

Este guia explica como configurar a aplicação para carregar dados a partir do Google Drive em vez de arquivos locais.

## ✅ Requisitos

- Python 3.7+
- Bibliotecas instaladas: `gdown` (adicionada automaticamente ao `requirements.txt`)
- Arquivos parquet no Google Drive com permissões de acesso compartilhado

## 🔧 Passo 1: Instalar Dependências

Execute no terminal:

```bash
pip install -r requirements.txt
```

Isto irá instalar `gdown` que é necessário para baixar arquivos do Google Drive.

## 📁 Passo 2: Preparar Arquivos no Google Drive

Você precisará dos seguintes arquivos no Google Drive:

1. **ml_score_reativacao_top5.parquet** - Dados de reativação
2. **ml_score_prospeccao_top5.parquet** - Dados de prospecção
3. **F.K03200$Z.D60214_1.CNAECSV.parquet** - Tabela de referência CNAE
4. **de_para_municipios.parquet** - Tabela de referência de Municípios

### Compartilhar Arquivos no Google Drive

Para cada arquivo:

1. No Google Drive, clique com botão direito no arquivo → **Compartilhar**
2. Configure para "Qualquer pessoa com o link" ou "Organizações/pessoas específicas"
3. Copie o link de compartilhamento
4. Extraia o **ID do arquivo** do link (veja próxima seção)

## 🔑 Passo 3: Obter IDs do Google Drive

### Como encontrar o ID de um arquivo:

#### Opção 1: Pelo link de compartilhamento
- Link: `https://drive.google.com/file/d/1AbC2DeF3GhIjKlMnOpQrStUvWxYz/view?usp=sharing`
- **ID**: `1AbC2DeF3GhIjKlMnOpQrStUvWxYz` (entre `/d/` e `/view`)

#### Opção 2: Pelo link direto
- Link: `https://drive.google.com/open?id=1AbC2DeF3GhIjKlMnOpQrStUvWxYz`
- **ID**: `1AbC2DeF3GhIjKlMnOpQrStUvWxYz` (após `id=`)

#### Opção 3: Manualmente no navegador
1. Abra o arquivo no Google Drive
2. Veja na URL: `drive.google.com/file/d/[ID]/view`
3. Copie o `[ID]`

## ⚙️ Passo 4: Configurar app.py

Abra o arquivo **app.py** e localize a seção `GOOGLE_DRIVE_IDS` (próximo às linhas 112-115):

```python
GOOGLE_DRIVE_IDS = {
    'cnae': '1AbC2DeF3GhIjKlMnOpQrStUvWxYz',           # ID do arquivo CNAE
    'municipios': '2BcD3EfG4HiJkLmNoPqRsTuVwXyZ',     # ID do arquivo de Municípios
    'reativacao': '3CdE4FgH5IjKlMnOpQrStUvWxYzAb',    # ID do arquivo de Reativação
    'prospeccao': '4DeF5GhI6JkLmNoPqRsTuVwXyZAbCd',   # ID do arquivo de Prospecção
}
```

Substitua os valores `'1AbC2DeF3GhIjKlMnOpQrStUvWxYz'` pelos IDs reais de seus arquivos.

**Exemplo completo:**

```python
GOOGLE_DRIVE_IDS = {
    'cnae': '1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1',
    'municipios': '2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2',
    'reativacao': '3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3',
    'prospeccao': '4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d',
}
```

## 🚀 Passo 5: Ativar Google Drive na Aplicação

No arquivo **app.py**, procure pela seção `FONTES DE DADOS` (após linha 300):

```python
usar_demo    = False
usar_gdrive  = True   # ← Altere para True
```

Agora a aplicação carregará dados do Google Drive.

## 🧪 Passo 6: Testar a Configuração

Execute a aplicação:

```bash
streamlit run app.py
```

A aplicação irá:
1. Baixar automaticamente os arquivos do Google Drive na primeira execução
2. Armazenar dados em cache para carregar mais rápido depois
3. Exibir aviso ⚠️ se algum arquivo não puder ser baixado

## 📊 Funcionamento

- **Cache**: Os dados são baixados uma única vez e armazenados em cache
- **Fallback**: Se Google Drive não estiver disponível, a app usa dados locais (se existirem)
- **Demonstração**: Se nenhum dado estiver disponível, usa dados fictícios para demonstração

## ⚠️ Troubleshooting

### Erro: "Erro ao conectar ao Google Drive"

**Soluções:**
1. Verifique se os IDs estão corretos no `GOOGLE_DRIVE_IDS`
2. Confirme que os arquivos estão compartilhados com "Qualquer pessoa com o link"
3. Teste se a URL de compartilhamento está acessível em um navegador
4. Verifique conectividade com a internet

### Erro: "Erro ao ler arquivo"

**Soluções:**
1. Confirme que os arquivos são de fato arquivos `.parquet`
2. Teste o download manual com:
   ```python
   import gdown
   gdown.download("https://drive.google.com/uc?id=SEU_ID", "teste.parquet")
   ```

### Aplicação lenta na primeira execução

Isto é normal! A primeira execução baixa os arquivos do Google Drive. Execuções posteriores usam cache.

## 🔒 Segurança

⚠️ **Atenção**: Não compartilhe links de arquivos contendo dados sensíveis publicamente!

**Recomendações:**
- Use "Acesso restrito" - compartilhe apenas com pessoas/grupos específicos
- Não adicione IDs em repositórios públicos (GitHub, GitLab, etc.)
- Use variáveis de ambiente para IDs sensíveis em produção

## 📝 Modo Híbrido

Você pode usar **ambos** - arquivos locais E Google Drive:

```python
usar_demo    = False
usar_gdrive  = True

# Se usar_gdrive=True:
#   - Tenta carregar do Google Drive primeiro
#   - Se falhar, tenta arquivo local
#   - Se ambos falharem, usa dados de demonstração
```

## 🆘 Suporte

Se encontrar problemas:

1. Consulte a documentação do `gdown`: https://github.com/wkentaro/gdown
2. Teste manualmente os IDs em Python:
   ```python
   import gdown
   import pandas as pd
   
   file_id = "seu_id_aqui"
   url = f"https://drive.google.com/uc?id={file_id}&export=download"
   gdown.download(url, "teste.parquet", quiet=False)
   df = pd.read_parquet("teste.parquet")
   print(df.head())
   ```

---

**Versão**: 1.0 | **Data**: 2026-04-01
