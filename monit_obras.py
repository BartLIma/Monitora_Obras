import pandas as pd
import streamlit as st
import os
import urllib.parse

st.title("🏗️ Monitoramento Estratégico - Pendências de Obras no SISMOB")

# --- CARREGAMENTO DO BANCO DE SECRETÁRIOS (COSEMS/PB) ---
df_sec = pd.DataFrame()
if os.path.exists("secretarios_cosems_pb.csv"):
    for enc in ["utf-8-sig", "latin1", "cp1252"]:
        try:
            df_sec = pd.read_csv("secretarios_cosems_pb.csv", sep=";", dtype=str)
            df_sec.columns = df_sec.columns.str.strip()
            for col in df_sec.columns:
                df_sec[col] = df_sec[col].fillna("").astype(str).str.strip()
            break
        except Exception:
            continue

# --- 🎛️ MENU LATERAL ELEGANTE (POUPA ESPAÇO NA TELA) ---
st.sidebar.header("Painel de Controle de Obras")
tipo_acompanhamento = st.sidebar.radio(
    "Selecione o programa de execução:",
    ["Obras Novo PAC", "Retomada de Obras Paralisadas"]
)
st.sidebar.markdown("---")

obras_filtradas = pd.DataFrame()
muni = ""
uf = "PB"
prop_escolhida = ""
msg_contexto = ""
programa_nome = ""

# =========================================================================
# FLUXO 1: OBRAS NOVO PAC
# =========================================================================
if tipo_acompanhamento == "Obras Novo PAC":
    st.subheader("⚡ Painel de Controle — Novo PAC")
    arquivo_pac = "PB - Lima(PAC_PB).csv"
    
    try:
        df_pac = pd.read_csv(arquivo_pac, sep=";", encoding="utf-8-sig", dtype=str)
    except Exception:
        try:
            df_pac = pd.read_csv(arquivo_pac, sep=";", encoding="latin1", dtype=str)
        except Exception:
            st.error(f"⚠️ Arquivo '{arquivo_pac}' não localizado na pasta do projeto.")
            st.stop()

    df_pac.columns = df_pac.columns.str.strip()
    for col in df_pac.columns:
        df_pac[col] = df_pac[col].fillna("").astype(str).str.strip()

    # Submenu de busca movido estrategicamente para a barra lateral
    metodo_busca = st.sidebar.radio("Filtrar PAC por:", ["Município", "Proposta", "Prioridade de Contato"], key="busca_pac")

    if metodo_busca == "Município":
        busca_muni = st.text_input("Digite o nome do Município:", key="muni_pac")
        if busca_muni.strip():
            obras_filtradas = df_pac[df_pac["Município"].str.lower().str.contains(busca_muni.lower().strip(), na=False)]
    elif metodo_busca == "Proposta":
        busca_prop = st.text_input("Digite o número exato da Proposta:", key="prop_pac")
        if busca_prop.strip():
            obras_filtradas = df_pac[df_pac["Proposta"] == busca_prop.strip()]
    elif metodo_busca == "Prioridade de Contato":
        lista_prioridades = sorted([p for p in df_pac["Prioridade de contato"].unique() if p != ""])
        busca_prio = st.selectbox("Selecione o nível de prioridade emergencial:", lista_prioridades, key="prio_pac_sel")
        if busca_prio:
            obras_filtradas = df_pac[df_pac["Prioridade de contato"] == busca_prio]

    if not obras_filtradas.empty:
        st.info(f"💡 Foram encontradas {len(obras_filtradas)} demandas sob este filtro.")
        opcoes_obras = [f"{row['Proposta']} - {row.get('Nome da unidade', 'Obra')} ({row.get('Município', 'PB')})" for idx, row in obras_filtradas.iterrows()]
        obra_selecionada = st.selectbox("Selecione a obra do PAC para abrir os detalhes:", opcoes_obras, key="sel_pac")
        
        prop_escolhida = obra_selecionada.split(" - ")[0].strip()
        dados_obra = obras_filtradas[obras_filtradas["Proposta"] == prop_escolhida].iloc[0]
        
        muni = dados_obra.get("Município", "").upper()
        uf = dados_obra.get("UF", "PB").upper()
        unidade = dados_obra.get("Nome da unidade", "")
        comp = dados_obra.get("Componente", "")
        sit_sismob = dados_obra.get("Situação no SISMOB", "")
        exec_fisica = dados_obra.get("Execução física (%) SISMOB", "")
        dias_sem_mon = dados_obra.get("Dias sem monitoramento SISMOB", "")
        sit_pac = dados_obra.get("Situação equipe PAC", "")
        prioridade = dados_obra.get("Prioridade de contato", "")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Proposta:** {prop_escolhida} | **UF:** {uf}")
            st.markdown(f"**Município:** {muni}")
            st.markdown(f"**Unidade:** {unidade}")
            st.markdown(f"**Componente:** {comp}")
        with col2:
            st.markdown(f"**Situação SISMOB:** {sit_sismob}")
            st.markdown(f"**Execução Física:** {exec_fisica}%")
            st.markdown(f"**Dias Sem Monit.:** {dias_sem_mon} dias")
            st.markdown(f"**Prioridade de Contato:** `{prioridade}`")

        msg_contexto = f"• Unidade: {unidade}\n• Componente: {comp}\n• Situação SISMOB: {sit_sismob}\n• Execução Física: {exec_fisica}%\n• Dias Sem Monitoramento: {dias_sem_mon}\n• Prioridade: {prioridade}"
        programa_nome = "Obras Novo PAC"

# =========================================================================
# FLUXO 2: RETOMADA DE OBRAS PARALISADAS
# =========================================================================
else:
    st.subheader("🔄 Painel de Controle — Retomada de Obras")
    arquivo_retomada = "PB - Lima(RetomadaObras).csv"
    
    try:
        df_ret = pd.read_csv(arquivo_retomada, sep=";", encoding="utf-8-sig", dtype=str)
    except Exception:
        try:
            df_ret = pd.read_csv(arquivo_retomada, sep=";", encoding="latin1", dtype=str)
        except Exception:
            st.error(f"⚠️ Arquivo '{arquivo_retomada}' não localizado na pasta do projeto.")
            st.stop()

    df_ret.columns = df_ret.columns.str.strip()
    for col in df_ret.columns:
        df_ret[col] = df_ret[col].fillna("").astype(str).str.strip()

    # Submenu de busca movido estrategicamente para a barra lateral
    metodo_busca = st.sidebar.radio("Filtrar Retomada por:", ["Município", "Proposta", "Prioridade de Contato"], key="busca_ret")

    if metodo_busca == "Município":
        busca_muni = st.text_input("Digite o nome do Município:", key="muni_ret")
        if busca_muni.strip():
            obras_filtradas = df_ret[df_ret["Município"].str.lower().str.contains(busca_muni.lower().strip(), na=False)]
    elif metodo_busca == "Proposta":
        busca_prop = st.text_input("Digite o número exato da Proposta:", key="prop_ret")
        if busca_prop.strip():
            obras_filtradas = df_ret[df_ret["Proposta"] == busca_prop.strip()]
    elif metodo_busca == "Prioridade de Contato":
        lista_prioridades = sorted([p for p in df_ret["Prioridade de contato"].unique() if p != ""])
        busca_prio = st.selectbox("Selecione o nível de prioridade emergencial:", lista_prioridades, key="prio_ret_sel")
        if busca_prio:
            obras_filtradas = df_ret[df_ret["Prioridade de contato"] == busca_prio]

    if not obras_filtradas.empty:
        st.info(f"💡 Foram encontradas {len(obras_filtradas)} demandas sob este filtro.")
        opcoes_obras = [f"{row['Proposta']} - {row.get('Nome da unidade', 'Obra')} ({row.get('Município', 'PB')})" for idx, row in obras_filtradas.iterrows()]
        obra_selecionada = st.selectbox("Selecione a obra para detalhar:", opcoes_obras, key="sel_ret")
        
        prop_escolhida = obra_selecionada.split(" - ")[0].strip()
        dados_obra = obras_filtradas[obras_filtradas["Proposta"] == prop_escolhida].iloc[0]
        
        muni = dados_obra.get("Município", "").upper()
        uf = dados_obra.get("UF", "PB").upper()
        unidade = dados_obra.get("Nome da unidade", "")
        comp = dados_obra.get("Componente", "")
        porte = dados_obra.get("Porte", "")
        modalidade = dados_obra.get("Modalidade", "")
        sit_sismob = dados_obra.get("Situação no SISMOB", "")
        exec_fisica = dados_obra.get("Execução física (%) SISMOB", "")
        dias_sem_mon = dados_obra.get("Dias sem monitoramento SISMOB", "")
        prioridade = dados_obra.get("Prioridade de contato", "")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown(f"**Proposta:** {prop_escolhida} | **UF:** {uf}")
            st.markdown(f"**Município:** {muni}")
            st.markdown(f"**Unidade:** {unidade}")
            st.markdown(f"**Componente:** {comp}")
            st.markdown(f"**Porte / Modalidade:** {porte} | {modalidade}")
        with col_r2:
            st.markdown(f"**Situação SISMOB:** {sit_sismob}")
            st.markdown(f"**Execução Física:** {exec_fisica}%")
            st.markdown(f"**Dias Sem Monit.:** {dias_sem_mon} dias")
            st.markdown(f"**Prioridade de Contato:** `{prioridade}`")
        
        msg_contexto = f"• Unidade: {unidade}\n• Componente: {comp}\n• Situação SISMOB: {sit_sismob}\n• Execução Física: {exec_fisica}%\n• Dias Sem Monitoramento: {dias_sem_mon}\n• Prioridade: {prioridade}"
        programa_nome = "Retomada de Obras Paralisadas"
# =========================================================================
# BLOCO INTEGRADO: SECRETÁRIOS (COSEMS/PB) + WHATSAPP (VERSÕES 2, 3 e 4)
# =========================================================================
if not obras_filtradas.empty and muni:
    st.markdown("---")
    st.subheader("📋 Dados de Contato do Gestor Local")

    nome_secretario = "Não localizado no cadastro"
    fone_secretario = ""
    
    if not df_sec.empty:
        # Cria um mapeamento de colunas limpas (sem espaços, minúsculas e sem acentos)
        colunas_limpas = {
            c: c.strip().lower()
            .replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            .replace("ã","a").replace("õ","a").replace("ç","c") 
            for c in df_sec.columns
        }
        
        # Localiza dinamicamente as colunas corretas na planilha de secretários
        col_muni_sec = next((orig for orig, limpa in colunas_limpas.items() if "municip" in limpa), df_sec.columns[0])
        col_nome_sec = next((orig for orig, limpa in colunas_limpas.items() if "nome" in limpa or "secretario" in limpa or "gestor" in limpa), None)
        col_fone_sec = next((orig for orig, limpa in colunas_limpas.items() if "tel" in limpa or "cel" in limpa or "fone" in limpa or "whats" in limpa or "zap" in limpa), None)
        
        # Filtra o secretário correspondente ao município da obra
        filtro_sec = df_sec[df_sec[col_muni_sec].str.lower().str.strip() == muni.lower().strip()]
        
        if not filtro_sec.empty:
            # Captura segura dos dados utilizando a primeira linha encontrada [0]
            nome_secretario = filtro_sec.iloc[0][col_nome_sec] if col_nome_sec else "Coluna de nome não identificada"
            fone_secretario = filtro_sec.iloc[0][col_fone_sec] if col_fone_sec else ""

    st.write(f"**Secretário(a) de Saúde:** {nome_secretario}")
    st.write(f"**WhatsApp/Telefone:** {fone_secretario if fone_secretario else 'Não informado'}")

    saudacao = "Prezado(a) Secretário(a)" if "Não localizado" in nome_secretario else f"Prezado(a) Secretário(a) {nome_secretario}"
    
    mensagem_whatsapp = (
        f"{saudacao},\n\n"
        f"Entramos em contato para verificar a evolução técnica e pendências de engenharia em seu município, vinculadas ao programa de {programa_nome}:\n\n"
        f"📌 *DADOS DO INSTRUMENTO:*\n"
        f"• Município: {muni} - {uf}\n"
        f"• Proposta Nº: {prop_escolhida}\n"
        f"{msg_contexto}\n\n"
        f"Solicitamos atenção especial quanto ao andamento dos trâmites administrativos para a regularização do objeto. "
        f"Permanecemos à disposição para suporte técnico."
    )
    
    st.text_area("Visualização da Mensagem:", value=mensagem_whatsapp, height=220)
    
    # Botão de Ação Rápida WhatsApp
    if fone_secretario:
        num_limpo = "".join(filter(str.isdigit, fone_secretario))
        if len(num_limpo) <= 11 and num_limpo != "":
            num_limpo = f"55{num_limpo}"
            
        texto_url = urllib.parse.quote(mensagem_whatsapp)
        link_api = f"https://whatsapp.com{num_limpo}&text={texto_url}"
        
        st.markdown(f"[📲 Enviar Diretamente via WhatsApp Web]({link_api})")
    
    st.markdown("**Se preferir copiar manualmente, clique no ícone no canto superior direito do bloco abaixo:**")
    st.code(mensagem_whatsapp, language="text")

# Rodapé Técnico do Corecon
# st.markdown("---")
# st.markdown("<p style='text-align:right; font-size:12px; color:gray;'>Bartolomeu Lima - Corecon-ES 1541</p>", unsafe_allow_html=True)
# =========================================================================
# 🗺️ BLOCO EXTRA: MAPEAMENTO GEOGRÁFICO DA PARAÍBA (CORRIGIDO)
# =========================================================================
st.markdown("---")
st.subheader("🗺️ Distribuição Geográfica das Demandas — Paraíba")

# Dicionário Mestre de Coordenadas dos Municípios da Paraíba
coordenadas_pb = {
    "joao pessoa": [-7.1198, -34.8450], "campina grande": [-7.2247, -35.8772],
    "santa rita": [-7.1139, -34.9736], "patos": [-7.0269, -37.2797],
    "guarabira": [-6.8547, -35.4914], "cabedelo": [-6.9811, -34.8339],
    "bayeux": [-7.1253, -34.9322], "sousa": [-6.7611, -38.2250],
    "cajazeiras": [-6.8886, -38.5583], "sape": [-7.0964, -35.2319],
    "mamanguape": [-6.8386, -35.1264], "itabaiana": [-7.3167, -35.3333],
    "pombal": [-6.7725, -37.8014], "catole do rocha": [-6.3439, -37.7456],
    "esperanca": [-7.0253, -35.8578], "monteiro": [-7.8894, -37.1200]
}

dados_mapa = []
df_atual = df_pac if tipo_acompanhamento == "Obras Novo PAC" else df_ret

if not df_atual.empty:
    # Captura a quantidade TOTAL real de obras/linhas filtradas na planilha cheia
    total_obras_geral = len(df_atual)
    
    # Agrupa por município para plotar apenas 1 ponto geográfico por cidade no mapa
    df_municipios_unicos = df_atual.drop_duplicates(subset=["Município"])

    for idx, row in df_municipios_unicos.iterrows():
        muni_bruto = str(row.get("Município", "")).lower().strip()
        muni_limpo = muni_bruto.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("â","a").replace("ê","e").replace("ô","o").replace("ã","a").replace("õ","a").replace("ç","c")
        
        if muni_limpo in coordenadas_pb:
            # SOMA DAS OBRAS: Conta quantas linhas aquele município tem no arquivo completo
            total_obras_muni = len(df_atual[df_atual["Município"].str.lower().str.strip() == muni_bruto])
            
            dados_mapa.append({
                # CORREÇÃO CRÍTICA: Puxa o índice [0] como float para Latitude e [1] para Longitude
                "lat": float(coordenadas_pb[muni_limpo][0]),
                "lon": float(coordenadas_pb[muni_limpo][1]),
                "Município": row.get("Município", "").upper(),
                "Total de Obras": int(total_obras_muni)
            })

    if dados_mapa:
        df_mapa = pd.DataFrame(dados_mapa)
        
        # Mensagem foca no total volumétrico de OBRAS e na quantidade de cidades
        st.success(f"📍 Sucesso! Foram localizadas **{total_obras_geral} obras** ativas, distribuídas entre **{len(df_mapa)} municípios** paraibanos.")
        
        # Renderiza o mapa nativo do Streamlit focado na Paraíba utilizando os números limpos
        st.map(df_mapa, latitude="lat", longitude="lon", zoom=7)
        
        # Exibe a tabela resumo com o totalizador real acumulado por cidade
        with st.expander("📊 Ver relação de municípios mapeados e quantidade de obras"):
            st.dataframe(
                df_mapa[["Município", "Total de Obras"]].sort_values(by="Total de Obras", ascending=False), 
                use_container_width=True,
                index=False
            )
    else:
        st.info("ℹ️ Nenhum município do filtro atual foi localizado no dicionário 'coordenadas_pb'. Verifique a grafia dos nomes.")

